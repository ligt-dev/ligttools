from dataclasses import dataclass
from os.path import exists

import requests

# def search(query_args, datasets):
#     endpoints = [ds.url for ds in datasets if ds.is_sparql]

def test_endpoint(url):
    params = { 'query': 'ASK { ?s ?p ?o }' }
    headers = {'Accept': 'application/sparql-results+json' }
    r = requests.get(url, headers=headers, params=params)
    return r.status_code == 200 and 'application/sparql-results+json' in r.headers.get('Content-Type', '')

@dataclass
class QueryArg:
    label: str | None = None
    gloss: str | None = None
    is_uri: bool = False

    @classmethod
    def from_token(cls, token: str) -> 'QueryArg':
        """Parse a token into a QueryArg object."""

        if not ':' in token:
            # If a user specified only one string, treat it as a gloss
            token = f"{token}:"
        label, gloss = token.split(':', 1)
        is_uri = gloss.startswith('http') or (gloss.startswith('<') and gloss.endswith('>'))
        if is_uri:
            gloss = gloss.strip('<>')

        return cls(label, gloss, is_uri)

    def to_sparql(self, var="morph") -> str:
        gloss = f"URI(\"{self.gloss}\")" if self.is_uri else f"\"{self.gloss}\""
        statements = [f"?{var} a ligt:Morph"]
        filters = []

        if self.label:
            statements.append(f"rdfs:label ?lab_{var}")
            filters.append(f"STR(?lab_{var})=\"{self.label}\"")
        if self.gloss:
            statements.append(f"ligt:gloss ?gl_{var}")
            if not self.is_uri:
                filters.append(f"STR(?gl_{var})={gloss}")

        mapping = (f"\nBIND(STR(?gl_{var}) AS ?gl_{var}_no_lang)\n"
                   f"<{self.gloss}> skos:notation ?gl_{var}_no_lang .") if self.gloss and self.is_uri else ""
        return ' ; '.join(statements) + " ." + (f" FILTER({' && '.join(filters)})" if filters else "") + mapping

@dataclass
class Dataset:
    url: str
    is_sparql: bool = False

    @classmethod
    def from_string(cls, s: str) -> 'Dataset | None':
        """Parse a string into a Dataset object."""
        if not s.startswith('http'):
            return cls(s, is_sparql=False) if exists(s) else None
        try:
            is_sparql = test_endpoint(s)
        except requests.exceptions.RequestException as e:
            print(f"Network Error: {e}")
            return None

        return cls(s, is_sparql=is_sparql)
