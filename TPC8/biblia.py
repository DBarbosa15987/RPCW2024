import xml.etree.ElementTree as ET
from rdflib import Namespace,URIRef,Graph,Literal
from rdflib.namespace import RDF,OWL,XSD


g = Graph()
g.parse("familia-base.ttl")
ns = Namespace("http://rpcw.di.uminho.pt/2024/familia/")


tree = ET.parse("biblia.xml")
root = tree.getroot()


for person in root.iter("person"):

    id = person.find("id").text
    nome = person.find("namegiven").text
    sex = person.find("sex").text

    personUri = URIRef(f"{ns}{id}")
    g.add((personUri, RDF.type, OWL.NamedIndividual))
    g.add((personUri, RDF.type, ns.Pessoa))
    g.add((personUri,ns.nome,Literal(nome)))        

    for child in person.findall("child"):
        childId = child.attrib.get("ref")
        childUri = URIRef(f"{ns}{childId}")

        if sex == "M":
            g.add((childUri,ns.temPai,personUri))
        elif sex == "F":
            g.add((childUri,ns.temMae,personUri))

g.serialize(format="ttl",destination="biblia.ttl")