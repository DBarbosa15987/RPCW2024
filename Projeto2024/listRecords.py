import json
import requests
import xml.etree.ElementTree as ET
import html
from rdflib import Namespace,URIRef,Graph,Literal
from rdflib.namespace import RDF,OWL,XSD

print("Parsing...")
g = Graph()
g.parse("repositoriumOriginal.ttl")
ns = Namespace("http://rpcw.di.uminho.pt/2024/repositorium")
print("Parsed")

# original_string = "Science &amp; Technology"
# decoded_string = html.unescape(original_string)
# print(decoded_string)

def getRToken(xmlString):
    root = ET.fromstring(xmlString)
    return root.find('.//{http://www.openarchives.org/OAI/2.0/}resumptionToken')


def getXmlString(s,type):
    r = ""

    match type:
        case "top":
            r = f"{{http://www.openarchives.org/OAI/2.0/}}{s}"
        case "dim":
            r = f"{{http://www.dspace.org/xmlns/dspace/dim}}{s}"
    return r



def process_qualifiers(element, qualifier, authority, confidence, value ,debugDic,recordUri):
    
    #create instance of record

    if element == "contributor":
        if qualifier=="author":
            pass
            #add to ontologia na tag certa
        elif qualifier == "editor":
            pass
        elif qualifier == "advisor":
            pass
        #elseif == "other"
        else: #other ?
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "date":
        if qualifier == "issued":
            pass
        elif qualifier == "embargo":
            pass
        else:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "identifier":
        if qualifier == "citation":
            pass
        elif qualifier == "issn":
            pass
        elif qualifier == "uri":
            pass
        elif qualifier == "doi":
            pass
        elif qualifier == "pmid":
            pass
        elif qualifier == "tid":
            pass
        elif qualifier == "other":
            pass
        elif qualifier == "eisbn":
            pass
        elif qualifier == "isbn":
            pass
        elif qualifier == "eissn":
            pass
        else:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "description":
        if qualifier == "abstract":
            pass
        elif qualifier == "sponsorship":
            pass
        elif qualifier == "publicationversion":
            pass
        else:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "language":
        if qualifier == "iso":
            pass
        else:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "publisher":
        if authority != None:
            pass
        
        if qualifier == "uri":
            pass
        else:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "rights":
        if qualifier == "uri":
            pass
        else:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)


    elif element == "subject":
        if qualifier == "ods":
            pass
        elif qualifier == "fos":
            pass
        elif qualifier == "acm":
            pass
        elif qualifier == "wos":
            pass
        else:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)
    
    elif element == "title":
        g.add((recordUri,ns.record_title,Literal(value)))
        if qualifier == "alternative":
            pass
        else:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "type":
        
        if qualifier != None:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "peerreviewed":
        
        if qualifier != None:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "publicationstatus":
        
        if qualifier != None:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)
    
    elif element == "journal":
        if authority != None:
            pass

        if confidence != None:
            pass

        if qualifier != None:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "citationEndPage":
        if qualifier != None:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)
        
    elif element == "citationIssue":
        if qualifier != None:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)


    elif element == "citationTitle":
        if qualifier != None:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)


    elif element == "citationConferencePlace":
        if qualifier != None:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)


    elif element == "event":
        if qualifier == "title":
            pass
        else:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "uoei":
        if qualifier != None:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    #elif element == "relation":
    #    if qualifier == "publisherversion": #this is optional
    #        pass
    #    else:
    #        pass

    elif element == "bookTitle":
        if qualifier != None:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "citationVolume":
        if qualifier != None:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "citationStartPage":
        if qualifier != None:
            pass

        if element not in debugDic:
            a = set()
            a.add(qualifier)
            debugDic[element] = a
        else:
            debugDic[element].add(qualifier)


    elif element == "version":
        if qualifier != None:
            pass

        if element not in debugDic:
            a = set()
            a.add(qualifier)
            debugDic[element] = a
        else:
            debugDic[element].add(qualifier)

    elif element == "export":
        if qualifier == "identifier":
            pass
        

        else:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    elif element == "conferencePublication":
        if qualifier != None:
            pass

        if element not in debugDic:
            a = set()
            a.add(qualifier)
            debugDic[element] = a
        else:
            debugDic[element].add(qualifier)

    elif element == "comments":
        if qualifier != None:
            pass

        if element not in debugDic:
            a = set()
            a.add(qualifier)
            debugDic[element] = a
        else:
            debugDic[element].add(qualifier)


    elif element == "citationConferenceDate":
        if qualifier != None:
            pass

        if element not in debugDic:
            a = set()
            a.add(qualifier)
            debugDic[element] = a
        else:
            debugDic[element].add(qualifier)

    elif element == "degree":
        if qualifier == "grade":
            pass
        elif qualifier == "grantor":
            pass
        else:
            if element not in debugDic:
                a = set()
                a.add(qualifier)
                debugDic[element] = a
            else:
                debugDic[element].add(qualifier)

    else:
        debugDic[element] = set()
    




def getInfo(xmlString):

    root = ET.fromstring(xmlString)
    listRecords = root.find(getXmlString("ListRecords","top"))
    records = listRecords.findall(getXmlString("record","top"))
    

    
    elementSet, qualifierSet = set(), set()
    debugDic={}
    #print(records)
    for record in records:
        recordHeader = record.find(getXmlString("header","top"))
        recordId = recordHeader.find(getXmlString("identifier","top")).text
        recordId = recordId.split(":")[-1]
        #TODO publish timestamp in DB
        publishTimeStamp = recordHeader.find(getXmlString("datestamp","top")).text
        #TODO setSpecs têm a informação dos "departamentos", mesmo para além dos nossos
        departmentIds = recordHeader.findall(getXmlString("setSpec","top"))
        #for ...

        recordMetadata = record.find(getXmlString("metadata","top"))
        recordUri = URIRef(f"{ns}record_{recordId}")
        g.add((recordUri,RDF.type,OWL.NamedIndividual))
        g.add((recordUri,RDF.type,ns.Record))
        g.add((recordUri,ns.record_id,Literal(recordId)))


        if recordMetadata:
            dim = recordMetadata.find(getXmlString("dim","dim"))
            fields = dim.findall(getXmlString("field","dim"))

            for field in fields:

                element = field.attrib["element"]
                qualifier = field.attrib.get("qualifier")
                authority = field.attrib.get("authority")
                confidence = field.attrib.get("confidence")

                process_qualifiers(element, qualifier, authority, confidence, field.text,debugDic,recordUri)


    for k,v in debugDic.items():
        debugDic[k] = list(v)
    with open("debug.json","w") as f:
        json.dump(debugDic,f,indent=4,ensure_ascii=False)


# metadataPrefix = "dim"
# endpoint_url = 'https://repositorium.sdum.uminho.pt/oai/oai'
# params = { 'verb': 'ListIdentifiers', 'metadataPrefix': 'oai_dc', 'metadataPrefix': 'com_1822_21291'}
# print(f'Requesting {endpoint_url}: {params}')
    
# r = requests.get(endpoint_url, params=params)
with open("old_dim.xml",'r') as f:
    r = f.read()


#rt = getRToken(r)
getInfo(r)
#print(rt.text)


#rt = getRToken(r.text)
# while rt.text != None:
#     print(rt.text)
#     params = { 'verb': 'ListIdentifiers', 'resumptionToken': rt.text}
#     r = requests.get(endpoint_url, params=params)
#     rt = getRToken(r.text)


print("Serializing")
g.serialize(format="ttl",destination="repositoriumTeste.ttl")