import json

f = open("db.json",'r',encoding='utf-8')
bd = json.load(f)
f.close()

f = open("clean_db.json", "w",encoding='utf-8')



alunos = bd["alunos"]
cursos = bd["cursos"]
instrumentos = bd["instrumentos"]

for a in alunos:
    inst = a["instrumento"]
    curso = a["curso"]
    for c in cursos:
        if(inst == c["instrumento"]["#text"]):
            if curso[:2]== c["id"][:2] and curso[2:]!= c["id"][2:]:
                a["curso"] = c["id"]

jsonDump = {
    "alunos":alunos,
    "cursos": cursos,
    "instrumentos": instrumentos
}

json.dump(jsonDump,f,indent=4,ensure_ascii=False)
f.close()