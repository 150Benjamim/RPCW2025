import requests
import json
from datetime import datetime
import re

def query_dbpedia(endpoint_url, query):
    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(endpoint_url, params={'query': query}, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f'Query failed. Returned code: {response.status_code}. {response.text}')

def extract_year(date_str):
    """Extract year from date string"""
    if not date_str:
        return None
    try:
        # Try to parse different date formats
        if '-' in str(date_str):
            return int(str(date_str)[:4])
        elif len(str(date_str)) == 4:
            return int(date_str)
    except (ValueError, TypeError):
        pass
    return None

def clean_uri_to_name(uri):
    """Convert DBpedia URI to readable name"""
    if not uri:
        return None
    if 'dbpedia.org/resource/' in uri:
        name = uri.split('/')[-1].replace('_', ' ')
        return name
    return uri

def build_cinema_dataset():
    # Endpoint SPARQL da DBpedia
    endpoint = "https://dbpedia.org/sparql"

    sparql_query = """
    SELECT DISTINCT ?film ?title ?director ?directorName ?releaseDate ?abstract ?budget ?gross ?imdbId WHERE {
      ?film a dbo:Film ;
            rdfs:label ?title ;
            dbo:director ?director ;
            dbo:releaseDate ?releaseDate .
      
      ?director rdfs:label ?directorName .
      
      OPTIONAL { ?film dbo:abstract ?abstract . }
      OPTIONAL { ?film dbo:budget ?budget . }
      OPTIONAL { ?film dbo:gross ?gross . }
      OPTIONAL { ?film dbo:imdbId ?imdbId . }
      
      FILTER (lang(?title) = 'en')
      FILTER (lang(?directorName) = 'en')
      FILTER (lang(?abstract) = 'en')
      FILTER (?releaseDate >= "1990-01-01"^^xsd:date)  # Focus on more recent films
    } 
    ORDER BY DESC(?releaseDate)
    LIMIT 750
    """

    print("Querying DBpedia to build cinema dataset...")
    results = query_dbpedia(endpoint, sparql_query)

    # Transform results with better data cleaning
    parsed_results = []
    seen_films = set()  # To avoid duplicates

    for result in results["results"]["bindings"]:
        def get_value(field):
            return result[field]["value"] if field in result else None
        
        film_uri = get_value("film")
        title = get_value("title")
        
        # Skip duplicates based on film URI
        if film_uri in seen_films:
            continue
        seen_films.add(film_uri)
        
        # Extract and clean data
        director_name = get_value("directorName")
        release_date = get_value("releaseDate")
        abstract = get_value("abstract")
        budget = get_value("budget")
        gross = get_value("gross")
        imdb_id = get_value("imdbId")
        
        # Clean and process data
        release_year = extract_year(release_date)
        
        # Only include films with essential data
        if title and director_name and release_year:
            film_data = {
                "title": title,
                "director": director_name,
                "release_year": release_year,
                "release_date": release_date,
                "budget": budget,
                "gross_revenue": gross,
                "imdb_id": imdb_id,
                "description": abstract[:500] + "..." if abstract and len(abstract) > 500 else abstract,
                "dbpedia_uri": film_uri
            }
            
            # Remove None values to keep JSON clean
            film_data = {k: v for k, v in film_data.items() if v is not None}
            parsed_results.append(film_data)

    print(f"Collected {len(parsed_results)} films with quality data.")

    # Save to JSON file with better formatting
    output_file = "cinema_dataset.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "total_films": len(parsed_results),
                "generated_on": datetime.now().isoformat(),
                "source": "DBpedia SPARQL endpoint",
                "description": "Cinema dataset with films from 1990 onwards, aiming for 500 entries."
            },
            "films": parsed_results
        }, f, ensure_ascii=False, indent=2)

    print(f"Dataset saved to {output_file}")
    print(f"This file contains {len(parsed_results)} films. You can now use tpc6_populate_ontology.py to process it.")

if __name__ == "__main__":
    build_cinema_dataset()