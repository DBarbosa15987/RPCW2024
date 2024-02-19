# JSON to TTL

## Utilização

* python json_to_ttl.py <outputFile.owl>
* o argumento do ficheiro de output é facultativo, se não fôr introduzido, é usado "ontology_plantas_output.owl"

## Descrição

O script faz o povoamento de uma ontologia ttl préviamente definida a partir dos dados lidos do ficheiro plantas.json

## Metodologia

### Criação da ontologia
A partir da dos dados JSON foi cridada uma ontologia que representasse os dados, as suas relações e as suas propriedades.\
Em termos de classes e propriedades dos dados a ontologia tem a seguinte constituição:

* **Entidade**
    * Nome_Entidade
* **Estado**
    * Tipo_Estado
* **Localização**
    * Rua
    * Local
    * Freguesia
    * Código_de_rua
* **Planta**
    * Espécie
    * Nome_Científico
* **Plantação**
    * Tutor
    * Implantação
    * Data_de_Plantação
    * Caldeira
* **Registo**
    * id
    * Data_de_atualização
    * Número_de_intervenções
    * Número_de_registo

As propiedades dos objetos listam-se abaixo:

* **Registo** *gerido_por* **Entidade**
* **Registo** *localizado_em* **Localização**
* **Plantação** *plantado_por* **Entidade**
* **Registo** *tem* **Plantação**
* **Planta** *é* **Estado**
* **Plantação** *é_de* **Planta**



### Análise do JSON
Foram detetadas várias inconsistências e erros nos dados fornecidos.\
Foi por isso necessária uma análise e e tratamento dos dados.

Este exemplo ilustra alguns dos tipo de erros econtrados:

```json
  {
    "Id": 20701727,
    "Número de Registo": 12312,
    "Código de rua": 1707935,
    "Rua": "Praceta Augusto Dias da Silva (Industrial e Político",
    "Local": "1887-1928)",
    "Freguesia": "Abóboda",
    "Espécie": "São Domingos de Rana",
    "Nome Científico": "a identificar",
    "Origem": "a identificar",
    "Data de Plantação": "",
    "Estado": "",
    "Caldeira": "",
    "Tutor": "",
    "Implantação": "",
    "Gestor": "Espaço Verde",
    "Data de actualização": "Não é municipal",
    "Número de intervenções": "30/10/2021 17:01:08"
  }
```

Aqui temos 4 tipos de problemas:

* A incoerência de tipos de dados, neste caso o **"Número de Intervenções"** deveria ser um ***int*** e está como ***string***.
* O posicionamento de valores nas chaves erradas, neste caso, o valor do **"Número de Intervenções"** é uma data que pode corresponder tanto a  **"Data de Plantação"** como **"Data de actualização"**
* O fragmento do valor da **"Rua"** que começa no seu lugar e continua na linha seguinte, como valor da chave **"Local"**
* O Valor **"a identificar"** que aparece várias vezes no ficheiro

Para este tipo de problemas foi adotada as mesma medida. Estes valores foram considerados inválidos e por isso tratados como se estivessem vazios, de modo a preservar ainda a informação correta do objeto e evitar a criação de informação errada no output.