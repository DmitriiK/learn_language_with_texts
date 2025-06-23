from pydantic import BaseModel, Field
from typing import List, Set
import yaml


class WordOccurrencesInText(BaseModel):
    """A class representing a word and its occurrences in a text."""
    
    word: str = Field(..., description="The word itself")
    positions_in_text: List[int] = Field(..., description="List of positions in the text where the word occurs")

class LemmaInTheText(BaseModel):
    lemma: str = Field(..., description="Lemmatized form of the word")
    pos: str = Field(..., description="Part of speech tag for the lemma")
    word_occurrences_in_text: List[WordOccurrencesInText] = Field(
        ...,
        description="Occurrences of the word in the text, including its positions"
    )

    def __hash__(self):
        return hash((self.lemma, self.pos))

    def __eq__(self, other):
        if not isinstance(other, LemmaInTheText):
            return NotImplemented
        return (self.lemma, self.pos) == (other.lemma, other.pos)

    def to_json(self):
        """Convert the LemmaIndex instance to a JSON string."""
        return self.model_dump_json(indent=4)
    
    def to_yaml(self):
        """Convert the LemmaIndex instance to a YAML string."""
        return yaml.dump(self.model_dump(), allow_unicode=True, sort_keys=False)
    
class LemmasIndex(BaseModel):
    text: str = Field(..., description="The original text from which lemmas are extracted")
    lemmas: Set[LemmaInTheText] = Field(
        ...,
        description="List of unique lemmas with their part of speech and occurrences in the text"
    )
    def add_lemma(self, lemma: str, pos: str, word: str, position_in_text: int):
        """Add a lemma to the index, ensuring uniqueness and updating occurrences."""
        # Find existing lemma entry
        existing_lemma = next((l for l in self.lemmas if l.lemma == lemma and l.pos == pos), None)
        if not existing_lemma:
            # Create new LemmaIndex and add to set
            new_lemma = LemmaInTheText(
                lemma=lemma,
                pos=pos,
                word_occurrences_in_text=[
                    WordOccurrencesInText(word=word, positions_in_text=[position_in_text])
                ]
            )
            self.lemmas.add(new_lemma)
            return

        # Find existing word occurrence within the lemma
        word_occurrence = next((wo for wo in existing_lemma.word_occurrences_in_text if wo.word == word), None)
        if word_occurrence:
            word_occurrence.positions_in_text.append(position_in_text)
        else:
            existing_lemma.word_occurrences_in_text.append(
                WordOccurrencesInText(word=word, positions_in_text=[position_in_text])
            )
