import spacy

nlp = spacy.load("zh_core_web_trf")

def extract_entity_relation_triples(text):
    doc = nlp(text)
    triples = []
    for sent in doc.sents:
        subject, relation, obj = "", "", ""
        for token in sent:
            if token.dep_ in ("nsubj", "nsubjpass"):
                subject = token
            elif token.dep_ == "ROOT":
                relation = token
            elif token.dep_ in ("dobj", "pobj"):
                obj = token
            if subject in ('.', '。', '，', ',', '、', '？', '!', '；'):
                continue
            if relation in ('.', '。', '，', ',', '、', '？', '!', '；'):
                continue
            if obj in ('.', '。', '，', ',', '、', '？', '!', '；'):
                continue
        if subject and relation and obj:
            triples.append((subject, relation, obj))
    return triples

def queryEnt(text: str):
    results = []
    doc = nlp(text)

    # 提取每个词的词性、依赖关系和词形
    for token in doc:
        if token.pos_ == "NOUN":
            results.append({"label": f"{token.text}:{token.pos_}", "number": 1})
    return results
