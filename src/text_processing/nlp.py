import re
from typing import List

import stanza
from langdetect import detect

from src.data_classes.lemma_index import  LemmasIndex

def lemmatize(text: str, lang: str = None) ->  LemmasIndex:
    """
    Processes the input text and returns a list of LemmaIndex objects,
    each containing lemma, POS, and character positions for each word.
    Lemmas are unique; if a lemma repeats, add the word and its position to the existing entry.
    """
    nlp = stanza.Pipeline(lang or detect(text), processors='tokenize,mwt,pos,lemma')
    doc = nlp(text)
    lsi = LemmasIndex(text=text, lemmas=set())
    for sentence in doc.sentences:
        for word in sentence.words:
            lemma = word.lemma or f'{word.text} (lemma not defined)'  # Use the original word if lemma is not available
            lsi.add_lemma(
                lemma=lemma,
                pos=word.upos,
                word=word.text,
                position_in_text=word.start_char
            )
    return lsi

def split_to_paragraphs(text: str, max_length: int = 0) -> list[str]:
    """
    Splits the input text into paragraphs, considering double new line as explicit paragraph splitter, 
      ensuring each paragraph does not exceed max_length.
      In case if len(sentence)>max_length?  it should be added as a new paragraph as is, without splitting.
    """
    paragraphs = []
    for paragraph in re.split(r'(?:\s*\n\s*\n\s*)', text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if not max_length or len(paragraph) <= max_length:
            # If paragraph does not exceed max_length, add it to the current paragraph
            paragraphs.append(paragraph)
        else:
            # If paragraph exceeds max_length, split it into chunks with some subset of lines
            paragraphs.extend(_repartition_paragraph(paragraph, max_length))
    return paragraphs

def _repartition_paragraph(paragraph: str, max_length: int) -> list[str]:
    """
    Splits a paragraph into smaller paragraphs by sentences, ensuring each does not exceed max_length.
    If a sentence itself exceeds max_length, it is added as a separate paragraph as is.
    """
    detected_language = detect(paragraph)  # This will return a language code like 'fr', 'en', 'ru', etc.
    nlp = stanza.Pipeline(lang=detected_language, processors='tokenize', tokenize_no_ssplit=True)
    doc = nlp(paragraph)
    sentences = [sentence.text.strip() for sentence in doc.sentences]

    result = []
    current = ""
    for sentence in sentences:
        if len(sentence) > max_length:
            if current:
                result.append(current.strip())
                current = ""
            result.append(sentence)
        elif len(current) + len(sentence) + 1 <= max_length:
            current = f"{current} {sentence}".strip() if current else sentence
        else:
            if current:
                result.append(current.strip())
            current = sentence
    if current:
        result.append(current.strip())
    return result


