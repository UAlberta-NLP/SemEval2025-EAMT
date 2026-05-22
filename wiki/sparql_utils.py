import time
import requests

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
RATE_LIMIT_DELAY = 1  # seconds between requests


def sparql_get(query: str) -> list[dict]:
    """Execute a SPARQL SELECT query and return result bindings."""
    response = requests.get(SPARQL_ENDPOINT, params={"query": query, "format": "json"})
    response.raise_for_status()
    time.sleep(RATE_LIMIT_DELAY)
    return response.json().get("results", {}).get("bindings", [])


def fetch_label(entity_id: str, language: str) -> list[str]:
    """Return rdfs:label values for a Wikidata entity in the given language."""
    query = f"""
    SELECT ?label WHERE {{
      wd:{entity_id} rdfs:label ?label .
      FILTER (lang(?label) = "{language}")
    }}
    """
    return [r["label"]["value"] for r in sparql_get(query) if "label" in r]


def fetch_label_and_aliases(entity_id: str, language: str) -> tuple[list[str], list[str], str | None]:
    """Return (labels, aliases, english_name) for a Wikidata entity."""
    query = f"""
    SELECT ?label ?alias ?entityLabel WHERE {{
      wd:{entity_id} rdfs:label ?label .
      OPTIONAL {{ wd:{entity_id} skos:altLabel ?alias FILTER(lang(?alias) = "{language}") }}
      OPTIONAL {{ wd:{entity_id} rdfs:label ?entityLabel FILTER(lang(?entityLabel) = "en") }}
      FILTER (lang(?label) = "{language}")
    }}
    """
    results = sparql_get(query)
    labels = list({r["label"]["value"] for r in results if "label" in r})
    aliases = list({r["alias"]["value"] for r in results if "alias" in r})
    en_label = next((r["entityLabel"]["value"] for r in results if "entityLabel" in r), None)
    return labels, aliases, en_label


def search_entity(name: str, language: str = "en") -> str | None:
    """Look up a Wikidata entity ID by its label. Returns the Q-ID or None."""
    query = f"""
    SELECT ?entity WHERE {{
      ?entity rdfs:label "{name}"@{language} .
    }} LIMIT 1
    """
    results = sparql_get(query)
    return results[0]["entity"]["value"].split("/")[-1] if results else None


def search_entity_with_label(name: str) -> tuple[str, str] | None:
    """Look up a Wikidata entity by English label. Returns (item_label, Q-ID) or None."""
    query = f"""
    SELECT ?item ?itemLabel WHERE {{
      ?item rdfs:label "{name}"@en.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    LIMIT 1
    """
    results = sparql_get(query)
    if not results:
        return None
    try:
        import re
        item_uri = results[0]["item"]["value"]
        item_label = results[0]["itemLabel"]["value"]
        entity_id = re.search(r"Q\d+", item_uri).group(0)
        return item_label, entity_id
    except (KeyError, IndexError, AttributeError):
        return None
