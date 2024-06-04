import json
import os
import requests
import xml.etree.ElementTree as ET
import html
from rdflib import Namespace,URIRef,Graph,Literal
from rdflib.namespace import RDF,OWL,XSD

print("Parsing...")
g = Graph()
g.parse("ontology/repositoriumOntOriginal.ttl")
ns = Namespace("http://rpcw.di.uminho.pt/2024/repositorium/")
print("Parsed")

# original_string = "Science &amp; Technology"
# decoded_string = html.unescape(original_string)
# print(decoded_string)

debugDic={}
attribSet = set()

contributorCreated = set()
departmentsCreated = set() #not yet done the counter for :)
publishersCreated = set()
subjectsCreated = set()
journalsCreated = set()


counterContributors = 0
counterPublisher = 0
counterJournal = 0
counterSubject = 0

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


def debug_func(element, qualifier):
    if element not in debugDic:
        a = set()
        a.add(qualifier)
        debugDic[element] = a
        print(debugDic)
    else:
        debugDic[element].add(qualifier)


def parse_contributors(element, qualifier, authority, confidence, value ,recordUri):
    global counterContributors
    new_person_uri = URIRef(f"{ns}contributor_{counterContributors}")
    counterContributors += 1

    if value not in contributorCreated:
        g.add((new_person_uri,RDF.type,OWL.NamedIndividual))
        g.add((new_person_uri,RDF.type,ns.Contributor))
        contributorCreated.add(value)

    if qualifier=="author": #add to ontologia na tag certa
        g.add((new_person_uri, ns.authored , recordUri))
        g.add((recordUri, ns.authored_by , new_person_uri))
        
    elif qualifier == "editor":
        g.add((new_person_uri, ns.edited , recordUri))
        g.add((recordUri, ns.edited_by , new_person_uri))
        
    elif qualifier == "advisor":
        g.add((new_person_uri, ns.advised , recordUri))
        g.add((recordUri, ns.advised_by , new_person_uri))
    else:
        g.add((new_person_uri, ns.contributed , recordUri))
        g.add((recordUri, ns.contributed_by , new_person_uri))

    return new_person_uri


def parse_date(element, qualifier, authority, confidence, value ,recordUri):
    if qualifier == "issued":
        g.add((recordUri, ns.record_dateIssued, Literal(value)))
    elif qualifier == "embargo":
        g.add((recordUri, ns.record_dateEmbargo, Literal(value)))
    else:
        pass


def parse_identifier(element, qualifier, authority, confidence, value ,recordUri):
    if qualifier == "citation":
        g.add((recordUri, ns.record_citation, Literal(value)))
    elif qualifier == "issn":
        g.add((recordUri, ns.record_issn, Literal(value)))
    elif qualifier == "uri":
        g.add((recordUri, ns.record_ogUri, Literal(value)))
    elif qualifier == "doi":
        g.add((recordUri, ns.record_doi, Literal(value)))
    elif qualifier == "pmid":
        g.add((recordUri, ns.record_pmid, Literal(value)))
    elif qualifier == "tid":
        g.add((recordUri, ns.record_issn, Literal(value)))
    elif qualifier == "other":
        g.add((recordUri, ns.record_other, Literal(value)))
    elif qualifier == "eisbn":
        g.add((recordUri, ns.record_eisbn, Literal(value)))
    elif qualifier == "isbn":
        g.add((recordUri, ns.record_isbn, Literal(value)))
    elif qualifier == "eissn":
        g.add((recordUri, ns.record_eissn, Literal(value)))
    else:
        pass

def parse_description(element, qualifier, authority, confidence, value ,recordUri):
    if qualifier == "abstract":
        g.add((recordUri, ns.record_abstract, Literal(value)))
    elif qualifier == "sponsorship":
        g.add((recordUri, ns.record_sponsorship, Literal(value)))
    elif qualifier == "publicationversion":
        g.add((recordUri, ns.publicationversion, Literal(value)))
    else:
        g.add((recordUri, ns.record_description, Literal(value))) #general

def parse_language(element, qualifier, authority, confidence, value ,recordUri):
    if qualifier == "iso":
        g.add((recordUri, ns.record_language, Literal(value)))
    else:
        pass

