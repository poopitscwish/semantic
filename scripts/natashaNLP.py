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
import re
from rdflib import Graph, Namespace, URIRef, Literal

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

def sort_tokens_by_word_number(tokens):
    # Функция для извлечения номера слова из id токена
    def word_number(token):
        _, word_num = token['id'].split('_')
        return int(word_num)

    # Сортировка списка токенов по номеру слова
    return sorted(tokens, key=word_number)

def create_triple(raw_text):
    text = re.sub(r'[\(\)\[\]\{\}]', '', raw_text)
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

    for span in doc.spans:
        span.normalize(morph_vocab)

    # Собираем результаты для вывода
    output_lines = []
    ents = []
    for i, sent in enumerate(doc.sents, start=1):
        for j, token in enumerate(sent.tokens, start=1):
            # По умолчанию тип сущности не определен
            entity_type = ''

            # Проверяем, попадает ли токен в диапазон какой-либо именованной сущности
            for span in doc.spans:
                if span.start <= token.start and span.stop >= token.stop:
                    entity_type = span.type
                    break  # Выходим из цикла, так как нашли соответствующую сущность

            # Формируем строку вывода с информацией о токене и, если есть, типе сущности
            output_line = f"{token.id}: {token.text}, POS: {token.pos}, head_id: {token.head_id}, "
            if entity_type:
                output_line += f"type: {entity_type}"
            output_lines.append(output_line)
            
            if (token.pos == 'PROPN' or token.pos == 'NOUN' or token.pos == 'VERB'):
                head_parts = token.head_id.split('_')
                sentence, word = head_parts
                subject = token
                predicate = sent.tokens[int(word)-1]
                pred_head = predicate.head_id.split('_')[1]
                obj = sent.tokens[int(pred_head)-1]
                line = f"{subject.text} - {predicate.text} - {obj.text}"
                ents.append(line)      
    pattern = r'(\d+_\d+):\s+(\w+),\s+POS:\s+(\w+),\s+head_id:\s+(\d+_\d+)(?:,\s+type:\s+(\w+))?'
    tokens_info = []
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

    def find_references(token_id, tokens):
        return [token for token in tokens if token['head_id'] == token_id]
    rdf_triples = []
    for token in tokens_info:
        if token['pos'] == 'VERB':
            # Глагол служит предикатом
            predicate = token['text']

            # Поиск субъекта, на который ссылается глагол
            subject_token = next((t for t in tokens_info if t['head_id'] == token['id']), None)
            if subject_token:
                subject = subject_token['text']
                
                # Поиск объектов, ссылающихся на глагол
                objects = find_references(token['id'], tokens_info)
                for obj_token in objects:
                    all_obj_tokens = [obj_token] + find_references(obj_token['id'], tokens_info)
                    # Сортировка всего списка токенов по номеру слова
                    sorted_obj_tokens = sort_tokens_by_word_number(all_obj_tokens)
                    # Формирование строки объекта
                    obj = ' '.join(token['text'] for token in sorted_obj_tokens)
                    # Формирование и добавление RDF-тройки
                    if subject != obj:
                        rdf_triples.append((subject, predicate, obj))

    # Вывод RDF-троек
    for triple in rdf_triples:
        print(f"Sub: {triple[0]}, Pred: {triple[1]}, Obj: {triple[2]}")

    
    # print(g.serialize(format="xml"))
    # Запись результатов в файл
    output_file_path = "C:\\Users\\sheny\\Downloads\\про\\Результат.txt"
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        for line in output_lines:
            output_file.write(line + "\n")
    return rdf_triples
 
# raw_text = "Посол Израиля на Украине Йоэль Лион признался, что пришел в шок, узнав о решении властей Львовской области объявить 2019 год годом лидера запрещенной в России Организации украинских националистов (ОУН) Степана Бандеры. Свое мнение он разместил в Twitter."
# # create_triple(raw_text)