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
from transformers import MBartTokenizer, MBartForConditionalGeneration
import re
from rdflib import Graph, Namespace, URIRef, Literal
model_name = "IlyaGusev/mbart_ru_sum_gazeta"
tokenizer = MBartTokenizer.from_pretrained(model_name)
model = MBartForConditionalGeneration.from_pretrained(model_name)
def summurize(text, max = 600):
    input_ids = tokenizer(
        [text],
        max_length = max,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )["input_ids"]

    output_ids = model.generate(
        input_ids=input_ids,
        no_repeat_ngram_size=4
    )[0]
    summary = tokenizer.decode(output_ids, skip_special_tokens=True)
    return summary
    
def generate_rdf(rdf_triples):
    g = Graph()
    # Определяем пространство имен для наших ресурсов (можно изменить на свое)
    ex = Namespace("http://example.org/ontology/")

    # Добавляем тройки в граф
    for sub, pred, obj in rdf_triples:
        subject = URIRef(ex + sub.replace(' ', '_'))  # Заменяем пробелы на подчеркивания для URI
        predicate = URIRef(ex + pred.replace(' ', '_'))
        # Для объекта выбираем Literal или URIRef в зависимости от контекста
        # Здесь используем Literal для упрощения; для ресурсов следует использовать URIRef
        object_ = Literal(obj)
        
        g.add((subject, predicate, object_))
    return g

def rework_sent(sent, doc, pos):
    # Словарь для хранения связей между модификаторами и главными словами
    dependencies = {}
    used_id = []
    # Сначала идентифицируем все связи
    for token in sent.tokens:
        if token.pos in pos and token.head_id != '1_0':  # Убедимся, что у токена есть главное слово
            # Добавляем модификатор и его главное слово в словарь
            if token.head_id not in dependencies:
                dependencies[token.head_id] = []
            # Добавляем в список словарь с id и текстом модификатора
            dependencies[token.head_id].append({
                'id': token.id,  # Уникальный идентификатор токена
                'text': token.text  # Текст токена
            })
            # if entity_type:
    for token in sent.tokens:
        # Если токен является главным словом для модификатора, добавляем модификаторы перед ним
        
        if token.id in dependencies and token.pos !='VERB':
            
            mods = "" 
            for mod in dependencies[token.id]:
                used_id.append(mod['id'])
                mods +=  mod['text'] + ' '
            if int(dependencies[token.id][0]['id'].split('_')[1]) < int(token.id.split('_')[1]):
                token.text = mods + token.text
            else:
                token.text += ' ' + mods                   
    return used_id
def get_entities(raw_text):
    text = raw_text
    
    # Инициализация компонентов Natasha
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
    
    # Сбор основных сущностей в тексте (без повторений)
    unique_entities = set()
    for span in doc.spans:
        span.normalize(morph_vocab)
        unique_entities.add(span.normal)
    entities = list(unique_entities)
    result = "| "
    for entity in entities:
        result += entity + " | "
    return result


