import unittest
import os
import json

from src.data_classes.bilingual_text import BilingualText
from src.pdf_gen.pdf_generator import generate_bilingual_pdf

OUTPUT_DIR = 'src/tests/test_data/outputs/audio'


class Test_pdf_generator(unittest.TestCase):

    def test_binlingual_to_pdf(self):
        with open("src/tests/test_data/outputs/billing_text.json", "r",
                  encoding="utf-8") as f:
            dict_data = json.load(f)
            bti = BilingualText.model_validate(dict_data)
            pdf_buffer: bytes = generate_bilingual_pdf(bti)
            output_file_name = os.path.join(OUTPUT_DIR, 'test_bilingual.pdf')
            with open(output_file_name, 'wb') as pdf_file:
                pdf_file.write(pdf_buffer)


        