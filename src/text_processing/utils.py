import re

import nltk
from nltk.tokenize import sent_tokenize
# Download the Punkt tokenizer model (if not already downloaded)
nltk.download('punkt')
nltk.download('punkt_tab')


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
            chunk = []
            # Split by sentence-ending punctuation (., ?, !), keeping the punctuation
            # 
            sentences = (sent.strip() for sent in sent_tokenize(paragraph) if sent.strip())
            for sentence in sentences:
                if chunk and len(' '.join(chunk + [sentence])) > max_length:
                    paragraphs.append(' '.join(chunk))
                    chunk = [sentence]
                else:
                    chunk.append(sentence)
            if chunk:
                paragraphs.append(' '.join(chunk))

    return paragraphs
