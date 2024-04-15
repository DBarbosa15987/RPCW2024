# Queries

* Quantos alunos estão registados? (inteiro)

```
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

select (count(?aluno) as ?count) where{

    ?aluno a :Aluno.

}
```

* Quantos alunos frequentam o curso "LCC"? (inteiro)

```
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

select (count(?aluno) as ?count) where{

    ?aluno a :Aluno.
    ?aluno :curso "LCC".

}
```

* Que alunos tiveram nota positiva no exame de época normal? (lista ordenada alfabeticamente por nome com: idAluno, nome, curso, nota do exame);

```
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

select ?idAluno ?nome ?curso ?nota where{

    ?aluno a :Aluno.
    ?exame :epoca "normal".
    ?exame :notaExame ?nota.
    FILTER(?nota>=10).
    
    ?aluno :tem_exame ?exame.
    ?aluno :idAluno ?idAluno.
    ?aluno :nome ?nome.
    ?aluno :curso ?curso.
    
}order by desc(?nome)
```

* Qual a distribuição dos alunos pelas notas do projeto? (lista com: nota e número de alunos que obtiveram essa nota)

```
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

select ?notaProjeto (COUNT(?aluno) as ?nAlunos) where{

    ?aluno a :Aluno.
    ?aluno :tem_projeto ?projeto.
    ?projeto :notaProjeto ?notaProjeto.
    
}group by (?notaProjeto)
```


* Quais os alunos mais trabalhadores durante o semestre? (lista ordenada por ordem decrescente do total: idAluno, nome, curso, total = somatório dos resultados dos TPC)

```
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

select ?id ?nome ?curso (SUM(?notaTPC) as ?soma) where{

    ?aluno a :Aluno.
    ?aluno :idAluno ?id.
    ?aluno :tem_tpc ?tpc.
    ?aluno :nome ?nome.
    ?aluno :curso ?curso.
    ?tpc :notaTPC ?notaTPC.
    
}group by ?id ?nome ?curso
order by desc(?soma)
```


* Qual a distribuição dos alunos pelos vários cursos? (lista de cursos, ordenada alfabeticamente, por curso, com: curso, número de alunos nesse curso)

```
PREFIX : <http://rpcw.di.uminho.pt/2024/alunos/>

select ?curso (COUNT(?aluno) as ?nAlunos) where{

    ?aluno a :Aluno.
    ?aluno :curso ?curso.
    
}group by ?curso
order by ?curso
```
