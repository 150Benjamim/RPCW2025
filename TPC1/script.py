import json

def format_individual_name(name):
    return name.strip().replace(" ", "_").replace('"', '').replace("'", "")

def bool_to_xsd(value):
    return "true" if value else "false"

def gerar_ttl_semanticamente(dados_emd, prefixo_iri="http://www.example.org/emd#"):
    ttl = []

    # Prefixos
    ttl.append(f"@prefix : <{prefixo_iri}> .")
    ttl.append("@prefix owl: <http://www.w3.org/2002/07/owl#> .")
    ttl.append("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
    ttl.append("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
    ttl.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")

    # Declaração de classes
    ttl.append("# Declarações de classes")
    ttl.extend([
        ":Atleta a owl:Class .",
        ":Genero a owl:Class .",
        ":Clube a owl:Class .",
        ":Modalidade a owl:Class .",
        ":Morada a owl:Class .\n"
    ])

    # Propriedades objetuais
    ttl.append("# Propriedades objetuais")
    ttl.extend([
        ":temGenero a owl:ObjectProperty ; rdfs:domain :Atleta ; rdfs:range :Genero .",
        ":temModalidade a owl:ObjectProperty ; rdfs:domain :Atleta ; rdfs:range :Modalidade .",
        ":pertenceAClube a owl:ObjectProperty ; rdfs:domain :Atleta ; rdfs:range :Clube .",
        ":temMorada a owl:ObjectProperty ; rdfs:domain :Atleta ; rdfs:range :Morada .\n"
    ])

    # Propriedades literais
    ttl.append("# Propriedades literais")
    ttl.extend([
        ":temIdade a owl:DatatypeProperty ; rdfs:domain :Atleta ; rdfs:range xsd:integer .",
        ":temEmail a owl:DatatypeProperty ; rdfs:domain :Atleta ; rdfs:range xsd:string .",
        ":temDataEMD a owl:DatatypeProperty ; rdfs:domain :Atleta ; rdfs:range xsd:date .",
        ":éFederado a owl:DatatypeProperty ; rdfs:domain :Atleta ; rdfs:range xsd:boolean .",
        ":temResultado a owl:DatatypeProperty ; rdfs:domain :Atleta ; rdfs:range xsd:boolean .\n"
    ])

    # Conjuntos para evitar duplicação
    generos, modalidades, clubes, moradas = set(), set(), set(), set()

    for atleta in dados_emd:
        nome_completo = f"{atleta['nome']['primeiro']}_{atleta['nome']['último']}"
        atleta_id = format_individual_name(nome_completo)
        genero_id = format_individual_name(atleta["género"])
        modalidade_id = format_individual_name(atleta["modalidade"])
        clube_id = format_individual_name(atleta["clube"])
        morada_id = format_individual_name(atleta["morada"])

        ttl.append(f":{atleta_id} a :Atleta ;")
        ttl.append(f"    :temIdade \"{atleta['idade']}\"^^xsd:integer ;")
        ttl.append(f"    :temEmail \"{atleta['email']}\"^^xsd:string ;")
        ttl.append(f"    :temDataEMD \"{atleta['dataEMD']}\"^^xsd:date ;")
        ttl.append(f"    :éFederado \"{bool_to_xsd(atleta['federado'])}\"^^xsd:boolean ;")
        ttl.append(f"    :temResultado \"{bool_to_xsd(atleta['resultado'])}\"^^xsd:boolean ;")
        ttl.append(f"    :temGenero :{genero_id} ;")
        ttl.append(f"    :temModalidade :{modalidade_id} ;")
        ttl.append(f"    :pertenceAClube :{clube_id} ;")
        ttl.append(f"    :temMorada :{morada_id} .\n")

        generos.add(genero_id)
        modalidades.add(modalidade_id)
        clubes.add(clube_id)
        moradas.add(morada_id)

    # Indivíduos auxiliares
    ttl.append("# Indivíduos de Genero")
    for g in generos:
        ttl.append(f":{g} a :Genero .")

    ttl.append("\n# Indivíduos de Modalidade")
    for m in modalidades:
        ttl.append(f":{m} a :Modalidade .")

    ttl.append("\n# Indivíduos de Clube")
    for c in clubes:
        ttl.append(f":{c} a :Clube .")

    ttl.append("\n# Indivíduos de Morada")
    for mor in moradas:
        ttl.append(f":{mor} a :Morada .")

    return '\n'.join(ttl)

# Ler JSON
with open('emd.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

# Gerar TTL
ttl_output = gerar_ttl_semanticamente(dados)

# Escrever ficheiro
with open('emd.ttl', 'w', encoding='utf-8') as f:
    f.write(ttl_output)

print("Ficheiro TTL gerado com sucesso.")
