# Filmes

Programa que obtem informação relativa aos filmes presentes na dbPedia, construindo ficheiros json com as informações recolhidas

## Utilização

*  ```python script.py``` 

## Dados Recolhidos

Os dados recolhidos são provenientes da dbPedia, através da API da mesma, com queries SPARQL.

Foram recolhidos dados sobre os filmes de tipo dbo:Film e dos atores que participaram nos mesmos. Abaixo listam-se os dados recolhidos.

Filmes:

* Uri
* Nome
* Descrição
* Duração
* Atores
* Diretores
* Músicos
* Produtores
* Escritores

Pessoas:

* Uri
* Nome
* Descrição
* Data de Nascimento

## Output

Os ficheiros produzidos pelo programa são [people.json](json/people.json), [films.json](json/films.json) e [updatedFilms.json](json/updatedFilms.json), localizados na diredoria [json](json).

### people.json

Ficheiro com um objeto que representa a lista de pessoas de cada categoria.

Ex:
```json
{
    "actors": [
        {
            "person": "person",
            "name": "name",
            "birthDate": "birthDate",
            "description": "description"
        }
    ],
    "directors": [],
    "musicComposers": [],
    "producers": [],
    "writers": [],
    "cinematographers": []
}
```

### films.json

Ficheiro temporário que serve como intermediário entre a função de obter os atributos singulares dos filmes e os plurares.

É criado para poder permitir que as funções do script possam ser executadas individualmente.

### updatedFilms.json

Ficheiro final com toda a informação recolhida sobre cada filme.

Ex:
```json
[
    {
        "uri": "uri",
        "nome": "nome",
        "abstract": "abstract",
        "runtime": "runtime",
        "releaseDate": "releaseDate",
        "actors": [],
        "directors": [],
        "musicComposers": [],
        "producers": [],
        "writers": [],
        "cinematographers": []
    }
]
```

## Metodologia

Devido ao facto da informação desejada ser bastante extensa e por vezes incompleta, foram tomadas decisões para colmatar esse entraves. 

Primeiramente, o programa que está dividido em 3 partes que correspondem a 3 funções: createFilmsJson, completeFilms, createActorJson. Esta divisão permite o tratamento destas funções de forma diferente tal como a opção de executá-las uma de cada vez para efeitos de debug.

Neste caso a função completeFilms é a que demora mais tempo, visto que tem que fazer tantos request como filmes (cerca de 150 000) e foca por isso dependente do overhead introduzido pela API da dbPedia. Utilizou-se uma ThreadPool para acelerar o processo de uma forma controlada.

Apresentam-se abaixo as 3 principais funções que compõem o programa

### createFilmsJson

Função que cria o ficheiro [films.json](json/films.json) com os atributos singulares dos filmes. 

### completeFilms

Função que lê o ficheiro [films.json](json/films.json) e acrescenta a informação restante a cada filme e escreve o json atualizado para um novo ficheiro [updatedFilms.json](json/updatedFilms.json).

### createActorJson

Função que cria o ficheiro [people.json](json/people.json) com os atributos das pessoas.

