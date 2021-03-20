from flask import render_template, url_for, flash, redirect, request
from HDBResaleWeb import app
from HDBResaleWeb.forms import SearchResaleHDBForm, UpdateResaleHDBForm
from HDBResaleWeb.models import resaleDataGov
from HDBResaleWeb.functions import UpdateResaleData


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = SearchResaleHDBForm()
    if form.validate_on_submit():
        # flash(f'Preparing recommendations for {form.streetname.data}...', 'info')
        return redirect(url_for('result'))
    return render_template('home.html', form=form)

@app.route('/about')
def about():
    return render_template('about.html', title='About Page')

@app.route('/result')
def result():
    return render_template('result.html', title='Result Page')

@app.route('/update/resaledata', methods=['GET', 'POST'])
def update_resaledata():
    form = UpdateResaleHDBForm()
    if (request.method == 'POST') and (form.confirm_update.data == 'Yes'):
        UpdateResaleData()
        flash(f'Updated latest HDB Resale data from data.gov into database.', 'success')
        return redirect(url_for('home'))
    if (request.method == 'POST') and (form.confirm_update.data == 'No'):
        return redirect(url_for('home'))
    return render_template('update_resaledata.html', title='Update HDB Resale Data', form=form)
