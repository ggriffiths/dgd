#!flask/bin/python
from flask import Flask, render_template, request
import miner

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/updateResults', methods=['POST'])
def update():
	term = request.form['searchTerm']
	return miner.main("Test")

if __name__ == '__main__':
    app.run(debug=True)