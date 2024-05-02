import time
from natasha import (
    Segmenter,
    MorphVocab,
    
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    
    NamesExtractor,

    Doc
)
text = ""

segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

extractor = NamesExtractor(morph_vocab)

doc = Doc(text)
# Сегментация, морфологический и синтаксический анализ, NER
doc.segment(segmenter)
doc.tag_morph(morph_tagger)
doc.parse_syntax(syntax_parser)
doc.tag_ner(ner_tagger) 
# начальное время
start_time = time.time()
 
# код, время выполнения которого нужно измерить

 
 

# конечное время
end_time = time.time()
 
# разница между конечным и начальным временем
elapsed_time = end_time - start_time
print('Elapsed time: ', elapsed_time)