from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from src.text_processing.llm_communicator import create_bilingual_text

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
    output_format: str  # 'web' or 'pdf'
    layout: str         # 'continuous' or 'side-by-side'

@app.post("/api/translate")
def translate(req: TranslationRequest):
    try:
        result = create_bilingual_text(req.source_text, req.target_language)
        # TODO: Format result according to req.output_format and req.layout
        # For now, just return as JSON
        return JSONResponse(content=result.dict())
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/")
def index():
    with open("src/static/index.html") as f:
        return HTMLResponse(f.read())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
