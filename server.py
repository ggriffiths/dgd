#!flask/bin/python
from flask import Flask, render_template, request
import miner

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getResults', methods=['POST'])
def update():
	term = request.form['searchTerm']
	return "Search term: " + str(term) + "<br><br>" +miner.main(term)

if __name__ == '__main__':
    app.run(debug=True)