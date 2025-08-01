import os
import traceback
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.text_processing.nlp import lemmatize
from src.data_classes.lemma_index import LemmasIndex
from src.data_classes.bilingual_text import BilingualText
from src.tts.tts_generator import TTS_GEN, AudioOutputFormat
from src.pdf_gen.pdf_generator import generate_bilingual_pdf
from src.api.data_classes import TranslationRequest, LemmatizeRequest

from src.api.utils import (
    save_to_session_store,
    read_from_session_store,
    get_bilingual_text
)
import src.config as cfg
from src.auth.authentication import get_current_user, UserRole
from src.logging_config import setup_logging


logger = setup_logging(logger_name=__name__, log_dir=cfg.LOGS_DIR,)
TEST_MODE = False  # if True, we are using test instance of BilingualText from file instead of LLM-generated data
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


@app.get("/")
def index():
    try:
        with open("src/static/index.html") as f:
            return HTMLResponse(f.read())
    except Exception as e:
        logger.error(f"Error in index: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(content={"error": str(e), "details": traceback.format_exc()}, status_code=500)


@app.post("/api/make_bilingual")
def make_bilingual(req: TranslationRequest, user=Depends(get_current_user)):
    try:
        bt: BilingualText = get_bilingual_text(req, is_test_mode=TEST_MODE, user=user)
        bt_hash = save_to_session_store(bt)
        logger.info(f"Bilingual text save in session with hash: {bt_hash} | User: {user.username}")
        if req.output_format in ('web', 'json'):
            content = bt.model_dump()
            content["data_hash"] = hash(bt)
            # Removed test exception
            return JSONResponse(content=content)
        else:
            return JSONResponse(content={"error": f"not valid output_format: {req.output_format}"}, status_code=400)
    except Exception as e:  # todo - sort out error handling
        logger.error(f"Error in make_bilingual: {str(e)} | User: {user.username}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/make-pdf", response_class=Response)
def make_pdf(req: TranslationRequest, user=Depends(get_current_user)):
    """Endpoint to generate PDF from bilingual text data"""
    try:
        bilingual_text_instance = get_bilingual_text(req, is_test_mode=TEST_MODE, user=user)
        pdf_buffer = generate_bilingual_pdf(bilingual_text_instance)
        return Response(content=pdf_buffer, media_type="application/pdf")
    except Exception as e:
        logger.error(f"Error in make_pdf: {str(e)} | User: {user.username}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/make_audio")
def make_audio(bilingual_text_hash: int, output_format: AudioOutputFormat,
               break_time_ms: int = cfg.AUDIO_PAUSE_BREAK, ssml_only: bool = False,
               user=Depends(get_current_user)):
    """
    Endpoint to generate audio for a given bilingual text hash and output format (GET method).
    Returns a JSON with audio_url or error.
    
    If ssml_only is True, returns the generated SSML without creating audio files.
    """
    try:
        output_dir = os.path.join(cfg.SESSION_DATA_FILE_PATH, str(bilingual_text_hash))
        bilingual_text_instance = read_from_session_store(bilingual_text_hash, output_dir)
        tts = TTS_GEN()
        
        # If SSML only is requested, generate and return the SSML without creating audio
        if ssml_only:
            logger.info(f"Generating SSML only for bilingual text with hash {bilingual_text_hash} | User: {user.username}")
            ssml_content = tts.get_ssml_only(
                bln=bilingual_text_instance,
                break_time=f'{break_time_ms}ms',
                aof=output_format
            )
            # Return SSML in JSON response to be handled by frontend
            return JSONResponse(content={"ssml": ssml_content})
        
        # Otherwise, generate the audio file as before
        audio_file_name = f"audio_{bilingual_text_hash}_{output_format}"
        output_audio_file_path = os.path.join(output_dir, audio_file_name)
        logger.info(f"Generating audio for bilingual text with hash {bilingual_text_hash} to {output_audio_file_path} | User: {user.username}")
        
        tts.binlingual_to_audio(
            bln=bilingual_text_instance,
            break_time=f'{break_time_ms}ms',
            output_file_name=output_audio_file_path,
            aof=output_format
        )
        
        # Generate the URL relative to the static mount
        audio_url = f"/static/data/{bilingual_text_hash}/{audio_file_name}.mp3"
        return JSONResponse(content={"audio_url": audio_url})
    except Exception as e:
        logger.error(f"Error in make_audio: {str(e)} | User: {user.username}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download_ssml", response_class=Response)
def download_ssml(bilingual_text_hash: int, output_format: AudioOutputFormat,
                  break_time_ms: int = cfg.AUDIO_PAUSE_BREAK,
                  user=Depends(get_current_user)):
    """
    Endpoint to generate and download SSML as an XML file for a given bilingual text hash.
    Returns the SSML content directly with XML content type.
    """
    try:
        output_dir = os.path.join(cfg.SESSION_DATA_FILE_PATH, str(bilingual_text_hash))
        bilingual_text_instance = read_from_session_store(bilingual_text_hash, output_dir)
        logger.info(f"Generating SSML for download with hash {bilingual_text_hash} | User: {user.username}")
        
        tts = TTS_GEN()
        ssml_content = tts.get_ssml_only(
            bln=bilingual_text_instance,
            break_time=f'{break_time_ms}ms',
            aof=output_format
        )
        
        # Generate a filename for the download
        filename = f"ssml_{bilingual_text_hash}_{output_format}.xml"
        
        # Return the SSML as XML with the proper content disposition for download
        return Response(
            content=ssml_content,
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error in download_ssml: {str(e)} | User: {user.username}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/lemmatize")
def lemmatize_endpoint(req: LemmatizeRequest, user=Depends(get_current_user)):
    try:
        result: LemmasIndex = lemmatize(
            text=req.text,
            lang=req.language,
            filter_out_stop_words=req.filter_out_stop_words
        )
        frequency_list = sorted(result.lemmas, key=lambda lemma: lemma.number_of_occurrences, reverse=True)

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
    except Exception as e:
        logger.error(f"Error in lemmatize_endpoint: {str(e)} | User: {user.username}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/current_user")
def get_user_info(user=Depends(get_current_user)):
    try:
        return {"username": user.username, "role": user.role}
    except Exception as e:
        logger.error(f"Error in get_user_info: {str(e)} | User: {user.username}\n{traceback.format_exc()}")
        return JSONResponse(content={"error": str(e), "details": traceback.format_exc()}, status_code=500)


@app.get("/api/usage_stats")
def get_usage_stats(user_name: str = None, user=Depends(get_current_user)):
    """Get usage statistics for LLM invocations. Only Admin users can access all stats."""
    try:
        from src.auth.usage_tracker import usage_tracker
        # Only allow admins to see overall stats or stats for other users
        if user.role not in (UserRole.Admin, UserRole.SupeAdmin) and user_name != user.username:
            # Non-admin users can only see their own stats
            user_name = user.username
            
        stats = usage_tracker.get_usage_stats(user_name)
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Error in get_usage_stats: {str(e)} | User: {user.username}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/logout")
def logout():
    return Response(headers={"WWW-Authenticate": "Basic", "Clear-Site-Data": "*"})

@app.get("/login")
def login():
    with open("src/static/login.html") as f:
        return HTMLResponse(f.read())


if __name__ == "__main__":
    # Run with standard logging configuration
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"  # You can change to "debug" for more detailed logging
    )
    # To run from command line with more detailed logs:
    # uvicorn src.main:app --reload --log-level debug
