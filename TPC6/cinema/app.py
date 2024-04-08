import urllib.parse
from flask import Flask, render_template, url_for
import requests
from rdflib import Graph
from datetime import datetime

app = Flask(__name__)
# g = Graph()
# print("parsing...")
# g.parse("../ontology/cinemaOriginalEx.ttl")
# print("done")

# query = "select distinct ?Concept where {[] a ?Concept}"

# response = g.query(query)
# for row in response:
#     print(row)

                                
# data do sistema em formato ANSI ISO
data_hora_atual = datetime.now()
data_iso_formatada = data_hora_atual.strftime('%Y-%m-%dT%H:%M:%S')
prefix = "http://rpcw.di.uminho.pt/2024/cinema/"

# GraphDB endpoint details
graphdb_endpoint = "http://localhost:7200/repositories/cinema"
limit = 100


def getUrl(x, page, offset):
    url = ""

    if x == "films":
        url = f"/films/{page + offset}"
    elif x == "actors":
        url = f"/actors/{page + offset}"
    return url


@app.route('/')
def index():
    return render_template('index.html', data = {"data": data_iso_formatada})
# select ?birthDate ?name ?description ?films where{
#     {optional{:4_Poofs_and_a_Piano :name ?name.}
#     optional{:4_Poofs_and_a_Piano :birthDate ?birthDate.}
#     optional{:4_Poofs_and_a_Piano :description ?description.}}
#     union {:4_Poofs_and_a_Piano :acted ?films}
# }limit 500
# <http://dbpedia.org/resource/Phantasm_II>
# Jim_Varney>
#sparqlQuery: PREFIX : <http://rpcw.di.uminho.pt/2024/cinema/> 
#select * where{
#<http://rpcw.di.uminho.pt/2024/cinema/"Good_Hair"_and_Other_Dubious_Distinctions> a :Film.
#}
@app.route('/films/', defaults={'page': 1})
@app.route('/films/<int:page>')
def films(page):

    sparqlQuery = f"""

    PREFIX : <{prefix}>

select distinct * where{{
    ?film a :Film.
    ?film :title ?title.
    optional{{?film :releaseDate ?releaseDate.}}
    optional{{?film :description ?description.}}
    optional{{?film :duration ?duration.}}
}}limit {limit}
offset {limit*(page-1)}
"""

    payload = {"query": sparqlQuery}

    response = requests.get(graphdb_endpoint, params=payload,
        headers = {'Accept': 'application/sparql-results+json'}
    )
    if response.status_code == 200:
        data = response.json()["results"]["bindings"]
        for i,entry in enumerate(data):
            data[i]["uri"] = entry["film"]["value"].split("/")[-1]
        return render_template('films.html', data={
            "films": data,
            "page": page
            },getUrl=getUrl)
    else:
        return render_template('empty.html')


@app.route('/actors/', defaults={'page': 1})
@app.route('/actors/<int:page>')
def actors(page):

    sparqlQuery = f"""

PREFIX : <{prefix}>

select ?actor ?birthDate ?name ?description where{{
    ?actor a :Actor.
    optional{{?actor :name ?name.}}
    optional{{?actor :birthDate ?birthDate.}}
    optional{{?actor :description ?description.}}
}}limit {limit}
offset {limit*(page-1)}
"""

    payload = {"query": sparqlQuery}

    response = requests.get(graphdb_endpoint, params=payload,
        headers = {'Accept': 'application/sparql-results+json'}
    )
    if response.status_code == 200:
        data = response.json()["results"]["bindings"]
        for i,entry in enumerate(data):
            data[i]["uri"] = entry["actor"]["value"].split("/")[-1]
        return render_template('actors.html', data={
            "actors": data,
            "page": page
            },getUrl=getUrl)
    else:
        return render_template('empty.html')


