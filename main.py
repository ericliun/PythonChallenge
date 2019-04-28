
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/challenge/0')
def zero():
    return render_template('calc.html')

@app.route('/challenge/274877906944')
def map():
    return render_template('map.html')

@app.route('/challenge/cor')
def cor():
    return render_template('cor.html')

if __name__ == '__main__':

    app.run(debug=True)
