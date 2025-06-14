from unittest import TestCase
from src.text_processing.llm_communicator import create_bilingual_text

class TestLLM(TestCase):
    def test_create_bilingual_text(self):
        input_text = """Kenan Bey, erkenden uyandı. Eşi ve çocukları hâlâ uyuyor-
        du. O çok heyecanlıydı. Gardıroptan takım elbisesini alıp
        hızlıca odadan çıktı. Kıyafetlerini değiştirdi ve kahvaltı et-
        meden evden çıktı. Sokağın başına kadar yürüdü. Durağa
        gidip beklemeye başladı. Beş dakika sonra otobüs geldi.
        Otobüs boştu. Kenan Bey, arka koltuklardan birine oturdu.
        Otobüs kırk beş dakika sonra Kızılay’a, Ankara’nın merke-
        zine ulaştı. Otobüs şoförü yüksek sesle “Kızılay’da inecek
        yolcularımız! Lütfen, hazırlanın!” dedi. Kenan Bey yerinden
        kalktı ve kapıya doğru ilerledi. Otobüs durakta durdu ve Ke-
        nan Bey otobüsten indi. Sonra Güvenpark’ın içinden geçip
        Maltepe Camisi’ne doğru yürümeye başladı. Kızılay her za-
        manki gibi çok kalabalıktı. Kenan Bey biraz yürüdü. Sonra
        sekiz katlı bir iş hanının önünde durdu. Hanın önündeki ta-
        belalara baktı. Sonra ceketinin cebinden bir kâğıt parçası
        çıkardı. Kâğıtta bir adres yazılıydı. Önce elindeki adrese
        sonra da tabelalara baktı. “Evet, aradığım yer burası.” dedi"""

        target_language = "Russian"
        result = create_bilingual_text(input_text, target_language)
        assert len(result.paragraphs) > 0, "Result should contain at least one paragraph"
        assert result.source_language == "Turkish", "Source language should be Turkish"
        print(result.to_yaml)