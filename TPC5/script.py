import requests
import json
import sys

"""
Queries para responder:
    Que filmes são curtas metragens?
    Que filmes de ação tenho no dataset?
    Qual o elenco do filme X?
    Em que filmes atuou o ator Y?
"""

# Query headers + endpoint + dbLimit
headers = {"Accept": "application/sparql-results+json"}
sparqlEndpoint = "http://dbpedia.org/sparql"
dbpediaLimit = 10000

def getQuery(type,offset=0,film=None,actor=None):

    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

    match type:
        case "films":
            query += f"""
    SELECT *
    WHERE
    {{
    ?film a dbo:Film.
    ?film rdfs:label ?label.
    filter(langMatches(lang(?filmAbstract), "en") && langMatches(lang(?label), "en")).
    ?film dbp:name ?filmName.
    ?film dbo:abstract ?filmAbstract.
    optional{{?film dbo:runtime ?runtime}}
    }} OFFSET {offset}
    LIMIT {dbpediaLimit}
    """
            
        case "directors":
            query += f"""
    SELECT DISTINCT ?director
    WHERE
    {{
        {{<{film}> dbp:director ?director.}} 
        UNION
        {{<{film}> dbo:director ?director.}}
    }}
    """
            
        case "actors":
            query += f"""
    SELECT DISTINCT ?actor
    WHERE
    {{
        {{<{film}> dbp:starring ?actor.}}
        UNION
        {{<{film}> dbo:starring ?actor.}}
    }}
    """
            
        case "actorFilms":
            query += f"""
    SELECT DISTINCT ?film ?name
    WHERE
    {{
        {{?film dbp:starring <{actor}>.}}
        UNION
        {{?film dbo:starring <{actor}>.}}
    }}
"""

        case "actorName":
            query += f"""
    SELECT distinct ?name
    WHERE
    {{
        {{optional  {{<{actor}> dbp:birthName ?name.}}}}
        UNION
        {{optional {{<{actor}> dbp:birthName ?name.}}}}
        UNION
        {{optional {{<{actor}> dbp:name ?name.}}}}

    }}
""" 

    return query


def createFilmsJson():

    offset = 0
    pageSize = dbpediaLimit
    pages = 0
    filmList = []

    # Sai do ciclo quando a "página" da query não vier cheia
    while dbpediaLimit==pageSize:

        query = getQuery(type="films",offset=offset)

        params = {
        "query": query,
        "format": "json"
        }

        response = requests.get(sparqlEndpoint, params=params, headers=headers)

        if response.status_code == 200:
            results = response.json()
            resultList = results["results"]["bindings"]
            pageSize = len(resultList)
            
            
            for result in resultList:
                film_IRI = result["film"]["value"]
                film_name = result["filmName"]["value"]
                film_abstract = result["filmAbstract"]["value"]
                runtime = None
                if "runtime" in result:
                    runtime = result["runtime"]["value"]
                    

                filmList.append({
                    "iri":film_IRI,
                    "nome": film_name,
                    "abstract": film_abstract,
                    "runtime" : runtime
                })

        else:
            print("Error:", response.status_code)
            print(response.text)

        offset += dbpediaLimit
        pages += 1
        print(f"page {pages},pageSize {pageSize}, offset {offset}")

        # FIXME vai ficar assim até ser resolvido, apenas com uma página
        # break



    print(len(filmList))
    outputFile = open("json/films.json", "w") 
    json.dump(filmList, outputFile, ensure_ascii=False)
    outputFile.close()


def completeFilms():

    inputFile = open("json/films.json", "r")
    data = json.load(inputFile)
    fullActorList = set()
    filmList = []
    i = 0

    for film in data:
        i+=1
        print(f"completeFilms {i}")

        newFilm = film

        filmiri = film["iri"]

        queryDirectors = getQuery(type="directors",film=filmiri)
        queryActors = getQuery(type="actors",film=filmiri)

        # Directors
        params = {
            "query": queryDirectors,
            "format": "json"
        }

        directorList = []

        response = requests.get(sparqlEndpoint, params=params, headers=headers)
        if response.status_code == 200:

            results = response.json()
            for result in results["results"]["bindings"]:
                
                actor = None
                if "director" in result:
                    actor = result["director"]
                    if actor["type"] == "uri":
                        directorList.append(actor["value"])
                

        else:
            print("Error in directors:", response.status_code)
            print(response.text)

        newFilm["directors"] = directorList


        # Actors
        params = {
            "query": queryActors,
            "format": "json"
        }


        actorList = []

        response = requests.get(sparqlEndpoint, params=params, headers=headers)
        if response.status_code == 200:

            results = response.json()
            for result in results["results"]["bindings"]:
                
                actor = None
                if "actor" in result:
                    actor = result["actor"]
                    if actor["type"] == "uri":
                        actorList.append(actor["value"])
                        fullActorList.add(actor["value"])
                

        else:
            print("Error in actors:", response.status_code)
            print(response.text)

        newFilm["actors"] = actorList
        
        filmList.append(newFilm)

    outputFile = open("json/updatedFilms.json", "w") 
    json.dump(filmList, outputFile, ensure_ascii=False)
    outputFile.close()

    return list(fullActorList)


def createActorJson(fullActorList):
    
    i = 0

    actorList = []

    for actor in fullActorList:

        print(f"createActorJson {i}")
        i+=1

        actorName = ""

        actorNamequery = getQuery(type="actorName",actor=actor)

        # Actors
        params = {
            "query": actorNamequery,
            "format": "json"
        }

        response = requests.get(sparqlEndpoint, params=params, headers=headers)
        if response.status_code == 200:

            results = response.json()
            if len(results["results"]["bindings"])>0:
                result = results["results"]["bindings"][0]
                if "name" in result:
                    actorName = result["name"]["value"]          

        else:
            print("Error in actorsFilms:", response.status_code)
            print(response.text)


        actorFilmsquery = getQuery(type="actorFilms",actor=actor)

        # Actors
        params = {
            "query": actorFilmsquery,
            "format": "json"
        }


        filmList = []

        response = requests.get(sparqlEndpoint, params=params, headers=headers)
        if response.status_code == 200:

            results = response.json()
            for result in results["results"]["bindings"]:
                
                films = None
                if "film" in result:
                    films = result["film"]
                    if films["type"] == "uri":
                        filmList.append(films["value"])            

        else:
            print("Error in actorFilms:", response.status_code)
            print(response.text)

        actorList.append({
            "uri" : actor,
            "name" : actorName,
            "films" : filmList
        })

    outputFile = open("json/actors.json", "w") 
    json.dump(actorList, outputFile, ensure_ascii=False)
    outputFile.close()



def main():
    createFilmsJson()
    #fullActorList = completeFilms()
    #createActorJson(fullActorList)
    pass


if __name__ == '__main__':
    main()
