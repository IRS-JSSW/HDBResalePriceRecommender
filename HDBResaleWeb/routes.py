from flask import render_template, url_for, flash, redirect, request
from HDBResaleWeb import app
from HDBResaleWeb.forms import SearchResaleHDBForm, UpdateDataGovForm, UpdatePropGuruForm, UpdateModelForm, UpdateAmenitiesForm
from HDBResaleWeb.functions import update_datagov_table, insert_railtransit_data, insert_shoppingmalls_data, insert_hawkercentre_data, insert_supermarket_data, train_regression_model, load_regression_model, get_history_transactions
from HDBResaleWeb.PropertyGuruRetriever import scrapeType, scrapeSearchListing
from HDBResaleWeb.recommendation import recommender_system


######################################################################################################
#Homepage URL
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = SearchResaleHDBForm()
    if form.validate_on_submit():
        #Function to scrape search
        search_url = form.streetname.data
        search_df = scrapeSearchListing(search_url)
        #If search_df is empty
        if (len(search_df)==0):
            flash(f'There is an error with the Propertyguru URL provided, please provide a valid Propertyguru URL.', 'danger')
            return redirect(url_for('home'))
        #If search_df contains valid user input
        if (len(search_df)>0):
            #Function to predict estimated price (Prediction model)
            L1, L4, L7, L10, L13, df_user_input = load_regression_model(search_df)
            listed_price = search_df.get('Price')
            price_array = [listed_price,L1,L4,L7,L10,L13]
            #Get the index of the maximum values and minimum values
            max_index = [i for i, x in enumerate(price_array) if x == max(price_array)]
            min_index = [i for i, x in enumerate(price_array) if x == min(price_array)]
            font_color = ['text-dark','text-dark','text-dark','text-dark','text-dark','text-dark']
            #Change font colour of maximum price to red and minimum price to green
            for x in max_index: font_color[x] = 'text-danger'
            for x in min_index: font_color[x] = 'text-success'
            #Historical transactions for same HDB
            postal_code = df_user_input['postal_code'][0]
            df_history = get_history_transactions(postal_code)
            #Customer recommender system to provide other recommended listings to user
            df_best_match, df_cheaper_price, df_bigger_house = recommender_system(df_user_input)
            return render_template('result.html', search_df=search_df, search_url=search_url,price_array=price_array,
            font_color=font_color,df_best_match=df_best_match,df_cheaper_price=df_cheaper_price,df_bigger_house=df_bigger_house,
            df_history=df_history)
    return render_template('home.html', form=form)


######################################################################################################
#Update data gov table
@app.route('/update/datagov', methods=['GET', 'POST'])
def update_datagov():
    form = UpdateDataGovForm()
    if (request.method == 'POST') and (form.confirm_update1.data == 'Yes'):
        #Update database with latest data from datagov
        message = update_datagov_table()
        if (message == "empty"): flash(f'There are no new records to be updated into the database.', 'info')
        if (message == "success"): flash(f'Updated latest HDB Resale data from data.gov into database.', 'success')
        if (message == "error"): flash(f'Database is not updated. There is a problem accessing HDB Resale data api. Please try again later.', 'danger')
        return redirect(url_for('home'))
    if (request.method == 'POST') and (form.confirm_update1.data == 'No'):
        return redirect(url_for('home'))
    return render_template('update_datagov_table.html', title='Update HDB Resale Data Gov Table', form=form)

#Update property guru table
@app.route('/update/propguru', methods=['GET', 'POST'])
def update_propguru():
    form = UpdatePropGuruForm()
    if (request.method == 'POST') and (form.confirm_update2.data == 'Yes'):
        #Update database with latest data from propguru
        scrapeType()
        flash(f'Updated latest Propertyguru data into database.', 'success')
        return redirect(url_for('home'))
    if (request.method == 'POST') and (form.confirm_update2.data == 'No'):
        return redirect(url_for('home'))
    return render_template('update_propguru_table.html', title='Update HDB Resale Propertyguru Table', form=form)

#Update property guru table
@app.route('/update/trainmodel', methods=['GET', 'POST'])
def train_model():
    form = UpdateModelForm()
    if (request.method == 'POST') and (form.confirm_update3.data == 'Yes'):
        #Train regression model
        train_regression_model()
        flash(f'Trained regression model.', 'success')
        return redirect(url_for('home'))
    if (request.method == 'POST') and (form.confirm_update3.data == 'No'):
        return redirect(url_for('home'))
    return render_template('update_model.html', title='Train Regression Model', form=form)

#Update amenities tables
@app.route('/update/amenities', methods=['GET', 'POST'])
def update_amenities():
    form = UpdateAmenitiesForm()
    if (request.method == 'POST') and (form.confirm_update4.data == 'Yes'):
        #Update database with amenities data
        insert_railtransit_data()
        insert_shoppingmalls_data()
        insert_hawkercentre_data()
        insert_supermarket_data()
        flash(f'Updated amenities tables in database.', 'success')
        return redirect(url_for('home'))
    if (request.method == 'POST') and (form.confirm_update4.data == 'No'):
        return redirect(url_for('home'))
    return render_template('update_amenities_table.html', title='Update Amenities Tables', form=form)
