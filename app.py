from flask import Flask, render_template, url_for
from forms import SearchResaleHDBForm
app = Flask(__name__)

app.config['SECRET_KEY'] = 'e7d0eaa8168231567e93d4eea521188dbb83b37ccaf576190862a4a2c0c66d80'

@app.route('/')
@app.route('/home')
def home():
    form = SearchResaleHDBForm()
    return render_template('home.html', form=form)

@app.route('/about')
def about():
    return render_template('about.html', title='About Page')



if __name__ == '__main__':
    app.run(debug=True)