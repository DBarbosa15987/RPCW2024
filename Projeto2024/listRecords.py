import requests
import xml.etree.ElementTree as ET
import html

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

def getInfo(xmlString):

    root = ET.fromstring(xmlString)
    listRecords = root.find(getXmlString("ListRecords","top"))
    records = listRecords.findall(getXmlString("record","top"))
    
    attribSet = set()
    #print(records)
    for record in records:
        recordHeader = record.find(getXmlString("header","top"))
        recordId = recordHeader.find(getXmlString("identifier","top")).text
        #TODO publish timestamp in DB
        publishTimeStamp = recordHeader.find(getXmlString("datestamp","top")).text
        #TODO setSpecs têm a informação dos "departamentos", mesmo para além dos nossos
        departmentIds = recordHeader.findall(getXmlString("setSpec","top"))
        #for ...

        recordMetadata = record.find(getXmlString("metadata","top"))

        if recordMetadata:

            dim = recordMetadata.find(getXmlString("dim","dim"))
            fields = dim.findall(getXmlString("field","dim"))
            for field in fields:
                match field.attrib["element"]:
                    case "description":
                        pass
                    case "citationEndPage":
                        pass
                    case "citationIssue":
                        pass
                    case "date":
                        pass
                    case "citationTitle":
                        pass
                    case "title":
                        pass
                    case "citationConferencePlace":
                        pass
                    case "event":
                        pass
                    case "uoei":
                        pass
                    case "relation":
                        pass
                    case "publicationstatus":
                        pass
                    case "bookTitle":
                        pass
                    case "contributor":
                        pass
                    case "citationVolume":
                        pass
                    case "language":
                        pass
                    case "citationStartPage":
                        pass
                    case "type":
                        pass
                    case "publisher":
                        pass
                    case "version":
                        pass
                    case "identifier":
                        pass
                    case "peerreviewed":
                        pass
                    case "export":
                        pass
                    case "subject":
                        pass
                    case "rights":
                        pass
                    case "journal":
                        pass
                    case "conferencePublication":
                        pass
                    case "comments":
                        pass
                    case "citationConferenceDate":
                        pass
                    case "degree":
                        pass

        else:
            pass
    print(attribSet)


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

