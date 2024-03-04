import json
import sys

f = open("mapa-virtual.json")
bd = json.load(f)
f.close()

f = open("mapa-virtual.ttl",'r')
ttl = f.read()
f.close()

ficheiroOutput = "mapa-virtual-output.ttl"
if(len(sys.argv)>1):
    ficheiroOutput = sys.argv[1]


ontologia = "http://rpcw.di.uminho.pt/2024/mapa-virtual"
ttl += """

#################################################################
#    Individuals
#################################################################

"""

cidades_dic = {}

for cidade in bd["cidades"]:

    cidadeId = cidade['id']
    cidades_dic[cidadeId] = cidade

    ttl += f"""

###  {ontologia}#{cidadeId}
:{cidadeId} rdf:type owl:NamedIndividual ,
               :Cidade ;
      :descricao "{cidade['descrição']}"^^xsd:string ;
      :distrito "{cidade['distrito']}"^^xsd:string ;
      :idCidade "{cidadeId}"^^xsd:string;
      :nome "{cidade['nome']}"^^xsd:string ;
      :populacao "{int(cidade['população'])}"^^xsd:int .


"""

for ligacao in bd["ligacoes"]:

    ligacaoId = ligacao['id']

    ttl += f"""

###  {ontologia}#{ligacaoId}
:{ligacaoId} rdf:type owl:NamedIndividual ,
               :Ligacao ;
      :tem_destino :{ligacao['destino']} ;
      :tem_origem :{ligacao['origem']} ;
      :distancia "{ligacao['distância']}"^^xsd:int ;
      :idLigacao "{ligacaoId}"^^xsd:string .


"""


f = open(ficheiroOutput,'w')
f.write(ttl)
f.close()




