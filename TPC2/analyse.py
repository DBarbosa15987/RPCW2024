import json
import sys

f = open(sys.argv[1])
bd = json.load(f)
f.close()


alunos = bd["alunos"]
cursos = bd["cursos"]
instrumentos = bd["instrumentos"]

curso_instId__inst_dic = {}
curso_id_inst_dic = {}

for curso in cursos:
    
    curso_instId__inst_dic[curso["instrumento"]["id"]] = curso["instrumento"]["#text"]
    curso_id_inst_dic[curso["id"]]= curso["instrumento"]["#text"]
    
aluno_curso_inst_dic={}
for aluno in alunos:
    aluno_curso_inst_dic[aluno["curso"]] = aluno["instrumento"] 

instrumentos_dic = {}
for i in instrumentos:
    instrumentos_dic[i["id"]]=i["#text"]


absent = []
error = []


for i in curso_instId__inst_dic: 
    if(i in instrumentos_dic):
        if(instrumentos_dic[i] == curso_instId__inst_dic[i]):
            pass
        else:
            error.append((i,curso_instId__inst_dic[i]))
    else:
        absent.append((i,curso_instId__inst_dic[i]))

print(absent)
print(len(absent))
print(error)

absent = []
error = []

for i in aluno_curso_inst_dic:

    if(i in curso_id_inst_dic):
        if(aluno_curso_inst_dic[i] == curso_id_inst_dic[i]):
            pass
        else:
            error.append((i,aluno_curso_inst_dic[i]))
    else:
        absent.append((i,aluno_curso_inst_dic[i]))


print(absent)
print(len(absent))
print(error)