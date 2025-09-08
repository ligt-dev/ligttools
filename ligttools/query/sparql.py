from rdflib import Graph
from oxrdflib import OxigraphStore

from ligttools.query import QueryArg, Dataset


def prepare_query(query_args: list[QueryArg], endpoint: str = None):
    conditions = []
    for i, arg in enumerate(query_args):
        name = f"m{i+1}"
        conditions.append(f"?utt a ligt:Utterance ; ligt:hasMorphs/ligt:item ?{name} . \n" + arg.to_sparql(name))

    endpoint = f"SERVICE <{endpoint}>" if endpoint else ""
    query = f"""
PREFIX ligt: <http://purl.org/ligt/ligt-0.3#> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?utt ?label ?translation
WHERE {{
{endpoint}
{{
?utt rdfs:label ?label ; ligt:translation ?translation .
""" + "\n".join(conditions) + "\n}\n}"

    # for arg in query_args:
    #     print(arg, arg.to_sparql())
    return query

def get_utterance(g, utt_uri):
    query = f"""
PREFIX ligt: <http://purl.org/ligt/ligt-0.3#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?utt ?word ?morph ?translation
WHERE {{
{utt_uri} a ligt:Utterance ; 
ligt:hasWords ?words .
}}""" % utt_uri
    res = g.query(query)
    print(res)

    return res

def create_graph(datasets: list[Dataset]):
    g = Graph(store=OxigraphStore())
    for dataset in datasets:
        if not dataset.is_sparql:
            print(f"Loading triples from {dataset.url}...")
            g.parse(dataset.url)
    print("All datasets loaded.")
    return g

def get_results(g: Graph, endpoints: list[str], query_args: list[QueryArg]):
    rows = []
    for endpoint in [None] + endpoints:
        print(f"Searching in  {endpoint if endpoint else 'RDF files'}")
        query = prepare_query(query_args, endpoint)
        res = g.query(query)
        print(f"Found {len(res)} examples")
        rows.extend([f"{row.utt}\t{row.label}\t{row.translation}" for row in res])
    print(f"Total {len(rows)} examples found")
    return rows