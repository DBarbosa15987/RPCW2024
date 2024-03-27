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

def getQuery(type,offset=0,film=None,rel=None):

    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

    match type:

        case "films":
            query += f"""
    SELECT * WHERE {{
    ?film a dbo:Film.
    ?film rdfs:label ?label.
    ?film dbp:name ?filmName.
    ?film dbo:abstract ?filmAbstract.
    filter(langMatches(lang(?filmAbstract), "en") && langMatches(lang(?label), "en")).
    optional{{?film dbo:runtime ?runtime}}
    optional{{?film dbo:releaseDate ?releaseDate.
    filter (datatype(?releaseDate) = xsd:date)}}
    
    }} OFFSET {offset}
    LIMIT {dbpediaLimit}
    """
                    
        case "updateFilms":
            query += f"""
    SELECT ?actor ?director ?musicComposer ?producer ?writer ?cinematographer ?releaseDate WHERE {{
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

        case "person":
            query += f"""
    SELECT DISTINCT ?person ?name ?bd ?description WHERE {{
        ?film a dbo:Film.
        ?film dbo:{rel} ?person.
        optional{{?person foaf:name ?name.
        filter(langMatches(lang(?name), "en"))}}
        optional{{?person dbo:birthDate ?bd.}}
        optional{{?person dbo:abstract ?description.
        filter(langMatches(lang(?description), "en")).}}
        

}} OFFSET {offset}
LIMIT {dbpediaLimit}
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
                filmUri = result["film"]["value"]
                film_name = result["label"]["value"]
                film_abstract = result["filmAbstract"]["value"]
                
                # Can be null
                releaseDate = result.get("releaseDate")
                runtime = result.get("runtime")
                
                if releaseDate:
                    releaseDate = releaseDate["value"]
                if runtime:
                    runtime = runtime["value"]


                filmList.append({
                    "uri": filmUri,
                    "nome": film_name,
                    "abstract": film_abstract,
                    "runtime" : runtime,
                    "releaseDate" : releaseDate
                })

        else:
            print("Error:", response.status_code)
            print(response.text)

        offset += dbpediaLimit
        pages += 1
        print(f"page {pages},pageSize {pageSize}, offset {offset}")

    outputFile = open("json/films.json", "w") 
    json.dump(filmList, outputFile, ensure_ascii=False,indent=4)
    outputFile.close()


def completeFilms():
    inputFile = open("json/films.json", "r")
    data = json.load(inputFile)
    inputFile.close()

    filmList = []
    
    i = 0
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = []
        for film in data:
            filmUri = film["uri"]
            future = executor.submit(process_film, filmUri, filmList,film,i)
            futures.append(future)
            i+=1
        for future in futures:
            future.result()

    outputFile = open("json/updatedFilms.json", "w")
    json.dump(filmList, outputFile, ensure_ascii=False,indent=4)
    outputFile.close()


def process_film(filmUri, filmList,film,i):

    query = getQuery(type="updateFilms", film=filmUri)
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
    newfilm["uri"] = filmUri
    newfilm["actors"] = actors
    newfilm["directors"] = directors
    newfilm["musicComposers"] = musicComposers
    newfilm["producers"] = producers
    newfilm["writers"] = writers
    newfilm["cinematographers"] = cinematographers

    with wLock:
        filmList.append(newfilm)

    print(f"Finish thread {i}")


def createActorJson():
    
    people = {
        "actors":  [],
        "directors": [],
        "musicComposers": [],
        "producers": [],
        "writers": [],
        "cinematographers": []
    }

    rel = {
        "actors": "starring",
        "directors": "director",
        "musicComposers": "musicComposer",
        "producers": "producer",
        "writers": "writer",
        "cinematographers": "cinematography"
}

    for personType in people.keys():

        offset = 0
        pageSize = dbpediaLimit
        pages = 0
        personList = []

        # Leaves cicle when the page doesn't come full
        while dbpediaLimit==pageSize:

            query = getQuery(type="person",offset=offset,rel=rel[personType])

            params = {
            "query": query,
            "format": "json"
            }

            response = requests.get(sparqlEndpoint, params=params, headers=headers)

            if response.status_code == 200:
                results = response.json()
                resultList = results["results"]["bindings"]
                pageSize = len(resultList)

                newPerson = {}

                for result in resultList:

                    person = result.get("person")
                    name = result.get("name")
                    bd = result.get("bd")
                    description = result.get("description")

                    if person:
                        person = person["value"]
                    if name:
                        name = name["value"]
                    if bd:
                        bd = bd["value"]
                    if description:
                        description = description["value"]

                    newPerson = {
                        "person": person,
                        "name": name,
                        "birthDate": bd,
                        "description": description
                    }
                    
                    personList.append(newPerson)


            else:
                print("Error:", response.status_code)
                print(response.text)

            offset += dbpediaLimit
            pages += 1
            print(f"page {pages},pageSize {pageSize}, offset {offset}, person {personType}")

        people[personType] = personList

    outputFile = open("json/people.json", "w") 
    json.dump(people, outputFile, ensure_ascii=False,indent=4)
    outputFile.close()

def main():
    createFilmsJson()
    completeFilms()
    createActorJson()


if __name__ == '__main__':
    main()