def parse_publisher(element, qualifier, authority, confidence, value ,recordUri):
    global counterPublisher
    new_publisher_uri = URIRef(f"{ns}publisher_{counterPublisher}")
    counterPublisher += 1

    if value not in publishersCreated:
        g.add((new_publisher_uri,RDF.type,OWL.NamedIndividual))
        g.add((new_publisher_uri,RDF.type,ns.PublisherEntity))
        publishersCreated.add(value)

    #if authority != None:
    #    pass

    #TODO: verify if this cannot be a single entity
    if qualifier == "uri":
        g.add((new_publisher_uri, ns.publisher_uri, Literal(value)))
    else:
        g.add((new_publisher_uri, ns.publisher_name, Literal(value)))

    g.add((new_publisher_uri, ns.published, recordUri))
    g.add((recordUri, ns.published, new_publisher_uri))

    return new_publisher_uri


def parse_rights(element, qualifier, authority, confidence, value ,recordUri):
    if qualifier == "uri":
        g.add((recordUri, ns.record_rightsUri, Literal(value)))
    else:
        g.add((recordUri, ns.record_rights, Literal(value)))


def parse_subject(element, qualifier, authority, confidence, value ,recordUri):
    global counterSubject
    new_subject_uri = URIRef(f"{ns}subject_{counterSubject}")
    counterSubject += 1

    if value not in subjectsCreated:
        g.add((new_subject_uri,RDF.type,OWL.NamedIndividual))
        g.add((new_subject_uri,RDF.type,ns.Subject))
        subjectsCreated.add(value)

    if qualifier == "ods":
        g.add((new_subject_uri, ns.subject_ods, Literal(value)))
    elif qualifier == "fos":
        g.add((new_subject_uri, ns.subject_fos, Literal(value)))
    elif qualifier == "acm":
        g.add((new_subject_uri, ns.subject_acm, Literal(value)))
    elif qualifier == "wos":
        g.add((new_subject_uri, ns.subject_wos, Literal(value)))
    else:
        g.add((new_subject_uri, ns.subject_, Literal(value)))

    g.add((new_subject_uri, ns.is_subject_in, recordUri))
    g.add((recordUri, ns.has_subject, new_subject_uri))

    return new_subject_uri


def parse_title(element, qualifier, authority, confidence, value ,recordUri):
    if qualifier == "alternative":
        g.add((recordUri,ns.record_alternativeTitle, Literal(value)))
    else:
        g.add((recordUri,ns.record_title,Literal(value)))

def parse_type(element, qualifier, authority, confidence, value ,recordUri):
    g.add((recordUri, ns.record_type, Literal(value)))
    #if qualifier != None:
    #    if element not in debugDic:
    #        a = set()
    #        a.add(qualifier)
    #        debugDic[element] = a
    #    else:
    #        pass

def parse_peerreviewed(element, qualifier, authority, confidence, value ,recordUri):
    g.add((recordUri, ns.record_peerReviewed, Literal(value)))
    # if qualifier != None:
    #     if element not in debugDic:
    #         a = set()
    #         a.add(qualifier)
    #         debugDic[element] = a
    #     else:
    #         pass

def parse_journal(element, qualifier, authority, confidence, value ,recordUri):
    
    global counterJournal
    new_journal_uri = URIRef(f"{ns}journal_{counterJournal}")
    counterJournal += 1

    if value not in journalsCreated:
        g.add((new_journal_uri,RDF.type,OWL.NamedIndividual))
        g.add((new_journal_uri,RDF.type,ns.Journal))
        journalsCreated.add(value)


    if authority != None:
        g.add((new_journal_uri,ns.journal_authority,Literal(authority)))
    if confidence != None:
        g.add((new_journal_uri,ns.journal_confidence,Literal(confidence)))
        
    g.add((new_journal_uri,ns.journal_name,Literal(value)))

#def parse_citation_endp(element, qualifier, authority, confidence, value ,recordUri)

def  parse_publicationStatus(element, qualifier, authority, confidence, value ,recordUri):
    g.add((recordUri, ns.record_publicationStatus, Literal(value)))







