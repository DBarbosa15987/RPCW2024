from rdflib import Namespace,URIRef,Graph, Literal, XSD
from rdflib.namespace import RDF, OWL
import json
import re
import sys

g = Graph()
g.parse("cinema.ttl")


cinema = Namespace("http://rpcw.di.uminho.pt/2024/cinema/")


def getUri(entity):
    match = re.search(r'[^/]+$', entity)
    id = ""
    if match:
        id = match.group(0)
    uri = ""
    if id != "" and "/http" not in id:
        uri = URIRef(f"{cinema}{id}")
    
    return uri

def processFilms():

    i=0
    uris = set()
    with open("../../TPC5/json/updatedFilms.json",'r') as f:
        data = json.load(f)


    for film in data:
        
        i+=1
        filmUri = film['uri']
        newFilmUri = getUri(filmUri)

        nome = film["nome"]
        runtime = film["runtime"]
        abstract = film["abstract"]
        releaseDate = film["releaseDate"]
        

        if newFilmUri not in uris:
            
            #Individuals
            g.add((newFilmUri, RDF.type, OWL.NamedIndividual))
            g.add((newFilmUri, RDF.type, cinema.Film))
            if nome: 
                g.add((newFilmUri, cinema.title, Literal(film["nome"])))
            if runtime: 
                runtime = int(float(runtime)/60)
                g.add((newFilmUri, cinema.duration, Literal(runtime,datatype=XSD.int)))
            if abstract:
                g.add((newFilmUri, cinema.description, Literal(film["abstract"])))
            if releaseDate: 
                g.add((newFilmUri, cinema.releaseDate, Literal(film["releaseDate"],datatype=XSD.date)))
        else:
            uris.add(newFilmUri)

        # Lists
        personTypeMatch = {
            "actors": (cinema.hasActor,cinema.acted),
            "directors": (cinema.hasDirector,cinema.directed),
            "musicComposers": (cinema.hasComposer,cinema.composed),
            "producers": (cinema.hasProducer,cinema.produced),
            "writers": (cinema.hasWriter,cinema.wrote)
        }

        for personType,ttlType in personTypeMatch.items():
            
            for person in film[personType]:

                personUri = getUri(person)
                if personUri != "":
                    g.add((newFilmUri, ttlType[0], personUri))
                    g.add((personUri, ttlType[1], newFilmUri))



def processActors():

    with open("../../TPC5/json/people.json",'r') as f:
        data = json.load(f)

    personTypeMatch = {
        "actors": cinema.Actor,
        "directors": cinema.Director,
        "musicComposers": cinema.Composer,
        "producers": cinema.Producer,
        "writers": cinema.Writer
        }

    i = 0

    for personType,ttlType in personTypeMatch.items():

        print(personType)

        for person in data[personType]:
                    
            i+=1
            personUri = person['person']
            uri = getUri(personUri)
            if uri != "":

                name = person["name"]
                description = person["description"]
                birthDate = person["birthDate"]

                g.add((uri, RDF.type, OWL.NamedIndividual))
                g.add((uri, RDF.type, ttlType))

                if name:
                    g.add((uri, cinema.name, Literal(name) ))
                if description:
                    g.add((uri, cinema.description, Literal(description) ))
                if birthDate:
                    g.add((uri, cinema.birthDate, Literal(birthDate) ))


def main():

    processActors()
    print("------------------------------------------------")
    processFilms()
    print("serialize started")

    outputFile = "cinemaOutput.ttl"
    if len(sys.argv)>1:
        outputFile = sys.argv[1]


    g.serialize(format="ttl",destination=outputFile)
    print("done")

if __name__ == "__main__":
    main()