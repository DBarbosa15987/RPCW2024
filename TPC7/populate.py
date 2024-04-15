from rdflib import Namespace,URIRef,Graph,Literal
from rdflib.namespace import RDF,OWL,XSD
import json

g = Graph()
g.parse("alunos.ttl")

ns = Namespace("http://rpcw.di.uminho.pt/2024/alunos/")

def processAlunos():

    with open("aval-alunos.json",'r') as f:
        data = json.load(f)
    
    alunosList = data["alunos"]
    alunosSet = set()

    for aluno in alunosList:

        id = aluno.get("idAluno")
        if id not in alunosSet:    
            nome = aluno.get("nome")
            curso = aluno.get("curso")
            notaProjeto = aluno.get("projeto")
            tpcs = aluno.get("tpc") #lista
            exames = aluno.get("exames")

            # Alunos
            alunoUri = URIRef(f"{ns}{id}")
            g.add((alunoUri, RDF.type, OWL.NamedIndividual))
            g.add((alunoUri, RDF.type, ns.Aluno))
            g.add((alunoUri, ns.idAluno, Literal(id)))

            if nome:
                g.add((alunoUri, ns.nome, Literal(nome)))
            if curso:
                g.add((alunoUri, ns.curso, Literal(curso)))
            if notaProjeto:
                project_id = URIRef(f"projeto_{id}")
                g.add((project_id, RDF.type, OWL.NamedIndividual))
                g.add((project_id, RDF.type, ns.Projeto))
                g.add((project_id, ns.notaProjeto, Literal(notaProjeto,datatype=XSD.int)))

                g.add((alunoUri,ns.tem_projeto,project_id))
            if tpcs:
                
                for tpc in tpcs:
                    tp = tpc["tp"]
                    nota = tpc["nota"]
                    tpc_id = URIRef(f"tpc_{id}_{tp}")
                    g.add((tpc_id, RDF.type, OWL.NamedIndividual))
                    g.add((tpc_id, RDF.type, ns.TPC))

                    g.add((tpc_id, ns.tp,Literal(tp)))
                    g.add((tpc_id, ns.notaTPC,Literal(nota,datatype=XSD.float)))

                    g.add ((alunoUri,ns.tem_tpc,tpc_id))
                
            if exames:

                examesList = exames.items() # list((epoca,nota))

                for epoca,nota in examesList:
                    exameId = URIRef(f"exame_{id}_{epoca}")
                    g.add((exameId, RDF.type, OWL.NamedIndividual))
                    g.add((exameId, RDF.type, ns.Exame))

                    g.add((exameId, ns.epoca, Literal(epoca)))
                    g.add((exameId, ns.notaExame,Literal(nota,datatype=XSD.int)))

                    g.add((alunoUri,ns.tem_exame,exameId))
            alunosSet.add(id)

        else:
            print(id)

    print(len(alunosSet))

processAlunos()
g.serialize(format="ttl",destination="alunosOutput.ttl")
