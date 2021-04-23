from flask import render_template, url_for, flash, redirect, request
from HDBResaleWeb import app
from HDBResaleWeb.forms import SearchResaleHDBForm, UpdateDataGovForm, UpdatePropGuruForm, UpdateModelForm
from HDBResaleWeb.functions import update_datagov_table, insert_railtransit_data, insert_shoppingmalls_data, insert_hawkercentre_data, insert_supermarket_data, train_regression_model, load_regression_model
from HDBResaleWeb.PropertyGuruRetriever import scrapeType, scrapeSearchListing, addfeaturesPG
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
        # search_url = 'https://www.propertyguru.com.sg/listing/hdb-for-sale-520a-tampines-central-8-23459129'
        search_df = scrapeSearchListing(search_url)
        # Function to predict estimated price (Prediction model)
        L1, L4, L7, L10, L13, df_recommendation = load_regression_model(search_df)
        listed_price = search_df.get('Price')
        price_array = [listed_price,L1,L4,L7,L10,L13]
        #Get the index of the maximum values and minimum values
        max_index = [i for i, x in enumerate(price_array) if x == max(price_array)]
        min_index = [i for i, x in enumerate(price_array) if x == min(price_array)]
        font_color = ['text-dark','text-dark','text-dark','text-dark','text-dark','text-dark']
        #Change font colour of maximum price to red and minimum price to green
        for x in max_index: font_color[x] = 'text-danger'
        for x in min_index: font_color[x] = 'text-success'
        # Customer recommender system to provide other recommended listings to user
        df_best_match_test, df_cheaper_price_test, df_bigger_house_test = recommender_system(df_recommendation)
        print(df_best_match_test)
        print(df_cheaper_price_test)
        print(df_bigger_house_test)
        df_best_match = ['Item 1','Item 2','Item 3']
        df_cheaper_price = ['Item 1','Item 2','Item 3']
        df_bigger_house = ['Item 1','Item 2','Item 3']
        return render_template('result.html', search_df=search_df, search_url=search_url,price_array=price_array,
        font_color=font_color,df_best_match=df_best_match,df_cheaper_price=df_cheaper_price,df_bigger_house=df_bigger_house)
    return render_template('home.html', form=form)

#Result URL
@app.route('/result')
def result():
    return render_template('result.html', title='Result Page')

######################################################################################################
#Update data gov table
@app.route('/update/datagov', methods=['GET', 'POST'])
def update_datagov():
    form = UpdateDataGovForm()
    if (request.method == 'POST') and (form.confirm_update1.data == 'Yes'):
        #Update database with latest data from datagov
        message = update_datagov_table()
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
@app.route('/update/amenities')
def update_amenities():
    insert_railtransit_data()
    insert_shoppingmalls_data()
    insert_hawkercentre_data()
    insert_supermarket_data()
    return redirect(url_for('home'))
