import requests
import xml.etree.ElementTree as ET


endpoint_url = 'https://repositorium.sdum.uminho.pt/oai/oai'

#1822/43244
prefixes = ["dim","oai_openaire"]
departments = ["com_1822_21291","com_1822_21290","com_1822_401","com_1822_21292","com_1822_14394"]

def getRToken(xmlString):
    root = ET.fromstring(xmlString)
    return root.find('.//{http://www.openarchives.org/OAI/2.0/}resumptionToken')

for dep in departments:
    for pref in prefixes:
        i=0
        params = { 'verb': "ListRecords","metadataPrefix":pref,'set': dep}
        print(f'Requesting {endpoint_url}: {params}')
        r = requests.get(endpoint_url, params=params)
        rt = getRToken(r.text)
        f = open(f'{pref}/records_{pref}_{i}_{dep}.xml','wb')
        f.write(r.content)
        f.close()
        print(f'Recorded: {pref}/records_{pref}_{i}_{dep}.xml')



        while rt.text != None:
            i+=1
            print(rt.text)
            params = { 'verb': 'ListRecords', 'resumptionToken': rt.text}
            print(f'Requesting {endpoint_url}: {params}')
            r = requests.get(endpoint_url, params=params)

            f = open(f'{pref}/records_{pref}_{i}_{dep}.xml','wb')
            f.write(r.content)
            f.close()
            print(f'Recorded: {pref}/records_{pref}_{i}_{dep}.xml')
            
            rt = getRToken(r.text)
