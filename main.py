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
    output_format: str  # 'web' or 'pdf' or 'json'
    layout: str         # 'continuous' or 'side-by-side'

@app.post("/api/make_bilingual")
def make_bilingual(req: TranslationRequest):
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

@app.get("/")
def index():
    with open("src/static/index.html") as f:
        return HTMLResponse(f.read())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
