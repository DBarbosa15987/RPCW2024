# JSON to TTL

## Utilização

* python [json_to_ttl.py](json_to_ttl.py) <outputFile.ttl>
* o argumento do ficheiro de output é facultativo, se não for introduzido, é usado **mapa-virtual-output.ttl** por defeito

## Descrição

O script faz o povoamento de uma ontologia ttl préviamente definida em [mapa-virtual.ttl](mapa-virtual.ttl), a partir dos dados lidos do ficheiro [mapa-virtual.json](mapa-virtual.json)

## Metodologia

### Criação da ontologia
A partir dos dados JSON foi cridada uma ontologia que representasse os dados, as suas relações e as suas propriedades.\
Em termos de classes e propriedades dos dados, a ontologia tem a seguinte constituição:

* **Cidade**
    * idCidade
    * distrito
    * populacao
    * nome
    * descricao
* **Ligacao**
    * idLigacao
    * distancia



As propiedades dos objetos listam-se abaixo:

* **Ligacao** *tem_destino* **Cidade**
* **Ligacao** *tem_origem* **Cidade**



### Análise do JSON
No ficheiro json fornecido como input não constavam erros de tipo e todos os valores estavam com a formatação correta.
Restava ver se existiam erros de coerência de dados, isto é, se existiam por exemplo relações entre entidades impossíveis (tendo em conta a ontologia apresentada acima) através de referências a identificadores inexistentes.

Foi então criado o script [analyse.py](analyse.py) para averiguar a existência de relações inválidas ou até de registos repetidos. Ao executar o script concluiu-se que este tipo de erros não consta no [mapa-virtual.json](mapa-virtual.json), e por isso o mesmo foi utilizado na sem qualquer alteração.


