import requests

def menu():
    print('(1): Identify')
    print('(2): ListSets')
    print('(3): ListMetadataFormats')
    print('(4): ListRecords')
    print('(5): GetRecord')
    print('(6): ListIdentifiers')
    print('(0): Sair')

# Define the OAI-PMH endpoint URL
# endpoint_url = 'https://www.hindawi.com/oai-pmh/oai.aspx'
# endpoint_url = 'https://www.arquivo.comiteolimpicoportugal.pt/OAI-PMH/oai/'
endpoint_url = 'https://repositorium.sdum.uminho.pt/oai/oai'

def req(url, verb, metadataprefix=None):
    print(f'Requesting {url}: {verb}')
    params = { 'verb': verb}
    if metadataprefix != None:
        params['metadataPrefix'] = metadataprefix
    r = requests.get(url, params=params)
    f = open('out.xml', 'wb')
    f.write(r.content)
    f.close()

menu()
opcao = input('Introduza uma opção:')
while opcao != '0':
    match opcao:
        case '1': 
            req(endpoint_url, 'Identify')
        case '2': 
            req(endpoint_url, 'ListSets')
        case '3': 
            req(endpoint_url, 'ListMetadataFormats')
        case '4': 
            req(endpoint_url, 'ListRecords', 'aif')
        case '5': 
            req(endpoint_url, 'ListRecords', 'aif')
        case '6': 
            req(endpoint_url, 'ListIdentifiers')
        case _:
            print("Opção não suportada. Selecione uma nova opção.")
    menu()
    opcao = input('Introduza uma opção:')
