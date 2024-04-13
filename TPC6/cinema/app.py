import urllib.parse
from flask import Flask, render_template, url_for
import requests
from rdflib import Graph,URIRef
from datetime import datetime

app = Flask(__name__)
                                
# data do sistema em formato ANSI ISO
data_hora_atual = datetime.now()
data_iso_formatada = data_hora_atual.strftime('%Y-%m-%dT%H:%M:%S')
prefix = "http://rpcw.di.uminho.pt/2024/cinema/"

# GraphDB endpoint details
graphdb_endpoint = "http://localhost:7200/repositories/cinema"
limit = 100


def getUrl(x, page, offset):
    return f"/{x}/{page + offset}"


@app.route('/')
def index():
    return render_template('index.html', data = {"data": data_iso_formatada})


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


@app.route('/actors/', defaults={'page': 1})
@app.route('/actors/<int:page>')
def actors(page):

    return getPersonsPage("actors",page)


@app.route('/actor/<string:uri>')
def actor(uri):

    return getPersonPage("actors",uri)


@app.route('/directors/', defaults={'page': 1})
@app.route('/directors/<int:page>')
def directors(page):

    return getPersonsPage("directors",page)

@app.route('/director/<string:uri>')
def director(uri):

    return getPersonPage("directors",uri)



@app.route('/musicComposers/', defaults={'page': 1})
@app.route('/musicComposers/<int:page>')
def musicComposers(page):

    return getPersonsPage("musicComposers",page)

@app.route('/musicComposer/<string:uri>')
def musicComposer(uri):

    return getPersonPage("musicComposers",uri)



@app.route('/producers/', defaults={'page': 1})
@app.route('/producers/<int:page>')
def producers(page):

    return getPersonsPage("producers",page)


@app.route('/producer/<string:uri>')
def producer(uri):

    return getPersonPage("producers",uri)


@app.route('/writers/', defaults={'page': 1})
@app.route('/writers/<int:page>')
def writers(page):

    return getPersonsPage("writers",page)


@app.route('/writer/<string:uri>')
def writer(uri):

    return getPersonPage("writers",uri)


def getPersonsPage(personType,page):

    variable = ""
    html = ""
    type = ""

    match personType:

        case "actors":
            variable = "actor"
            type = "Actor"
            html = "actors"

        case "directors":
            variable = "director"
            type = "Director"
            html = "directors"
        case "musicComposers":
            variable = "musicComposer"
            type = "MusicComposer"
            html = "musicComposers"
        case "producers":
            variable = "producer"
            type = "Producer"
            html = "producers"
            
        case "writers":
            variable = "writer"
            type = "Writer"
            html = "writers"


    sparqlQuery = f"""

PREFIX : <{prefix}>

select ?{variable} ?birthDate ?name ?description where{{
    ?{variable} a :{type}.
    optional{{?{variable} :name ?name.}}
    optional{{?{variable} :birthDate ?birthDate.}}
    optional{{?{variable} :description ?description.}}
}}limit {limit}
offset {limit*(page-1)}
"""

    payload = {"query": sparqlQuery}

    response = requests.get(graphdb_endpoint, params=payload,
        headers = {'Accept': 'application/sparql-results+json'}
    )
    if response.status_code == 200:
        data = response.json()["results"]["bindings"]
        
        if len(data)>0:
            for i,entry in enumerate(data):
                data[i]["uri"] = entry[variable]["value"].split("/")[-1]
            template = render_template(f'{html}.html', data={
                html: data,
                "page": page
                },getUrl=getUrl)
        else:
            template = render_template("empty.html")
        return template
    else:
        return render_template('empty.html')


def getPersonPage(personType,uri):
    
    variable = ""
    type = ""
    property = ""

    match personType:

        case "actors":
            variable = "actor"
            type = "Actor"
            property = "acted"

        case "directors":
            variable = "director"
            type = "Director"
            property = "directed"

        case "musicComposers":
            variable = "musicComposer"
            type = "MusicComposer"
            property = "composed"

        case "producers":
            variable = "producer"
            type = "Producer"
            property = "produced"
            
        case "writers":
            variable = "writer"
            type = "Writer"
            property = "wrote"


    if '"' in uri:
        uri = urllib.parse.quote(uri, safe='')

    fullUri = URIRef(f"{prefix}{uri}")

    sparqlQuery = f"""

PREFIX : <{prefix}>

select * where{{
    
    <{fullUri}> a :{type}.
    {{
        BIND("http://dbpedia.org/resource/{uri}" AS ?source)
        optional{{<{fullUri}> :name ?name.}}
        optional{{<{fullUri}> :birthDate ?birthDate.}}
        optional{{<{fullUri}> :description ?description.}}
    }}
    union {{ 
        select * where{{
            <{fullUri}> :{property} ?filmUri.
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
        if len(data)>0:
            base = data[0]
            films = data[1:]
            for i,entry in enumerate(films):
                films[i]["filmUri"] = entry["filmUri"]["value"].split("/")[-1]
            template = render_template(f'{variable}.html', data={
            "base" : base,
            "films": films,
            "source": "http://dbpedia.org/resource/"
            })

        else:
            template = render_template("empty.html",data={"response": f'Empty response, {type} {uri} not found'})

        return template

    else:
        return render_template('empty.html',data={"response": response})



if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
