"""
CLDF to Ligt converter
"""

import logging
from pathlib import Path
from typing import Union, Optional
import tempfile

import requests
import pycldf

import rdflib
from rdflib.namespace import RDF, RDFS, OWL, DCTERMS
from rdflib.term import URIRef, Literal

from ligttools.converters.base import BaseConverter

PROPERTIES = {'dc:bibliographicCitation', 'dc:title', 'dc:description', 'dc:contributor'}

def align_glosses(morphs, glosses, example):
    if len(morphs) != len(glosses):
        print("Unaligned glosses:", morphs, glosses, example)
    return list(zip(morphs, glosses))

def split_morphs(gloss):
    morphs = gloss[0].split('-') if gloss and len(gloss) > 0 and gloss[0] else []
    glosses = gloss[1].split('-') if gloss and len(gloss) > 1 and gloss[1] else []

    if len(morphs) == len(glosses) and len(glosses) > 1:
        return list(zip(morphs, glosses))

    return [gloss]

def igt_well_formed(word):
    # For now, we check for the malformed examples where word separation is within a token
    # Additional replaces are a hack to correctly handle glossing like ["morph- morph"]
    # which is sometimes used in books
    return word and not any(' ' in morph.replace('- ', '-').replace('- ', '-') for morph in word)

class CLDFConverter(BaseConverter):
    """Converter for CLDF format."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        with open('glottolog-codes.txt') as inp_file:
            self._glottolog_codes = {
                line.split("\t")[0]: line.split("\t")[1].strip() for line in inp_file
            }

    def to_rdf(self, input_data: Union[str, Path], output_path: Optional[Path] = None, serialization='ttl') -> Union[str, rdflib.graph.Graph, None]:
        """
        Convert a CLDF dataset to Ligt.
        If output_path is provided, writes the Ligt RDF to a file, otherwise returns it as a string.
        Input can point to a metadata file or directly to the examples table.

        Args:
            input_data: CSV data to convert. Can be a local file path or a URL.
            output_path: Optional path to write the output to. If not provided, returns the result as a string.
            serialization: RDF serialization for the output.
            If both output_path and serialization are None, the dataset is returned as rdflib.Graph object

        Returns:
            None if output_path is None, otherwise RDF in a specified serialization (defaults to Turtle) or as a graph object.
        """

        input_is_data = str(input_data).endswith('.csv')
        input_is_url = str(input_data).startswith(('http://', 'https://'))

        if not input_is_url:
            input_data = Path(input_data).expanduser().resolve()
        dataset_ns = f"{input_data}#" if input_is_url else f"file://{input_data}#"

        # pycldf can only load remote metadata, not data
        # so we download the file and save it as a temporary file in case it is a remote examples.csv
        if input_is_url and input_is_data:
            try:
                response = requests.get(input_data)
                response.raise_for_status()

                # Save the content as examples.csv to a temporary directory
                temp_dir = tempfile.TemporaryDirectory()
                file_path = Path(temp_dir.name) / 'examples.csv'
                with open(file_path, 'wb') as f:
                    f.write(response.content)

                # Update input_data to point to the temporary file
                input_data = Path(file_path)
            except requests.RequestException as e:
                raise ValueError(f"Failed to download CSV file from URL: {e}")
        try:
            cldf_dataset = pycldf.Dataset.from_data(input_data) if input_is_data else pycldf.Dataset.from_metadata(
                input_data)
        except (FileNotFoundError, ValueError, UnicodeDecodeError) as e:
            raise ValueError(f"Failed to load CLDF dataset: {e}")

        ligt_dataset = self._make_graph(cldf_dataset, uri=dataset_ns)

        if not serialization or serialization == 'ttl':
            serialization = 'turtle'
        if not output_path:
            return ligt_dataset if not serialization else ligt_dataset.serialize(format=serialization)
        else:
            with open(output_path, 'w') as f:
                f.write(ligt_dataset.serialize(format=serialization))

    def from_rdf(self, input_data, output_path=None, serialization='ttl'):
        """
        Convert a Ligt RDF dataset to CLDF.
        :param input_data: Ligt RDF dataset. Must be a local or remote file.
        :param output_path: Optional path to write the output to. If not provided, returns the result as a string.
        :param serialization: RDF serialization for the output. Turtle by default.
        :return: CLDF dataset with a single ExampleTable.
        """
        if not serialization or serialization == 'ttl':
            serialization = 'turtle'

        self.logger.info(f"Parsing {input_data}...")
        try:
            g = rdflib.Graph()
            g.parse(input_data, format=serialization)
        # TODO: Make a specific list
        except Exception as e:
            raise ValueError(f"Failed to parse RDF file: {e}")

        ligt = rdflib.Namespace('http://purl.org/ligt/ligt-0.3#')
        glottolog = rdflib.Namespace('http://glottolog.org/resource/languoid/id/')

        g.bind('ligt', ligt)

    def get_iso_code(self, glottocode):
        glottolog_uri = f'http://glottolog.org/resource/languoid/id/{glottocode}'
        return self._glottolog_codes.get(glottolog_uri)


    def _make_graph(self, cldf_dataset, uri: str) -> rdflib.graph.Graph:
        g = rdflib.Graph(identifier=uri)
        ns = rdflib.Namespace(uri)
        doc = rdflib.URIRef(uri)

        ligt = rdflib.Namespace('http://purl.org/ligt/ligt-0.3#')
        glottolog = rdflib.Namespace('http://glottolog.org/resource/languoid/id/')

        g.bind('ligt', ligt)
        g.bind('glottolog', glottolog)
        g.bind('data', doc)


        g.set((doc, RDF.type, ligt.Document))
        g.set((doc, ligt.hasUtterances, ns.examples))

        g.set((ns.examples, RDF.type, ligt.InterlinearCollection))

        for prop in PROPERTIES:
            if prop in cldf_dataset.properties:
                g.set((ns.examples, RDFS.comment, Literal(cldf_dataset.properties[prop], lang="en")))

        examples = [{'id': example['ID'],
                     'baseline': example.get('Primary_Text'),
                     'glosses': align_glosses(example.get('Analyzed_Word'), example.get('Gloss'), example),
                     'translation': example.get('Translated_Text'),
                     'language': example.get("Language_ID", "unk"), #languages.get(example.get('Language_ID'), {"Glottocode": example.get('Language_ID')}),
                     'meta_language': example.get('Meta_Language_ID'),
                     'comment': example.get('Comment')
                     } for example in cldf_dataset['ExampleTable'] if
                    igt_well_formed(example.get("Analyzed_Word"))]

        for example in examples:
            lang_tag = self.get_iso_code(example['language']) or "unk"
            lang_uri = glottolog + URIRef(example['language'])

            meta_lang = self.get_iso_code(example["meta_language"]) or "en"

            # Utterance node
            ex = ns + URIRef(f"ex_{example['id']}")
            g.add((ns.examples, ligt.subSegment, ex))

            # Utterance properties
            g.add((ex, RDF.type, ligt.Utterance))
            g.add((ex, RDFS.label, Literal(example['baseline'], lang=lang_tag)))
            if example['comment']:
                g.add((ex, RDFS.comment, Literal(example['comment'], lang=meta_lang)))
            g.add((ex, ligt.translation, Literal(example['translation'], lang=meta_lang)))

            # Utterance metadata
            g.add((ex, DCTERMS.language, lang_uri))

            # Tiers
            ex_tier_phrase = URIRef('{}_tier_phrase'.format(ex))
            ex_tier_morphs = URIRef('{}_tier_morphs'.format(ex))
            ex_tier_words = URIRef('{}_tier_words'.format(ex))

            g.add((ex, ligt.hasTier, ex_tier_phrase))
            g.add((ex, ligt.hasMorphs, ex_tier_morphs))
            g.add((ex, ligt.hasWords, ex_tier_words))

            # Phrase
            phrase = URIRef('{}_item_phrase_1'.format(ex))
            g.add((ex_tier_phrase, RDF.type, ligt.Tier))
            g.add((ex_tier_phrase, ligt.item, phrase))

            # Glosses

            if len(example['glosses']):
                next_word = URIRef('{}_item_word_{}'.format(ex, 1))

            for i, gloss in enumerate(example['glosses']):
                word = next_word
                next_word = URIRef('{}_item_word_{}'.format(ex, i + 2)) if i < len(example['glosses']) - 1 else None

                g.add((ex_tier_words, ligt.item, word))
                g.add((word, RDF.type, ligt.Word))
                g.add((word, DCTERMS.isPartOf, phrase))
                g.add((word, RDFS.label, Literal(gloss[0].strip('\\.,'), lang=lang_tag)))

                if next_word:
                    g.add((word, ligt.next, next_word))

                next_morph = URIRef('{}_item_morph_{}_{}'.format(ex, i + 1, 1))
                subglosses = split_morphs(gloss)

                for j, subgloss in enumerate(subglosses):
                    morph = next_morph
                    next_morph = URIRef('{}_item_morph_{}_{}'.format(ex, i + 1, j + 2)) if j < len(
                        subglosses) - 1 else None

                    g.add((ex_tier_morphs, ligt.item, morph))
                    g.add((morph, RDF.type, ligt.Morph))
                    g.add((morph, DCTERMS.isPartOf, word))
                    g.add((morph, RDFS.label,
                           Literal(subgloss[0].strip('\\.,') if len(subgloss) > 0 and subgloss[0] else "",
                                   lang=lang_tag)))
                    g.add((morph, ligt.gloss,
                           Literal(subgloss[1].strip('\\.,') if len(subgloss) > 1 and subgloss[1] else "", lang=meta_lang)))

                    if next_morph:
                        g.add((morph, ligt.next, next_morph))

        return g
