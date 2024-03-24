from concurrent.futures import ThreadPoolExecutor
import requests
import json
import threading

# Query headers + endpoint + dbLimit
headers = {"Accept": "application/sparql-results+json"}
sparqlEndpoint = "http://dbpedia.org/sparql"
dbpediaLimit = 10000

# Lock for appending json output files
wLock = threading.Lock()

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
    ?film dbp:name ?filmName.
    ?film dbo:abstract ?filmAbstract.
    filter(langMatches(lang(?filmAbstract), "en") && langMatches(lang(?label), "en")).
    optional{{?film dbo:runtime ?runtime}}
    }} OFFSET {offset}
    LIMIT {dbpediaLimit}
    """
                    
        case "updateFilms":
            query += f"""
    SELECT ?actor ?director ?musicComposer ?producer ?writer ?cinematographer WHERE {{
    {{ SELECT DISTINCT ?director WHERE {{
        <{film}> dbo:director ?director.
        FILTER(isURI(?director))
        }}
    }}
    UNION
    {{ SELECT DISTINCT ?actor WHERE {{
        <{film}> dbo:starring ?actor.
        FILTER(isURI(?actor))
        }}
    }}
    UNION
    {{ SELECT DISTINCT ?musicComposer WHERE {{
        <{film}> dbo:musicComposer ?musicComposer.
        FILTER(isURI(?musicComposer))
        }}
    }}
    UNION
    {{ SELECT DISTINCT ?producer WHERE {{
        <{film}> dbo:producer ?producer.
        FILTER(isURI(?producer))
        }}
    }}
    UNION
    {{ SELECT DISTINCT ?writer WHERE {{
        <{film}> dbo:writer ?writer.
        FILTER(isURI(?writer))
        }}
    }}
    UNION
    {{ SELECT DISTINCT ?cinematographer WHERE {{
        <{film}> dbo:cinematography ?cinematographer.
        FILTER(isURI(?cinematographer))
        }}
    }}
}}
"""

        case "actors":
            query += f"""
    SELECT ?role ?name ?description ?birthDate WHERE {{
    {{
        SELECT ?name WHERE {{
            {{<{actor}> dbo:birthName ?name.}}
            UNION
            {{<{actor}> dbp:birthName ?name.}}
            UNION
            {{<{actor}> dbp:name ?name.}}
            UNION
            {{<{actor}> rdfs:label ?name.}}
        }} LIMIT 1
    }}
    UNION
    {{
        SELECT DISTINCT ?role WHERE {{
            ?role dbo:starring <{actor}>.
            FILTER(isURI(?role))
        }}
    }}
    UNION
    {{
        SELECT ?description WHERE {{
            <{actor}> dbo:abstract ?description.
            filter(langMatches(lang(?description), "en"))
        }}
    }}
    UNION
    {{
        SELECT ?birthDate WHERE {{
            <http://dbpedia.org/resource/Sandalu_Thalen_Eha> dbo:birthDate ?birthDate.
        }}
    }}
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
                film_name = result["label"]["value"]
                film_abstract = result["filmAbstract"]["value"]
                runtime = None
                if "runtime" in result:
                    runtime = result["runtime"]["value"]
                    

                filmList.append({
                    "iri": film_IRI,
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

    print(len(filmList))
    outputFile = open("json/films.json", "w") 
    json.dump(filmList, outputFile, ensure_ascii=False,indent=4)
    outputFile.close()


def completeFilms():
    inputFile = open("json/films.json", "r")
    data = json.load(inputFile)
    inputFile.close()

    fullActorSet = set()
    filmList = []
    
    i = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for film in data:
            filmiri = film["iri"]
            future = executor.submit(process_film, filmiri, fullActorSet, filmList,film,i)
            futures.append(future)
            i+=1
        for future in futures:
            future.result()

    outputFile = open("json/updatedFilms.json", "w")
    json.dump(filmList, outputFile, ensure_ascii=False,indent=4)
    outputFile.close()

    fullActorList = list(fullActorSet)
    outputFile = open("json/actorList.json", "w")
    json.dump(fullActorList, outputFile, ensure_ascii=False,indent=4)
    outputFile.close()


def process_film(filmiri, fullActorSet, filmList,film,i):

    query = getQuery(type="updateFilms", film=filmiri)
    params = {"query": query, "format": "json"}
    response = requests.get(sparqlEndpoint, params=params, headers=headers)

    actors = []
    directors = []
    musicComposers = []
    producers = []
    writers = []
    cinematographers = []


    if response.status_code == 200:
        
        results = response.json()
        for result in results["results"]["bindings"]:
            actor = result.get("actor")
            director = result.get("director")
            musicComposer = result.get("musicComposer")
            producer = result.get("producer")
            writer = result.get("writer")
            cinematographer = result.get("cinematographer")
            
            if actor:
                actors.append(actor["value"])
            if director:
                directors.append(director["value"])
            if musicComposer:
                musicComposers.append(musicComposer["value"])
            if producer:
                producers.append(producer["value"])
            if writer:
                writers.append(writer["value"])
            if cinematographer:
                cinematographers.append(cinematographer["value"])
            
    newfilm = film

    newfilm["iri"] = filmiri
    newfilm["actors"] = actors
    newfilm["directors"] = directors
    newfilm["musicComposers"] = musicComposers
    newfilm["producers"] = producers
    newfilm["writers"] = writers
    newfilm["cinematographers"] = cinematographers

    with wLock:
        filmList.append(newfilm)
        for actor in actors:
            fullActorSet.add(actor)

    print(f"Finish thread {i}")


def createActorJson():
    
    inputFile = open("json/actorList.json", "r")
    data = json.load(inputFile)
    inputFile.close()

    i = 0
    actorList = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for actorIri in data:
            future = executor.submit(process_actor, actorIri, actorList,i)
            futures.append(future)
            i+=1
        for future in futures:
            future.result()


    outputFile = open("json/actors.json", "w")
    json.dump(actorList, outputFile, ensure_ascii=False,indent=4)
    outputFile.close()


def process_actor(actorIri, actorList,i):

    query = getQuery(type="actors",actor=actorIri)
    params = {"query": query, "format": "json"}
    response = requests.get(sparqlEndpoint, params=params, headers=headers)

    finalName = ""
    roles = []
    finalDescription = ""

    if response.status_code == 200:
        
        results = response.json()
        for result in results["results"]["bindings"]:
            name = result.get("name")
            role = result.get("role")
            description = result.get("description")
            
            if name:
                finalName = name["value"]
            if role:
                roles.append(role["value"])
            if description:
                finalDescription = description["value"]

    actor = {}
    actor["iri"] = actorIri
    actor["name"] = finalName
    actor["roles"] = roles
    actor["description"] = finalDescription

    with wLock:
        actorList.append(actor)

    print(f"Finish thread {i}")


def main():
    createFilmsJson()
    completeFilms()
    createActorJson()
    pass


if __name__ == '__main__':
    main()
