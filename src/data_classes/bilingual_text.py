from pydantic import BaseModel, Field
from typing import List
import yaml


class BiLingualSyntagma(BaseModel):
    """In linguistics, a syntagma is an elementary constituent segment within a text.
    Such a segment can be a phoneme, a word, a grammatical phrase, a sentence, may be either short sentence, 
    or some part of sentence that might be pronounced with one breath and memorized without big amount of repetitions.
    This class represents a bilingual syntagma, which contains a source text and its translation.
    """
    source_text: str = Field(..., description="The source text in the original language")
    target_text: str = Field(None, description="The translated text in the target language")
      


class BilingualParagraph(BaseModel):

    """
   Paragraph containing bilingual sintagmas.
    """
    Sintagmas: List[BiLingualSyntagma] = Field(
        ...,
        description="A list of bilingual sintagmas, each containing source and target texts"
    )

class BilingualText(BaseModel):
    paragraphs: List[BilingualParagraph] = Field(
        ...,
        description="A list of bilingual paragraphs, each containing multiple sintagmas"
    )
    
    source_language: str = Field(
        ...,
        description="The language of the source text"
    )
    target_language: str = Field(
        ...,
        description="The language of the target text, if available"
    )

    def to_json(self):
        """Convert the BilingualText instance to a JSON string."""
        return self.model_dump_json(indent=4)
    
    def to_yaml(self):
        """Convert the BilingualText instance to a YAML string."""
        return yaml.dump(self.model_dump(), allow_unicode=True, sort_keys=False)
    
 
    def __str__(self):
        return f"BilingualText(source_language={self.source_language}, target_language={self.target_language}, paragraphs_count={len(self.paragraphs)})"