import unittest
import json
import xml.etree.ElementTree as ET

from src.tts.ssml_generator import generate_ssml, chunk_ssml
from src.data_classes.bilingual_text import BilingualText

OUTPUT_DIR = 'src/tests/test_data/outputs/audio'
class TestSSML(unittest.TestCase):
    
    def validate_xml(self, xml_str, description):
        """Helper method to validate XML and assert that it's well-formed"""
        try:
            ET.fromstring(xml_str)
            is_valid_xml = True
            error_msg = None
        except ET.ParseError as e:
            is_valid_xml = False
            error_msg = str(e)
            print(f"XML validation error in {description}: {error_msg}")
        
        self.assertTrue(is_valid_xml, f"{description} should be valid XML")

    def test_ssml_gen(self):
        with open("src/tests/test_data/outputs/billing_text.json", "r", encoding="utf-8") as f:
            dict_data = json.load(f)
            bilingual_text_instance = BilingualText.model_validate(dict_data)
        # Define additional parameters
        source_language_voice = "tr-TR-AhmetNeural"
        target_language_voice = "en-US-AvaNeural"
        break_time = "750ms"

        # Generate SSML
        ssml_output = generate_ssml(
            bilingual_text=bilingual_text_instance,
            source_language_voice=source_language_voice,
            target_language_voice=target_language_voice,
            break_time=break_time
        )

        # Print the SSML output
        print(ssml_output)
        
        # Validate that the generated SSML is well-formed XML
        self.validate_xml(ssml_output, "Generated SSML")
        
    def test_chunk_ssml(self):
        """Test the chunk_ssml function that splits SSML into chunks of specified size."""
        # Create sample SSML with multiple voice blocks
        sample_ssml = """<speak>
        <voice name="tr-TR-AhmetNeural">
           Kenan Bey, erkenden uyandı.
        </voice>

        <voice name="en-GB-RyanNeural"> Kenan Bey woke up early. </voice>

        <voice name="tr-TR-AhmetNeural">
           Eşi ve çocukları hâlâ uyuyordu.
        </voice>

        <voice name="en-GB-RyanNeural"> His wife and children were still sleeping. </voice>
        
        <voice name="tr-TR-AhmetNeural">
           O çok heyecanlıydı.
        </voice>
        </speak>"""
        
        # Test with chunk_size = 2
        chunks = chunk_ssml(sample_ssml, chunk_size=2)
        
        # Verify we got the right number of chunks
        self.assertEqual(len(chunks), 3, "Should split into 3 chunks with chunk_size=2")
        
        # Verify each chunk has the correct structure
        for i, chunk in enumerate(chunks):
            self.assertTrue(chunk.startswith("<speak>"), "Chunk should start with <speak>")
            self.assertTrue(chunk.endswith("</speak>"), "Chunk should end with </speak>")
            
            # Validate that the XML is well-formed
            self.validate_xml(chunk, f"Chunk {i + 1}")
        
        # Verify first chunk has exactly 2 voice blocks
        self.assertEqual(
            chunks[0].count("<voice"), 2,
            "First chunk should contain exactly 2 voice blocks"
        )
        
        # Verify second chunk has exactly 2 voice blocks
        self.assertEqual(
            chunks[1].count("<voice"), 2,
            "Second chunk should contain exactly 2 voice blocks"
        )
        
        # Verify last chunk has exactly 1 voice block
        self.assertEqual(
            chunks[2].count("<voice"), 1,
            "Last chunk should contain exactly 1 voice block"
        )
        
        # Test with default chunk_size
        chunks_default = chunk_ssml(sample_ssml)
        
        # With the default size (should be 45), all voice blocks should fit into a single chunk
        self.assertEqual(len(chunks_default), 1,
                         "With default chunk size, all 5 voice blocks should fit into 1 chunk")
        
        # Validate XML format for the default chunk
        self.validate_xml(chunks_default[0], "Default chunk")