def process_qualifiers(element, qualifier, authority, confidence, value ,recordUri):
    #create instance of record
    #debug_func(element, qualifier)

    if element == "contributor":
        personUri = parse_contributors(element, qualifier, authority, confidence, value ,recordUri)

    elif element == "date":
        parse_date(element, qualifier, authority, confidence, value ,recordUri)
    
    elif element == "identifier":
        parse_identifier(element, qualifier, authority, confidence, value ,recordUri)
        # debugDic = debug_func(element, qualifier)

    elif element == "description":
        parse_description(element, qualifier, authority, confidence, value ,recordUri)
        # debugDic = debug_func(element, qualifier)
        
    elif element == "language":
        parse_language(element, qualifier, authority, confidence, value ,recordUri)
        # debugDic = debug_func(element, qualifier)
        
    elif element == "publisher":
        publisherUri = parse_publisher(element, qualifier, authority, confidence, value ,recordUri)
        # debugDic = debug_func(element, qualifier)

    elif element == "rights":
        parse_rights(element, qualifier, authority, confidence, value ,recordUri)
        
        # debugDic = debug_func(element, qualifier)
    elif element == "subject":
        subjectUri = parse_subject(element, qualifier, authority, confidence, value ,recordUri)
        
        # debugDic = debug_func(element, qualifier)
    elif element == "title":
        # g.add((recordUri,ns.record_title,Literal(value)))
        parse_title(element, qualifier, authority, confidence, value ,recordUri)
        
        # debugDic = debug_func(element, qualifier)
    elif element == "type":
        parse_type(element, qualifier, authority, confidence, value ,recordUri)
            
        # debugDic = debug_func(element, qualifier)
    elif element == "peerreviewed":
        parse_peerreviewed(element, qualifier, authority, confidence, value ,recordUri)    
            
        # debugDic = debug_func(element, qualifier)
    elif element == "publicationstatus":
        parse_publicationStatus(element, qualifier, authority, confidence, value ,recordUri)
        
        # debugDic = debug_func(element, qualifier)
    elif element == "journal":
        parse_journal(element, qualifier, authority, confidence, value ,recordUri)
        # debugDic = debug_func(element, qualifier)
    
    elif element == "citationEndPage":
        #parse_citation_endp(element, qualifier, authority, confidence, value ,recordUri)
        pass
        # debugDic = debug_func(element, qualifier)
    
    elif element == "citationIssue":
        if qualifier != None:
            pass
        # debugDic = debug_func(element, qualifier)
    elif element == "citationTitle":
        if qualifier != None:
            pass
        # debugDic = debug_func(element, qualifier)
    elif element == "citationConferencePlace":
        if qualifier != None:
            pass
        # debugDic = debug_func(element, qualifier)
    elif element == "event":
        if qualifier == "title":
            pass
        else:
            pass
        # debugDic = debug_func(element, qualifier)
    elif element == "uoei":
        if qualifier != None:
            pass
        # debugDic = debug_func(element, qualifier)
    #elif element == "relation":
    #    if qualifier == "publisherversion": #this is optional
    #        pass
    #    else:
    #        pass
    elif element == "bookTitle":
        if qualifier != None:
            pass
        
        # debugDic = debug_func(element, qualifier)
    elif element == "citationVolume":
        if qualifier != None:
            pass
        
        # debugDic = debug_func(element, qualifier)
    elif element == "citationStartPage":
        if qualifier != None:
            pass
        # debugDic = debug_func(element, qualifier)
    elif element == "version":
        if qualifier != None:
            pass
        # debugDic = debug_func(element, qualifier)
    elif element == "export":
        if qualifier == "identifier":
            pass
        else:
            pass
        # debugDic = debug_func(element, qualifier)
    elif element == "conferencePublication":
        if qualifier != None:
            pass
        # debugDic = debug_func(element, qualifier)
    elif element == "comments":
        if qualifier != None:
            pass
        # debugDic = debug_func(element, qualifier)
    elif element == "citationConferenceDate":
        if qualifier != None:
            pass
        # debugDic = debug_func(element, qualifier)
    elif element == "degree":
        if qualifier == "grade":
            pass
        elif qualifier == "grantor":
            pass
        else:
            pass
        # debugDic = debug_func(element, qualifier)
    else:
        debugDic[element] = set()
    

