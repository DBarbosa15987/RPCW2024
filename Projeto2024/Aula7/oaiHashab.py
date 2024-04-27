import requests

endpoint_url = 'https://repositorium.sdum.uminho.pt/oai/oai'

metadataPrefix = "oai_dc"
#1822/43244
params = { 'verb': "ListRecords","metadataPrefix":metadataPrefix, 'set': 'com_1822_21291'}
r = requests.get(endpoint_url, params=params)
f = open(f'haslab_single_{metadataPrefix}.xml','wb')
f.write(r.content)
f.close()
