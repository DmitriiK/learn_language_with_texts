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
            sorted_lemmas = sorted(result.lemmas, key=lambda l: l.number_of_occurrences, reverse=True)
            print(f'Count of lemmas: {len(sorted_lemmas)}')
            for lemma in list(sorted_lemmas)[:20]:
                assert lemma.number_of_words > 0, "Each lemma should have at least one word associated with it"
                print(f'count of words in lemma: {lemma.number_of_words}')
                assert lemma.number_of_occurrences >= lemma.number_of_words , "Each lemma should have at least one occurrence"
                print(f'count of occurrences in lemma: {lemma.number_of_occurrences}')
                print(lemma.to_yaml())




        