@app.route('/actor/<string:uri>')
def actor(uri):

    if '"' in uri:
        uri = urllib.parse.quote(uri, safe='')

    sparqlQuery = f"""

PREFIX : <{prefix}>

select * where{{
    
    <{prefix+uri}> a :Actor.
    {{
        BIND("http://dbpedia.org/resource/{uri}" AS ?source)
        optional{{<{prefix+uri}> :name ?name.}}
        optional{{<{prefix+uri}> :birthDate ?birthDate.}}
        optional{{<{prefix+uri}> :description ?description.}}
    }}
    union {{ 
        select * where{{
            <{prefix+uri}> :acted ?filmUri.
            optional{{?filmUri :title ?title.}}
            optional{{?filmUri :description ?filmDescription.}}
            optional{{?filmUri :duration ?duration.}}
            optional{{?filmUri :releaseDate ?releaseDate.}}
        }}
    }}
}}

"""

    payload = {"query": sparqlQuery}

    response = requests.get(graphdb_endpoint, params=payload,
        headers = {'Accept': 'application/sparql-results+json'}
    )
    if response.status_code == 200:
        data = response.json()["results"]["bindings"]
        base = data[0]
        films = data[1:]
        for i,entry in enumerate(films):
            films[i]["filmUri"] = entry["filmUri"]["value"].split("/")[-1]


        return render_template('actor.html', data={
            "base" : base,
            "films": films,
            "source": "http://dbpedia.org/resource/"
            })
    else:
        return render_template('empty.html')


@app.route('/film/<string:uri>')
def film(uri):

    if '"' in uri:
        uri = urllib.parse.quote(uri, safe='')
    
    sparqlQuery = f"""

PREFIX : <{prefix}>

select * where{{
    <{prefix+uri}> a :Film.
    {{
    BIND("http://dbpedia.org/resource/{uri}" AS ?source)
    optional{{<{prefix+uri}> :title ?title.}}
    optional{{<{prefix+uri}> :birthDate ?releaseDate.}}
    optional{{<{prefix+uri}> :description ?filmDescription.}}
    }}
    union {{
        select * where{{
            <{prefix+uri}> :hasActor ?personUri.
            BIND("Actors" AS ?type).
            optional{{?personUri :name ?name.}}
            optional{{?personUri :description ?description.}}
            optional{{?personUri :birthDate ?birthDate.}}
        }}
    }}
    union {{
        select * where{{
            <{prefix+uri}> :hasDirector ?personUri.
            BIND("Directors" AS ?type).
            optional{{?personUri :name ?name.}}
            optional{{?personUri :description ?description.}}
            optional{{?personUri :birthDate ?birthDate.}}
        }}
    }}
    union {{
        select * where{{
            <{prefix+uri}> :hasComposer ?personUri.
            BIND("Composers" AS ?type).
            optional{{?personUri :name ?name.}}
            optional{{?personUri :description ?description.}}
            optional{{?personUri :birthDate ?birthDate.}}
        }}
    }}
    union {{
        select * where{{
            <{prefix+uri}> :hasProducer ?personUri.
            BIND("Producers" AS ?type).
            optional{{?personUri :name ?name.}}
            optional{{?personUri :description ?description.}}
            optional{{?personUri :birthDate ?birthDate.}}
        }}
    }}
    union {{
        select * where{{
            <{prefix+uri}> :hasWriter ?personUri.
            BIND("Writers" AS ?type).
            optional{{?personUri :name ?name.}}
            optional{{?personUri :description ?description.}}
            optional{{?personUri :birthDate ?birthDate.}}
        }}
    }}
}}
"""

    payload = {"query": sparqlQuery}

    response = requests.get(graphdb_endpoint, params=payload,
        headers = {'Accept': 'application/sparql-results+json'}
    )
    if response.status_code == 200:
        data = response.json()["results"]["bindings"]
        cleanData = {}
        cleanData["base"] = data[0]
        cleanData["people"] = {}
        cleanData["source"] = "http://dbpedia.org/resource/"
        for entry in data[1:]:
            type = entry["type"]["value"]
            entry["personUri"]["value"] = entry["personUri"]["value"].split("/")[-1]
            if type in cleanData["people"]:
                cleanData["people"][type].append(entry)
            else:
                cleanData["people"][type] = [entry]
        return render_template('film.html', data=cleanData)
    else:
        return render_template('empty.html',data={"response" :response,"sparqlQuery" :sparqlQuery})



if __name__ == '__main__':
    app.run(debug=True)
