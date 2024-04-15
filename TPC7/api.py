from flask import Flask, jsonify, request
import requests

app = Flask(__name__)
graphdb_endpoint = "http://localhost:7200/repositories/Alunos"

def executeQuery(sparqlQuery):

    payload = {"query": sparqlQuery}

    response = requests.get(graphdb_endpoint, params=payload,
        headers = {'Accept': 'application/sparql-results+json'}
    )

    data = None

    if response.status_code == 200:
        data = response.json()["results"]["bindings"]

    return data


def getQuery(k,arg=None):

    sparqlQuery = ""

    match k:
        case "curso":
            sparqlQuery = f"""

PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

    SELECT ?idAluno ?nome WHERE {{
        ?aluno a :Aluno.
        ?aluno :idAluno ?idAluno.
        ?aluno :curso "{arg}".
        ?aluno :nome ?nome.   	
}}order by asc(?nome)
"""
            
        case "groupBy":

            match arg:
                case "curso":
                    sparqlQuery = """

PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

SELECT ?curso (count(?aluno) as ?alunos)  WHERE {
    	?aluno a :Aluno.
    	?aluno :curso ?curso.
    	
}group by ?curso
order by asc(?curso)
"""

                case "projeto":
                    sparqlQuery = """
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

SELECT ?nota (count(?aluno) as ?alunos)  WHERE {
    	?aluno a :Aluno.
    	?aluno :tem_projeto ?projeto.
    	?projeto :notaProjeto ?nota.
    	
}group by ?nota
order by asc(?nota)
"""

                case "recurso":
                    sparqlQuery = """
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

SELECT ?idAluno ?nome ?curso ?recurso  WHERE {
    	?aluno a :Aluno.
    	?aluno :idAluno ?idAluno.
      	?aluno :nome ?nome.
      	?aluno :curso ?curso.
    	?aluno :tem_exame ?exame.
    	?exame :epoca "recurso".
    	?exame :notaExame ?recurso.
    	  	
}order by asc(?nome)
"""

        case "alunos":

            sparqlQuery = """
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

SELECT ?idAluno ?nome ?curso WHERE {
      ?aluno a :Aluno.
      ?aluno :idAluno ?idAluno.
      ?aluno :nome ?nome.
      ?aluno :curso ?curso.
    } ORDER BY ASC(?nome)
    """


    return sparqlQuery


def alunosGroupBy(sparqlQuery,arg):

    result = executeQuery(sparqlQuery)
   
    alunosList = []

    if result:

        match arg:

            case "curso":
                
                for entry in result:

                    curso = entry['curso']['value']
                    alunos = entry['alunos']['value']

                    aluno = {
                        "curso": curso,
                        "alunos": alunos

                    }
                    alunosList.append(aluno)
                    

            case "projeto":
                for entry in result:

                    nota = entry['nota']['value']
                    alunos = entry['alunos']['value']

                    aluno = {
                        "nota": nota,
                        "alunos": alunos
                    }
                    alunosList.append(aluno)

            case "recurso":
                for entry in result:

                    idAluno = entry['idAluno']['value']
                    nome = entry['nome']['value']
                    curso = entry['curso']['value']
                    recurso = entry['recurso']['value']

                    aluno = {
                        "idAluno": idAluno,
                        "nome": nome,
                        "curso": curso,
                        "recurso": recurso
                    }

                    alunosList.append(aluno)

        return jsonify({"alunos": alunosList})
    else:
        return jsonify({"error": "Página não encontrada"}), 404


def listAlunos(sparqlQuery, curso=None):

    result = executeQuery(sparqlQuery)
    alunos = []
    if result:
        for entry in result:
            
            idAluno = entry['idAluno']['value']
            nome = entry['nome']['value']
            if curso is None:
                curso = entry['curso']['value']


            aluno = {
                "idAluno" : idAluno,
                "nome" : nome,
                "curso" : curso
            }
            alunos.append(aluno)

        return jsonify({"alunos": alunos})
    else:
        return jsonify({"error": "Página não encontrada"}), 404