def getInfoDIM(xmlString):

    root = ET.fromstring(xmlString)
    listRecords = root.find(getXmlString("ListRecords","top"))
    records = listRecords.findall(getXmlString("record","top"))
    
    elementSet, qualifierSet = set(), set()
    
    for record in records:
        recordHeader = record.find(getXmlString("header","top"))
        recordId = recordHeader.find(getXmlString("identifier","top")).text
        recordId = recordId.split(":")[-1]
        recordIdUri = recordId.replace('/','_')
        #TODO publish timestamp in DB
        publishTimeStamp = recordHeader.find(getXmlString("datestamp","top")).text
        #TODO setSpecs têm a informação dos "departamentos", mesmo para além dos nossos
        recordMetadata = record.find(getXmlString("metadata","top"))
        recordUri = URIRef(f"{ns}record_{recordIdUri}")
        g.add((recordUri,RDF.type,OWL.NamedIndividual))
        g.add((recordUri,RDF.type,ns.Record))
        g.add((recordUri,ns.record_id,Literal(recordId)))
        departmentIds = recordHeader.findall(getXmlString("setSpec","top"))
        
        for departmentId in departmentIds:
            #g.add 
            pass

        if recordMetadata:

            dim = recordMetadata.find(getXmlString("dim","dim"))
            fields = dim.findall(getXmlString("field","dim"))

            for field in fields:
                
                for a in field.attrib:
                    attribSet.add(a)

                element = field.attrib.get("element")
                qualifier = field.attrib.get("qualifier")
                authority = field.attrib.get("authority")
                confidence = field.attrib.get("confidence")

                value = process_qualifiers(element, qualifier, authority, confidence, field.text,recordUri)

def getInfoOPEN_AIRE(xmlString):

    root = ET.fromstring(xmlString)
    listRecords = root.find(getXmlString("ListRecords","top"))
    records = listRecords.findall(getXmlString("record","top"))
    
    elementSet, qualifierSet = set(), set()
    # debugDic={}


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
        # g.add((recordUri,RDF.type,OWL.NamedIndividual))
        # g.add((recordUri,RDF.type,ns.Record))
        # g.add((recordUri,ns.record_id,Literal(recordId)))

        if recordMetadata:

            resource = recordMetadata.find("{http://namespace.openaire.eu/schema/oaire/}resource")
            funding_references = resource.findall('.//{http://namespace.openaire.eu/schema/oaire/}fundingReference')

            for i, funding_ref in enumerate(funding_references, start=1):
                
                print(f"Funding Reference {i}:")
                funder_name_elem = funding_ref.find('{http://namespace.openaire.eu/schema/oaire/}funderName')
                if funder_name_elem is not None:
                    print("Funder Name:", funder_name_elem.text)
                funder_identifier_elem = funding_ref.find('{http://namespace.openaire.eu/schema/oaire/}funderIdentifier')
                if funder_identifier_elem is not None:
                    print("Funder Identifier Type:", funder_identifier_elem.attrib.get('funderIdentifierType', ''))
                    print("Funder Identifier:", funder_identifier_elem.text)
                funding_stream_elem = funding_ref.find('{http://namespace.openaire.eu/schema/oaire/}fundingStream')
                if funding_stream_elem is not None:
                    print("Funding Stream:", funding_stream_elem.text)
                award_number_elem = funding_ref.find('{http://namespace.openaire.eu/schema/oaire/}awardNumber')
                if award_number_elem is not None:
                    print("Award Number:", award_number_elem.text)
                print()




# metadataPrefix = "dim"
# endpoint_url = 'https://repositorium.sdum.uminho.pt/oai/oai'
# params = { 'verb': 'ListIdentifiers', 'metadataPrefix': 'oai_dc', 'metadataPrefix': 'com_1822_21291'}
# print(f'Requesting {endpoint_url}: {params}')
    
# r = requests.get(endpoint_url, params=params)
# with open("old_dim.xml",'r') as f:
#     r = f.read()


# rt = getRToken(r)
# getInfo(r)
# print(rt.text)



#rt = getRToken(r.text)
# while rt.text != None:
#     print(rt.text)
#     params = { 'verb': 'ListIdentifiers', 'resumptionToken': rt.text}
#     r = requests.get(endpoint_url, params=params)
#     rt = getRToken(r.text)


# files = os.listdir("oai_openaire")

# for file in files:
#     f = open(f"oai_openaire/{file}")
#     print(f"reading file {file}")
#     getInfoOPEN_AIRE(f.read())
#     f.close()

# for k,v in debugDic.items():
#     debugDic[k] = list(v)
# with open("debugOai_openaire.json","w") as f:
#     json.dump(debugDic,f,indent=4,ensure_ascii=False)


dimFiles = os.listdir("dim")
openaireFiles = os.listdir("oai_openaire")

for file in dimFiles:
    f = open(f"dim/{file}")
    print(f"reading file {file}")
    getInfoDIM(f.read())
    f.close()

# for file in openaireFiles:
#     f = open(f"oai_openaire/{file}")
#     print(f"reading file {file}")
#     getInfoOPEN_AIRE(f.read())
#     f.close()
    

print("Serializing")
g.serialize(format="ttl",destination="ontology/repositoriumTeste.ttl")