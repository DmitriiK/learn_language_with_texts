from unittest import TestCase
from src.text_processing.nlp import lemmatize
from src.data_classes.lemma_index import LemmasIndex   

class TestNLP(TestCase):
    def test_lemmatize(self):
        with open("src/tests/test_data/inputs/turkish_text.txt", "r") as file:
            text = file.read()
            result: LemmasIndex = lemmatize(text)
            assert isinstance(result, LemmasIndex), "Lemmatization result should be a LemmasIndex instance"
            assert len(result.lemmas) > 0, "Lemmatization should return at least one lemma"




        