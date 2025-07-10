
import json
import os

from fastapi.responses import JSONResponse


from src.data_classes.bilingual_text import BilingualText
from src.api.data_classes import TranslationRequest
import src.config as cfg
from src.authentication import UserRole


# utilities
def save_to_session_store(bt: BilingualText) -> int:
    bt_hash = hash(bt)
    output_dir = os.path.join(cfg.SESSION_DATA_FILE_PATH, str(bt_hash))
    os.makedirs(output_dir, exist_ok=True)
    # Write the JSON to a file in the output directory
    output_path = os.path.join(output_dir, "bilingual_text.json")
    with open(output_path, "w", encoding="utf-8") as out_f:
        out_f.write(bt.to_json())
    return bt_hash


def read_from_session_store(bilingual_text_hash: int, output_dir: str) -> BilingualText:
    bt_file_path = os.path.join(output_dir, "bilingual_text.json")
    if not os.path.exists(bt_file_path):
        raise FileNotFoundError(f"Bilingual text with hash {bilingual_text_hash} not found.")
    return BilingualText.from_json_file(bt_file_path)


def validate_translation_request(req: TranslationRequest, user):
    # Validate user role and text length
    role2maxlen = {UserRole.Admin: 100000,
                   UserRole.SupeAdmin: 50000, 
                   UserRole.User: 10000, UserRole.Guest: 1000} # TODO - move to config
    if role2maxlen.get(user.role, 200) < len(req.source_text):
        return JSONResponse(content={"error": "Text too long for your role"},
                            status_code=400)
    return None   


def get_test_blt():
    # This is a stub for the data for testing get_test_bilingual_text endpoint
    with open("src/tests/test_data/outputs/billing_text.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        bt: BilingualText = BilingualText.model_validate(data)
        return bt

