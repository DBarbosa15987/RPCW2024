# JSON to TTL

## Utilização

* python **json_to_ttl.py** <outputFile.owl>
* o argumento do ficheiro de output é facultativo, se não for introduzido, é usado **escolaDeMusicaOutput.owl** por defeito

## Descrição

O script faz o povoamento de uma ontologia ttl préviamente definida em **escolaDeMusica.owl**, a partir dos dados lidos do ficheiro **clean_db.json**

## Metodologia

### Criação da ontologia
A partir dos dados JSON foi cridada uma ontologia que representasse os dados, as suas relações e as suas propriedades.\
Em termos de classes e propriedades dos dados a ontologia tem a seguinte constituição:

* **Aluno**
    * alunoId
    * anoCurso
    * dataNasc
    * nome
* **Curso**
    * cursoId
    * duracao
    * designacao
* **Instrumento**
    * instrumentoId
    * text


As propiedades dos objetos listam-se abaixo:

* **Curso** *e_de* **Instrumento**
* **Instrumento** *lecionado_em* **Curso**
* **Aluno** *esta_inscrito_em* **Curso**
* **Curso** *tem_estudante* **Aluno**



### Análise do JSON
O ficheiro de input não tinha erros de tipo, todos os valores json correspondiam ao tipo devido com a formatação correta. No entanto, o json tinha erros de coerência, nomeadamente o facto alunos estarem incritos em cursos que não existiam. Devido à redundância que os dados forneceram foi possível detetar que era muito provavelmente um erro de introdução dos dados.

Segue-se o exemplo abaixo:

```json

"aluno": {
      "id": "A39343",
      "nome": "SERGIO FELICIANO FERREIRA JACOME",
      "dataNasc": "2002-10-23",
      "curso": "CS19",
      "anoCurso": "6",
      "instrumento": "Violoncelo"
    }

"curso": {
      "id": "CB19",
      "designacao": "Curso Básico de Violoncelo",
      "duracao": "5",
      "instrumento": {
        "id": "I19",
        "#text": "Violoncelo"
      }
    }

```

Com este exemplo assume-se que de facto este aluno está inscrito no CB19 (Curso Básico 19), visto que não existe nenhum CS19 (Curso Supletivo 19) e que o instrumento corresponde.

Para poder analisar este tipo de erro, foi criado um script **analise.py**. Foram tiradas as seguintes conclusões:

* Todos os instrumentos mencionados na lista de cursos existiam na lista de instrumentos e todos os e todos os ids correspondiam aos instrumentos certos
* Os instrumentos da lista de alunos estavam todos presentes na lista de cursos, ou seja, todos os alunos tocavam um instrumento lecionado na escola
* Existiam ids de cursos na lista dos alunos que não estavam presentes na lista de cursos, ou seja, cursos inexistentes no json

Depois destas conclusões foi feita uma tentativa de correção de dados em **db_json** usando o script **cleanUp.py**, criando um novo ficheiro, **clean_db.json**.

