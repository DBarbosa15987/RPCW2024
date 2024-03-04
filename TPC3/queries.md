## Quantas cidades se podem atingir a partir do Porto? (diretamente)

```
select (count( distinct ?destinos) as ?n) where {
    ?cidades :distrito "Porto" .
    ?lig :tem_origem ?cidades.
    ?lig :tem_destino ?destinos.
}
```

## Quais as cidades de um determinado distrito? (neste caso Braga)

```
select ?cidades ?nomes where {
	
	?cidades :distrito "Braga".
    ?cidades :nome ?nomes.

}
```

## Distribuição de cidades por distrito?

```

select ?distrito (count(?cidades) as ?nCidades) where {
	
	?cidades :distrito ?distrito.
    
} group by ?distrito

```

## Quais as cidades com população acima de um determinado valor? (neste caso 500 000)

```
select ?nomes ?pop where {
	
    ?cidades a :Cidade.
    ?cidades :populacao ?pop.
    filter(?pop>500000).
    ?cidades :nome ?nomes.
} 
```