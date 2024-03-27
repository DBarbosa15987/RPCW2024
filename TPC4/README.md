# Tabela Periódica
<!-- TODO tem que ter uma instancia de  docker ligado -->

## Requisitos

* É necessária a bibliteca ```flask```

* Esta aplicação faz queries por default ao endpoint http://localhost:7200/repositories/TabPeriodica, por isso este repositório tem que existir para o website funcionar.

## Utilização

* A execução do programa é com o commando: ```python app.py``` que inicializa o website, acessível em http://localhost:5000.


## Descrição

Aplicação web que expõe os grupos e elementos da tabela periódica.

Esta aplicação web tem 5 páginas:

* **/index.html** : página inicial ao visitar o endereço que expõe os os links para as páginas **/groups** e **/elements**.

* **/groups** : enumera os grupos da tabela periódica com o seu número e o nome correspondente, sendo que o nome é opcional. Ao clicar num grupo, é redirecionado para a página do grupo em questão (**/group/\<int:ng>**).

* **/group/\<int:ng>** : enumera todos os elementos que pertencem ao grupo em questão, identificado pelo seu número. Ao clicar num elemento, é redirecionado para do elemento em questão (**/element/\<int:na>**).

* **/elements** : enumera os elementos da tabela periódica com o seu número atómico, nome, símbolo e grupo, sendo que elementos não pertencem a um grupo. Ao clicar num elemento é redirecionado para do elemento em questão (**/element/\<int:na>**), mas ao clicar na coluna do grupo de um elemento, é redirecionado para a página do grupo em questão (**/group/\<int:ng>**).

* **/element/\<int:na>** : mostra a informação relativa ao elemento selecionado identificado pelo número atómico. Ao clicar na coluna do grupo do elemento, é redirecionado para a página do grupo em questão (**/group/\<int:ng>**).

