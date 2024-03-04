import json

f = open("mapa-virtual.json")
bd = json.load(f)
f.close()


cidades = bd['cidades']
ligacoes = bd['ligacoes']
cidadesDic = {}

for cidade in cidades:
    if(cidade['id'] not in cidadesDic):
        cidadesDic[cidade['id']] = cidade
    else:
        print(f"Cidade repetida: {cidade['id']}")


ligacoesSet = set()

for ligacao in ligacoes:

    if(ligacao['id'] in ligacoesSet):
        print(f"Ligação repetida: {ligacao['id']}")
    else:
        ligacoesSet.add(ligacao['id'])

    origem = ligacao['origem']
    destino = ligacao['destino']

    if(origem not in cidadesDic):
        print(f"Origem {origem} não existe na lista das cidades")

    if(destino not in cidadesDic):
        print(f"Destino {destino} não existe na lista das cidades")
