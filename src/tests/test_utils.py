
import unittest
from text_processing.utils import split_to_paragraphs
from nltk.tokenize import sent_tokenize

class TestSplitToParagraphs(unittest.TestCase):

    def test_split_to_paragraphs_basic(self):
        text = "This is the first paragraph.\n\nThis is the second paragraph."
        result = split_to_paragraphs(text)
        self.assertEqual(result, ["This is the first paragraph.", "This is the second paragraph."])

    def test_split_to_paragraphs_with_max_length(self):
        text = "Sentence one. Sent two. Sentence three."
        result = split_to_paragraphs(text, max_length=25)
        self.assertEqual(result, ["Sentence one. Sent two.", "Sentence three."])

    @unittest.skip("Test for abbreviation splitting is currently not supported")
    def test_split_with_abbreviation(self):
        # does not work with abbreviations
        text = "Sentence one. Sent. 2."
        result = sent_tokenize(text)  # split_to_paragraphs(text, max_length=5)
        self.assertEqual(result, ["Sentence one.", "Sent. 2."])

    def test_split_to_paragraphs_sentence_longer_than_max_length(self):
        text = "Short. This sentence is definitely longer than ten characters."
        result = split_to_paragraphs(text, max_length=10)
        self.assertEqual(result, ["Short.", "This sentence is definitely longer than ten characters."])

    def test_split_to_paragraphs_multiple_paragraphs_and_sentences(self):
        text = (
            "First para sentence one. First para sentence two!\n\n"
            "Second para sentence one? Second para sentence two."
        )
        result = split_to_paragraphs(text, max_length=30)
        self.assertEqual(result, [
            "First para sentence one.",
            "First para sentence two!",
            "Second para sentence one?",
            "Second para sentence two."
        ])

    def test_split_to_paragraphs_empty_and_whitespace(self):
        text = "\n\n   \n\n"
        result = split_to_paragraphs(text)
        self.assertEqual(result, [])

    def test_split_to_paragraphs_no_max_length(self):
        text = "A. B. C."
        result = split_to_paragraphs(text, max_length=0)
        self.assertEqual(result, ["A. B. C."])

    def test_split_to_paragraphs_paragraph_exactly_max_length(self):
        text = "12345"
        result = split_to_paragraphs(text, max_length=5)
        self.assertEqual(result, ["12345"])

    def test_split_to_paragraphs_sentence_with_no_punctuation(self):
        text = "This is a sentence without punctuation"
        result = split_to_paragraphs(text, max_length=10)
        self.assertEqual(result, ["This is a sentence without punctuation"])

    # Additional tests

    def test_split_to_paragraphs_multiple_newlines(self):
        text = "Para1.\n\n\n\nPara2."
        result = split_to_paragraphs(text)
        self.assertEqual(result, ["Para1.", "Para2."])

    def test_split_to_paragraphs_leading_and_trailing_whitespace(self):
        text = "   Para1.   \n\n   Para2.   "
        result = split_to_paragraphs(text)
        self.assertEqual(result, ["Para1.", "Para2."])

    def test_split_to_paragraphs_long_sentence_within_paragraph(self):
        text = "Short. " + "A very long sentence that should not be split even if it exceeds the max length."
        result = split_to_paragraphs(text, max_length=10)
        self.assertEqual(result, ["Short.", "A very long sentence that should not be split even if it exceeds the max length."])

    def test_split_to_paragraphs_single_long_sentence(self):
        text = "A very long sentence that should be its own paragraph."
        result = split_to_paragraphs(text, max_length=10)
        self.assertEqual(result, ["A very long sentence that should be its own paragraph."])

    def test_split_to_paragraphs_mixed_punctuation(self):
        text = "Hello! How are you? I'm fine."
        result = split_to_paragraphs(text, max_length=15)
        self.assertEqual(result, ["Hello!", "How are you?", "I'm fine."])

    def test_split_to_paragraphs_unicode_characters(self):
        text = "Привет. Как дела? Всё хорошо!"
        result = split_to_paragraphs(text, max_length=15)
        self.assertEqual(result, ["Привет.", "Как дела?", "Всё хорошо!"])

    def test_split_to_paragraphs_no_sentences(self):
        text = ""
        result = split_to_paragraphs(text)
        self.assertEqual(result, [])

    def test_split_to_paragraphs_paragraph_with_only_spaces(self):
        text = "   \n\n   "
        result = split_to_paragraphs(text)
        self.assertEqual(result, [])

    def test_split_to_paragraphs_sentence_ends_without_punctuation(self):
        text = "This is a sentence without punctuation\n\nAnother one"
        result = split_to_paragraphs(text, max_length=10)
        self.assertEqual(result, ["This is a sentence without punctuation", "Another one"])

if __name__ == "__main__":
    unittest.main()

