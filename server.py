#!flask/bin/python
from flask import Flask, render_template, request
import miner
import urllib2
import goslate

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/showResults', methods=['POST','GET','HEAD'])
def update():
	# Get user input
	term = request.form['searchTerm']
	language = request.form['language']
	
	# Translate term
	gs = goslate.Goslate()
	translatedTerm = gs.translate(term,language)

	# Get results
	results = miner.main(term)
	tresults = miner.main(translatedTerm)

	# Get long form of language
	lang_long = gs.get_languages()[language]

	return render_template('results.html', term=term, results=results, language=lang_long, translated_results=tresults, translated_term=translatedTerm)

if __name__ == '__main__':
    app.run(debug=True)
