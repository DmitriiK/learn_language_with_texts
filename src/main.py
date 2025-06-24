import json
from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from src.text_processing.llm_communicator import create_bilingual_text
from src.text_processing.nlp import lemmatize
from src.data_classes.lemma_index import LemmasIndex

app = FastAPI()

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

class TranslationRequest(BaseModel):
    source_text: str
    target_language: str
    output_format: str  # 'web' or 'pdf' or 'json'
    layout: str         # 'continuous' or 'side-by-side'

class LemmatizeRequest(BaseModel):
    text: str
    language: str
    filter_out_stop_words: bool = False

@app.post("/api/make_bilingual2")
def make_bilingual2(req: TranslationRequest):
    try:
        result = create_bilingual_text(req.source_text, req.target_language)
        # Only return JSON for both 'web' and 'json' output formats
        if req.output_format in ('web', 'json'):
            return JSONResponse(content=result.model_dump())
        elif req.output_format == 'pdf':
            # TODO: Implement PDF export
            return JSONResponse(content={"error": "PDF export not implemented yet."}, status_code=501)
        else:
            return JSONResponse(content={"error": "Unknown output_format"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@app.post("/api/make_bilingual")
def make_bilingual(req: TranslationRequest):
    # This is a stub for the make_bilingual endpoint
    # It returns the contents of a test JSON file for testing purposes
    print("Received request for stub data")
    with open("src/tests/test_data/outputs/biling_text.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    print("Returning stub data")
    return JSONResponse(content=data)

@app.get("/")
def index():
    with open("src/static/index.html") as f:
        return HTMLResponse(f.read())
    

@app.post("/api/lemmatize")
def lemmatize_endpoint(req: LemmatizeRequest):
    result: LemmasIndex = lemmatize(text=req.text, lang=req.language, filter_out_stop_words=req.filter_out_stop_words)
    frequency_list = sorted(result.lemmas, key=lambda l: l.number_of_occurrences, reverse=True)

    # Only include lemma, number_of_words, and number_of_occurencs in the response
    for_fe = [
        {
            "lemma": lemma.lemma,
            "number_of_words": lemma.number_of_words,
            "number_of_occurrences": lemma.number_of_occurrences
        }
        for lemma in frequency_list
    ]
    return JSONResponse(content={"lemmas": for_fe})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # uvicorn src.main:app --reload

