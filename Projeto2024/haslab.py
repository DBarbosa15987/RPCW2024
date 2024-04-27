# OAIpmh: Recuperar um set inteiro: Haslab
# 2024-03-30 by jcr
#
import requests
# --- XML Processing ---
import xml.etree.ElementTree as ET

def getIds(xmlString):
    res = []
    root = ET.fromstring(xmlString)
    for id in root.findall('.//{http://www.openarchives.org/OAI/2.0/}identifier'):
        res.append(id.text)
    return res

def getRToken(xmlString):
    root = ET.fromstring(xmlString)
    return root.find('.//{http://www.openarchives.org/OAI/2.0/}resumptionToken')

endpoint_url = 'https://repositorium.sdum.uminho.pt/oai/oai'
params = { 'verb': 'ListIdentifiers', 'metadataPrefix': 'oai_dc', 'set': 'com_1822_21291'}
print(f'Requesting {endpoint_url}: {params}')
    
r = requests.get(endpoint_url, params=params)
lista_ids = getIds(r.text)
rt = getRToken(r.text)

while rt.text != None:
    print(rt.text)
    params = { 'verb': 'ListIdentifiers', 'resumptionToken': rt.text}
    r = requests.get(endpoint_url, params=params)
    lista_ids = lista_ids + getIds(r.text)
    rt = getRToken(r.text)

print(lista_ids)