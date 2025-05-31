# Quantos triplos existem na Ontologia?

```
Select (count(*) as ?n) where{
    ?s ?p ?o.
}
```
6603

# Que classes estão definidas?

```
SELECT DISTINCT ?class WHERE {
   ?class a owl:Class 
}
```
102 classes

# Que propriedades tem a classe "Rei"?

```
prefix : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

SELECT distinct ?prop WHERE {
  ?s a :Rei .
  ?s ?prop ?o .
}
```
16 propriedades

# Quantos reis aparecem na ontologia?
```
prefix : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

Select (count(?s) as ?n) where{
    ?s a :Rei.
}
```
32


# Calcula uma tabela com o seu nome, data de nascimento e cognome.
```
prefix : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

Select ?n ?d ?cgn where{
    ?s a :Rei;
       :nome ?n;
       :nascimento ?d;
       :cognomes ?cgn .
}
```

# Acrescenta à tabela anterior a dinastia em que cada rei reinou.
```
prefix : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

Select ?n ?d ?cgn ?dnome where{
    ?s a :Rei;
       :nome ?n;
       :nascimento ?d;
       :cognomes ?cgn .
    ?reinado :temMonarca ?s;
             :dinastia ?dinastia .
    ?dinastia :nome ?dnome .
}
```

# Qual a distribuição de reis pelas 4 dinastias?
```
Select ?dinastia (count(?monarca) as ?nmonarca) where{
    ?monarca a :Rei .
    ?monarca :temReinado/:dinastia ?dinastia
}
group by ?dinastia 
```
4 dinastias

#  Lista os descobrimentos (sua descrição) por ordem cronológica.
```
select ?d ?desc ?data where{
    ?d a :Descobrimento;
        :notas ?desc;
        :data ?data .
}
order by ?data
```

# Lista as várias conquistas, nome e data, juntamento com o nome que reinava no momento.
```
prefix : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

Select distinct ?conquista ?data ?reinado Where { 
 ?s a :Conquista .
 ?s :nome ?conquista.
 ?s :data ?data .
 ?s :temReinado ?temReinado .
 ?temReinado :temMonarca ?rei .
 ?rei :nome ?reinado . 
}
```

# Calcula uma tabela com o nome, data de nascimento e número de mandatos de todos os presidentes portugueses.
```
prefix : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?n ?d (count(?mandato) as ?nmandato) where{
    ?p a :Presidente;
        :nome ?n;
        :nascimento ?d;
        :mandato ?mandato .
}
group by ?p ?n ?d
```

# Quantos mandatos teve o presidente Sidónio Pais? Em que datas iniciaram e terminaram esses mandatos?
```
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

SELECT ?nome (COUNT(?mandato) AS ?total) ?começo ?fim WHERE {
  ?p a :Presidente .
  ?p :nome ?nome .
  ?p :mandato ?mandato .
  ?mandato :comeco ?começo .
  ?mandato :fim ?fim .
	
  FILTER(REGEX(?nome, "^Sidónio( [A-Z][a-z]*)* Pais$", "i"))
}
GROUP BY ?nome ?começo ?fim
```
2

# Quais os nomes dos partidos políticos presentes na ontologia?
```
prefix : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

SELECT  ?nome (COUNT(?militante) AS ?total) WHERE {
  ?p a :Partido .
  ?p :temMilitante ?militante .
  ?p :nome ?nome
}
GROUP BY ?nome
```

# Qual a distribuição dos militantes por cada partido político?
```
prefix : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

SELECT  ?nome (COUNT(?militante) AS ?total) WHERE {
  ?p a :Partido .
  ?p :temMilitante ?militante .
  ?p :nome ?nome
}
GROUP BY ?nome
```

# Qual o partido com maior número de presidentes militantes?
```
prefix : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

SELECT ?nome (COUNT(?militante) AS ?total) WHERE {
  ?p a :Partido .
  ?p :temMilitante ?militante .
  ?p :nome ?nome
}
GROUP BY ?nome
ORDER BY DESC(?total)
LIMIT 1
```
Independente com 4