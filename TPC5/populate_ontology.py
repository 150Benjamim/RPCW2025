import json
from rdflib import Graph, Namespace, URIRef, Literal, RDF, XSD
from rdflib.namespace import RDFS, FOAF # FOAF for foaf:name
import re

CINE = Namespace("http://www.semanticweb.org/ontologies/2025/5/cinema#")

def sanitize_for_uri(text):
    """
    Replaces spaces and special characters to create a safe string for a URI.
    """
    if not text:
        return "unknown"
    # Remove or replace special characters. Keep it simple for this example.
    text = re.sub(r'[^\w\s-]', '', str(text)) # Keep alphanumeric, spaces, hyphens
    text = re.sub(r'\s+', '_', text) # Replace spaces with underscores
    return text

def populate_ontology_from_dataset(dataset_file="cinema_dataset.json", output_ontology_file="cinema.ttl"):
    """
    Loads film data from a JSON file, defines a simple ontology,
    populates it, and saves it to a Turtle file.
    """
    try:
        with open(dataset_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Dataset file '{dataset_file}' not found.")
        print("Please run tpc5_build_dataset.py first to generate the dataset.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{dataset_file}'.")
        return

    films_data = data.get("films", [])
    metadata = data.get("metadata", {})
    
    print(f"Loaded {metadata.get('total_films', len(films_data))} films from '{dataset_file}'.")
    print("Starting ontology definition and population...")

    # --- Initialize RDF Graph ---
    g = Graph()
    g.bind("cine", CINE)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("foaf", FOAF) # For foaf:name

    # --- Define Ontology Classes ---
    # cine:Film
    g.add((CINE.Film, RDF.type, RDFS.Class))
    g.add((CINE.Film, RDFS.label, Literal("Film")))
    g.add((CINE.Film, RDFS.comment, Literal("Represents a motion picture.")))

    # cine:Person
    g.add((CINE.Person, RDF.type, RDFS.Class))
    g.add((CINE.Person, RDFS.label, Literal("Person")))
    g.add((CINE.Person, RDFS.comment, Literal("Represents a person involved in cinema.")))

    # cine:Director (as a type of cine:Person)
    g.add((CINE.Director, RDF.type, RDFS.Class))
    g.add((CINE.Director, RDFS.subClassOf, CINE.Person)) # Director is a cine:Person
    g.add((CINE.Director, RDFS.label, Literal("Director")))
    g.add((CINE.Director, RDFS.comment, Literal("Represents a film director.")))
    
    # --- Define Ontology Properties ---
    # Object Properties
    g.add((CINE.hasDirector, RDF.type, RDF.Property))
    g.add((CINE.hasDirector, RDFS.label, Literal("has director")))
    g.add((CINE.hasDirector, RDFS.domain, CINE.Film))
    g.add((CINE.hasDirector, RDFS.range, CINE.Director))

    # Data Properties for Film
    film_properties = {
        "title": (FOAF.name, XSD.string, "The title of the film."), # Using foaf:name for title
        "releaseYear": (CINE.releaseYear, XSD.gYear, "The release year of the film."),
        "releaseDate": (CINE.releaseDate, XSD.date, "The full release date of the film."),
        "description": (CINE.description, XSD.string, "A short description or abstract of the film."),
        "budget": (CINE.budget, XSD.decimal, "The budget of the film."), # Using decimal for currency
        "grossRevenue": (CINE.grossRevenue, XSD.decimal, "The gross revenue of the film."),
        "imdbId": (CINE.imdbId, XSD.string, "The IMDB identifier for the film."),
        "dbpediaUri": (CINE.dbpediaUri, XSD.anyURI, "The DBpedia URI for the film.")
    }

    for prop_name, (prop_uri, prop_range, prop_comment) in film_properties.items():
        g.add((prop_uri, RDF.type, RDF.Property)) # Some might be RDF.DatatypeProperty, but RDF.Property is fine
        g.add((prop_uri, RDFS.label, Literal(prop_name)))
        g.add((prop_uri, RDFS.comment, Literal(prop_comment)))
        g.add((prop_uri, RDFS.domain, CINE.Film))
        g.add((prop_uri, RDFS.range, prop_range))

    # --- Populate Ontology from Dataset ---
    populated_count = 0
    director_uris = {} # To store and reuse director URIs

    for film_data in films_data:
        # Create Film Instance URI from DBPedia URI
        # Using the last part of the DBPedia URI as the local name for the film instance
        film_local_name = film_data['dbpedia_uri'].split('/')[-1]
        film_instance = CINE[sanitize_for_uri(film_local_name)] # film_instance = CINE[film_local_name]
        
        g.add((film_instance, RDF.type, CINE.Film))

        # Add Film Data Properties
        if film_data.get('title'):
            g.add((film_instance, FOAF.name, Literal(film_data['title'], datatype=XSD.string)))
        if film_data.get('release_year'):
            g.add((film_instance, CINE.releaseYear, Literal(str(film_data['release_year']), datatype=XSD.gYear)))
        if film_data.get('release_date'):
            try:
                g.add((film_instance, CINE.releaseDate, Literal(film_data['release_date'], datatype=XSD.date)))
            except ValueError:
                print(f"Warning: Could not parse date '{film_data['release_date']}' for film '{film_data.get('title')}'. Skipping date property.")
        if film_data.get('description'):
            g.add((film_instance, CINE.description, Literal(film_data['description'], datatype=XSD.string)))
        if film_data.get('budget'):
            try:
                g.add((film_instance, CINE.budget, Literal(float(film_data['budget']), datatype=XSD.decimal)))
            except (ValueError, TypeError):
                 print(f"Warning: Could not parse budget '{film_data['budget']}' for film '{film_data.get('title')}'. Skipping budget.")
        if film_data.get('gross_revenue'):
            try:
                g.add((film_instance, CINE.grossRevenue, Literal(float(film_data['gross_revenue']), datatype=XSD.decimal)))
            except (ValueError, TypeError):
                print(f"Warning: Could not parse gross_revenue '{film_data['gross_revenue']}' for film '{film_data.get('title')}'. Skipping gross_revenue.")
        if film_data.get('imdb_id'):
            g.add((film_instance, CINE.imdbId, Literal(film_data['imdb_id'], datatype=XSD.string)))
        if film_data.get('dbpedia_uri'):
            g.add((film_instance, CINE.dbpediaUri, Literal(film_data['dbpedia_uri'], datatype=XSD.anyURI)))

        # Handle Director
        director_name_str = film_data.get('director')
        if director_name_str:
            director_sanitized_name = sanitize_for_uri(director_name_str)
            if director_sanitized_name not in director_uris:
                director_instance = CINE[f"Director_{director_sanitized_name}"]
                director_uris[director_sanitized_name] = director_instance
                g.add((director_instance, RDF.type, CINE.Director)) # Instance of Director
                # Directors (as cine:Person) will use foaf:name
                g.add((director_instance, FOAF.name, Literal(director_name_str, datatype=XSD.string)))
            else:
                director_instance = director_uris[director_sanitized_name]
            
            # Link Film to Director
            g.add((film_instance, CINE.hasDirector, director_instance))
        
        populated_count += 1
        if populated_count % 50 == 0: # Print progress every 50 films
            print(f"  Processed {populated_count} films...")

    print(f"\nFinished processing {populated_count} films for ontology population.")

    # --- Serialize Graph to File ---
    try:
        g.serialize(destination=output_ontology_file, format="turtle")
        print(f"Populated ontology successfully saved to '{output_ontology_file}'")
    except Exception as e:
        print(f"Error serializing ontology: {e}")

if __name__ == "__main__":
    # Ensure tpc5_build_dataset.py has been run successfully first to create cinema_dataset.json
    populate_ontology_from_dataset()
