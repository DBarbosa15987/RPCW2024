from datetime import datetime
import json
import re
import sys

def getDataXSD(data):
    try:
        
        date_obj = datetime.strptime(data, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%Y-%m-%dT00:00:00Z')

        return formatted_date
    except ValueError:
        return ""

def getLista(dic,id):

    r = ""
    for i in dic[id]:
        r += f":{i},\n"

    # retirar a ",\n" a mais no último elemento da lista
    r = r[:-2]
    return r

ficheiroOutput = "escolaDeMusicaOutput.owl"
if(len(sys.argv)>1):
    ficheiroOutput = sys.argv[1]

f = open("clean_db.json")
bd = json.load(f)
f.close()

f = open("escolaDeMusica.owl")
ttl = f.read()
f.close()

ontologia = "http://rpcw.di.uminho.pt/2024/escola-de-musica"


ttl+="""

#################################################################
#    Individuals
#################################################################
"""


tem_estudante_dic = {}

for aluno in bd["alunos"]:

    dataNasc = getDataXSD(aluno['dataNasc'])
    alunoId = aluno['id']
    cursoId = aluno['curso']

    if(cursoId not in tem_estudante_dic):
        tem_estudante_dic[cursoId] = [alunoId]
    else:
        tem_estudante_dic[cursoId].append(alunoId)


    registoAluno = f"""

###  {ontologia}#{alunoId}
:{alunoId} rdf:type owl:NamedIndividual ,
                 :Aluno ;
        :esta_inscrito_em :{cursoId} ;
        :alunoId "{alunoId}"^^xsd:string ;
        :anoCurso "{aluno['anoCurso']}"^^xsd:int ;
        :dataNasc "{dataNasc}"^^xsd:dateTime ;
        :nome "{aluno['nome']}"^^xsd:string .

"""
    ttl += registoAluno

    
lecionado_em_dic = {}

for curso in bd["cursos"]:

    cursoId = curso['id']
    instId = curso['instrumento']['id']
    alunos = getLista(tem_estudante_dic,cursoId)


    if(instId not in lecionado_em_dic):
        lecionado_em_dic[instId] = [cursoId]
    else:
        lecionado_em_dic[instId].append(cursoId)

    registoCurso = f"""

###  {ontologia}#{cursoId}
:{cursoId} rdf:type owl:NamedIndividual ,
                 :Curso ;
        :e_de :{instId} ;
        :tem_estudante {alunos} ;
        :cursoId "{cursoId}"^^xsd:string .

"""
    ttl += registoCurso


for inst in bd["instrumentos"]:

    instId = inst['id']
    cursos = getLista(lecionado_em_dic,instId)

    registoInst = f"""

###  {ontologia}#{instId}
:{instId} rdf:type owl:NamedIndividual ,
                       :Instrumento ;
              :lecionado_em {cursos} ;
              :instrumentoId "{instId}"^^xsd:string ;
              :text "{inst['#text']}"^^xsd:string .

"""
    ttl += registoInst


f = open(ficheiroOutput,"w")
f.write(ttl)
f.close()
