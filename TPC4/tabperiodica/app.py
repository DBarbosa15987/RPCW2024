from flask import Flask, render_template, url_for
import requests
from datetime import datetime

app = Flask(__name__)

# data do sistema em formato ANSI ISO
data_hora_atual = datetime.now()
data_iso_formatada = data_hora_atual.strftime('%Y-%m-%dT%H:%M:%S')

# GraphDB endpoint details
graphdb_endpoint = "http://localhost:7200/repositories/TabPeriodica"

@app.route('/')
def index():
    return render_template('index.html', data = {"data": data_iso_formatada})

@app.route('/elements')
def elements():
    # Send SPARQL query to GraphDB
    sparql_query = """
    prefix tp: <http://www.daml.org/2003/01/periodictable/PeriodicTable#>
    select ?n ?nome ?simb ?group where { 
	?e a tp:Element.
    ?e tp:group ?g.
    optional {?g tp:number ?group.}
    ?e tp:name ?nome.
    ?e tp:symbol ?simb.
    ?e tp:atomicNumber ?n. 
}  
order by ?n
"""
    payload = {"query": sparql_query}

    response = requests.get(graphdb_endpoint, params=payload,
        headers = {'Accept': 'application/sparql-results+json'}
    )
    if response.status_code == 200:
        data = response.json()["results"]["bindings"]
        return render_template('elements.html', data=data)
    else:
        return render_template('empty.html', data=data)


@app.route('/element/<int:na>')
def element(na):
    sparql_query = f"""
prefix tp: <http://www.daml.org/2003/01/periodictable/PeriodicTable#>
select * where {{
	?e a tp:Element .
    ?e tp:name ?nome.
    ?e tp:symbol ?simb.
    ?e tp:atomicNumber {na}.
    ?g a tp:Group.
    ?g tp:element ?e.
    optional{{?g tp:number ?ng.}}
}}
 order by ?n
"""
    payload = {"query": sparql_query}
    response = requests.get(graphdb_endpoint, params=payload,
        headers = {'Accept': 'application/sparql-results+json'}
    )
    if response.status_code == 200:
        data = response.json()["results"]["bindings"]
        return render_template('element.html', data = {
            "data": data_iso_formatada,
            "elem": data[0],
            "na": na
        })
    else:
        return render_template('empty.html', data=data)

@app.route('/groups')
def groups():

    sparql_query = """
    prefix tp: <http://www.daml.org/2003/01/periodictable/PeriodicTable#>
select ?num ?nome where { 
	?g a tp:Group .
    ?g tp:number ?num.
    optional{?g tp:name ?nome.}   
} order by ?num
"""

    payload = {"query": sparql_query}
    response = requests.get(graphdb_endpoint, params=payload,
        headers={'Accept': 'application/sparql-results+json'}
    )

    if response.status_code == 200:
        data = response.json()["results"]["bindings"]
        return render_template('groups.html', data = data)
    else:
        return render_template('empty.html', data=data)

@app.route('/group/<int:ng>')
def group(ng):

    sparql_query = f"""
prefix tp: <http://www.daml.org/2003/01/periodictable/PeriodicTable#>
select * where {{ 
	?g a tp:Group .
    ?g tp:number {ng}.
    optional{{?g tp:name ?nomeG.}}
    ?g tp:element ?elems.
    ?elems tp:name ?nomeE.
    ?elems tp:symbol ?simb.
    ?elems tp:atomicNumber ?na. 

}}
"""
    
    payload = {"query": sparql_query}
    response = requests.get(graphdb_endpoint, params=payload,
        headers = {'Accept': 'application/sparql-results+json'}
    )

    if response.status_code == 200:
        data = response.json()["results"]["bindings"]
        nomeG = f', {data[0]["nomeG"]["value"]}' if "nomeG" in data[0] else ""
        return render_template('group.html', data = {
            "data": data_iso_formatada,
            "ng": ng,
            "elems": data,
            "nomeG": nomeG
        })
    else:
        return render_template('empty.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
