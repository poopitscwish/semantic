import spacy
from spacy.pipeline import Sentencizer
from rdflib import Graph, Namespace, URIRef, Literal

nlp = spacy.load("xx_ent_wiki_sm")

if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe('sentencizer')



def create_ontology(text):
    g = Graph()
    onto = Namespace("http://example.org/ontology/")
    g.bind("onto", onto)
    doc = nlp(text)
    
    for sent in doc.sents:
        entities = [ent.text for ent in sent.ents]

        for entity in entities:

            uri = URIRef(onto[entity.lower().replace(" ", "_")])
            # Добавляем свойство типа для сущности
            g.add((uri, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), onto.Entity))
            # Добавляем литерал с текстом сущности
            g.add((uri, URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal(entity)))    
    # print(g.serialize(format="xml"))
    return g