def create_triple(raw_text):
    text = raw_text
    
    # Инициализация компонентов Natasha
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

    # Собираем результаты для вывода и преобразуем в словарь для удобного обращения к значениям
    output_lines = [] # Список для хранения строк вывода
    # Формирование файла с морфологическим разбором
    for i, sent in enumerate(doc.sents, start=1):
        entity = {}
        main_tokens = []
        second_tokens = []
        for span in doc.spans:
            token_id = []
            token_head_id = []
            for token in span.tokens:
                token_id.append(token.id)
                token_head_id.append(token.head_id)
            for j, id in enumerate(token_head_id, start=0):
                if id not in token_id:
                    main_tokens.append(token_id[j])
                    entity[token_id[j]] = span.text
                else:
                    second_tokens.append(token_id[j])   
        for token in sent.tokens[:]:
            if token.id in main_tokens:
                token.text = entity[token.id]
            if token.id in second_tokens:
                sent.tokens.remove(token)
        
        used_id = []
        # used_id += rework_sent(sent, doc, ['PART'])
        # used_id += rework_sent(sent, doc, ['PROPN'])
        used_id += rework_sent(sent, doc, ['ADP'])
        used_id += rework_sent(sent, doc, ['ADJ'])
        # used_id += rework_sent(sent, doc, ['DET'])
        # used_id += rework_sent(sent, doc, ['SCONJ'])
        # used_id += rework_sent(sent, doc, ['NOUN'])
        # used_id += rework_sent(sent, doc, ['NUM'])
        # used_id += rework_sent(sent, doc, ['CCONJ'])
        # used_id += rework_sent(sent, doc, ['PRON'])
        
        for token in sent.tokens: 
            entity_type = ''
            for span in doc.spans:
                if span.start <= token.start and span.stop >= token.stop:
                    entity_type = span.type
                    break  # Выходим из цикла, так как нашли соответствующую сущность    
            output_line = f"{token.id}: {token.text}, POS: {token.pos}, head_id: {token.head_id}"
            if entity_type:
                output_line += f" type: {entity_type}" # Добавление поля о типе сущности (локация, организация и т.д)
            
            # if token.pos in ['NOUN', 'VERB', 'PRON', 'PROPN', 'ADJ', 'ADP', 'NUM', ] and token.id not in used_id:
            if token.pos != 'PUNCT':
                output_lines.append(output_line)      
        
        
        
    output_file_path = "C:\\Users\\sheny\\Downloads\\про\\Результат.txt"
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        for line in output_lines:
            output_file.write(line + "\n")
            
            
            
    pattern = r'(\d+_\d+):\s+([^\,]+),\s+POS:\s+(\w+),\s+head_id:\s+(\d+_\d+)(?:,\s+type:\s+(\w+))?' # Шаблон строки которая будет добавляться в словарь
    tokens_info = [] # конечный словарь с данными о токенах
    for input_str in output_lines:
        # Применяем регулярное выражение к строке
        match = re.match(pattern, input_str)

        # Если совпадение найдено, создаем словарь с результатами и добавляем его в список
        if match:
            token_info = {
                'id': match.group(1),
                'text': match.group(2),
                'pos': match.group(3),
                'head_id': match.group(4)
            }

            # Добавляем тип, если он присутствует в строке
            if match.group(5):
                token_info['type'] = match.group(5)

            tokens_info.append(token_info)
    

    # Сортировка слов в порядке возрастания
    def sort_tokens_by_word_number(tokens):
    # Функция для извлечения номера слова из id токена
        def word_number(token):
            _, word_num = token['id'].split('_')
            return int(word_num)
        # Сортировка списка токенов по номеру слова
        return sorted(tokens, key=word_number)
    def find_references(token_id, tokens):
        return [token for token in tokens if token['head_id'] == token_id]
    rdf_triples = []
    used_triples = []
    for token in tokens_info:
        if token['pos'] == 'VERB':
            # Глагол служит предикатом
            predicate = token['text']

            # Поиск субъекта, на который ссылается глагол
            subject_tokens = find_references(token['id'], tokens_info)
            for obj_token in subject_tokens:
                all_obj_tokens = [obj_token] + find_references(obj_token['id'], tokens_info)
                # Сортировка всего списка токенов по номеру слова
                sorted_obj_tokens = sort_tokens_by_word_number(all_obj_tokens)
                # Формирование строки объекта
                subject = ' '.join(token['text'] for token in sorted_obj_tokens)
                
                
                objects = find_references(token['id'], tokens_info)
                for obj_token in objects:
                    all_obj_tokens = [obj_token] + find_references(obj_token['id'], tokens_info)
                    # Сортировка всего списка токенов по номеру слова
                    sorted_obj_tokens = sort_tokens_by_word_number(all_obj_tokens)
                    # Формирование строки объекта
                    obj = ' '.join(token['text'] for token in sorted_obj_tokens)
                    # Формирование и добавление RDF-тройки
                    if subject != obj and obj and (obj, predicate, subject) not in used_triples:
                        used_triples.append((subject, predicate, obj))
                        rdf_triples.append((subject, predicate, obj))               
    
    # Запись результатов в файл

    return rdf_triples
def remove_specific_punctuation(text):
    # Удаляем конкретные символы пунктуации
    return re.sub(r'["()«»]', '', text)

# raw_text = "Посол Израиля на Украине Йоэль Лион признался, что пришел в шок, узнав о решении властей Львовской области объявить 2019 год годом лидера запрещенной в России Организации украинских националистов (ОУН) Степана Бандеры. Свое мнение он разместил в Twitter."
# raw_text = "Энергетический комплекс Иркутской области является одним из крупнейших в РФ. Он представлен объектами «большой энергетики», входящими в основном в структуру «ЕвроСибэнерго», а также объектами «малой энергетики», которую прежде относили к «коммунальной». В состав «малой энергетики» входят распределительные электрические и тепловые сети, муниципальные, одна ТЭЦ, котельные, дизельные электростанции (ДЭС), возобновляемые источники энергии (ВИЭ) с различной формой собственности. Кроме перечисленных объектов, к энергетическому комплексу Иркутской области, относятся также частные и государственные компании по добыче и переработки ископаемых энергетических ресурсов, функционирующие в различных районах области. Рассмотрим состояние, проблемы, перспективы функционирования и развития обеих составляющих энергетического комплекса Иркутской области, относящиеся, прежде всего, к электроснабжению и теплоснабжению потребителей."
# create_triple(raw_text)