@app.route('/api/alunos/<string:id>')
def alunosById(id):
    
    sparqlQuery = f"""
    PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

    SELECT ?nome ?curso WHERE {{
        ?aluno a :Aluno ;
            :idAluno "{id}" ;
            :nome ?nome ;
            :curso ?curso .
    }}
    """

    result = executeQuery(sparqlQuery)

    if result:
        
        entry = result[0]
        
        nome = entry['nome']['value']
        curso = entry['curso']['value']

        aluno = {
            "idAluno" : id,
            "nome" : nome,
            "curso" : curso
        }

        return jsonify(aluno)
    else:
        return jsonify({"error": f"Aluno com id {id} não encontrado"}), 404


@app.route('/api/alunos')
def alunos():
    
    curso = request.args.get('curso')
    groupBy = request.args.get('groupBy')

    jsonObj = {}

    if curso:
        sparqlQuery = getQuery("curso",curso)
        jsonObj = listAlunos(sparqlQuery,curso)
        
    elif groupBy:
        sparqlQuery = getQuery("groupBy",groupBy)
        jsonObj = alunosGroupBy(sparqlQuery,groupBy)

    else:
        sparqlQuery = getQuery("alunos")
        jsonObj = listAlunos(sparqlQuery)

    return jsonObj


@app.route("/api/alunos/tpc")
def alunosTPC():

    sparqlQuery = f"""
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

SELECT ?idAluno ?nome ?curso (count(?tpcs) as ?ntpc) WHERE {{
    ?aluno a :Aluno.
    ?aluno :idAluno ?idAluno.
    ?aluno :curso ?curso.
    ?aluno :nome ?nome.
    ?aluno :tem_tpc ?tpcs.
    	
}}group by ?idAluno ?nome ?curso
order by ?nome
"""
    
    result = executeQuery(sparqlQuery)
    alunos = []

    if result:
        for entry in result:

            idAluno = entry['idAluno']['value']
            nome = entry['nome']['value']
            curso = entry['curso']['value']
            ntpc = entry['ntpc']['value']

            aluno = {
                "idAluno": idAluno,
                "nome": nome,
                "curso": curso,
                "ntpc": ntpc
            }

            alunos.append(aluno)

        return jsonify({"alunos": alunos})

    else:
        return jsonify({"error": 'TPCs não encontrados'}), 404


@app.route("/api/alunos/avaliados")
def avaliados():

    sparqlQuery = """
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

SELECT ?idAluno ?nome ?curso ?notaProjeto (max(?notaExame) as ?notaExameMax) (sum(?tpc) as ?sumNotaTPC) WHERE {
      ?aluno a :Aluno.
      ?aluno :idAluno ?idAluno.
      ?aluno :nome ?nome.
      ?aluno :curso ?curso.
      ?aluno :tem_exame ?exame.
      ?exame :notaExame ?notaExame.
      ?aluno :tem_projeto ?projeto.
      ?projeto :notaProjeto ?notaProjeto.
      ?aluno :tem_tpc ?tpcs.
      ?tpcs :notaTPC ?tpc.
} group by ?idAluno ?nome ?curso ?notaProjeto
ORDER BY ASC(?nome)
"""

    result = executeQuery(sparqlQuery)
    alunos = []
    if result:
        for entry in result:

            idAluno = entry["idAluno"]['value']
            nome = entry["nome"]['value']
            curso = entry["curso"]['value']
            notaProjeto = int(entry["notaProjeto"]['value'])
            notaExameMax = int(entry["notaExameMax"]['value'])
            sumNotaTPC = float(entry["sumNotaTPC"]['value'])

            notaFinal = 0
            if notaProjeto >= 10 and notaExameMax >= 10:
                notaFinal = sumNotaTPC + 0.4*notaExameMax + 0.4*notaProjeto

            notaFinalPauta = 'R' if notaFinal < 10 else str(notaFinal)

            aluno = {
                "idAluno": idAluno,
                "nome": nome,
                "curso": curso,
                "notaFinal": notaFinalPauta
            }

            alunos.append(aluno)

        return jsonify({"alunos":alunos})
    
    else:
        return jsonify({"error": "Página não encontrada"}), 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")


