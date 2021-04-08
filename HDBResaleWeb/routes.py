from flask import render_template, url_for, flash, redirect, request
from HDBResaleWeb import app
from HDBResaleWeb.forms import SearchResaleHDBForm, UpdateDataGovForm, UpdatePropGuruForm
from HDBResaleWeb.models import DataGovTable, PropGuruTable, RailTransitTable, ShoppingMallsTable, HawkerCentreTable, SuperMarketTable
from HDBResaleWeb.functions import update_datagov_table, update_propguru_table, insert_railtransit_data, insert_shoppingmalls_data, insert_hawkercentre_data, insert_supermarket_data

######################################################################################################
#Homepage URL
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = SearchResaleHDBForm()
    if form.validate_on_submit():
        # Function to predict estimated price (Prediction model)
        # Function to get closest match (Recommender)
        # flash(f'Preparing recommendations for {form.streetname.data}...', 'info')
        return redirect(url_for('result'))
    return render_template('home.html', form=form)

@app.route('/about')
def about():
    return render_template('about.html', title='About Page')

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
        update_datagov_table()
        #Train Model
        flash(f'Updated latest HDB Resale data from data.gov into database.', 'success')
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
        update_propguru_table()
        flash(f'Updated latest Propertyguru data into database.', 'success')
        return redirect(url_for('home'))
    if (request.method == 'POST') and (form.confirm_update2.data == 'No'):
        return redirect(url_for('home'))
    return render_template('update_propguru_table.html', title='Update HDB Resale Propertyguru Table', form=form)

#Update amenities tables
@app.route('/update/amenities')
def update_amenities():
    insert_railtransit_data()
    insert_shoppingmalls_data()
    insert_hawkercentre_data()
    insert_supermarket_data()
    return redirect(url_for('home'))