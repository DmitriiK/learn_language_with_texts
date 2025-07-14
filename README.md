# Learn Language with Texts

A comprehensive tool for language learning that implements various effective learning techniques including the Ilya Frank's Reading Method, audio mirroring, and ANKI cards integration (upcoming).

  ## Features

  - Split text into syntagmas (meaningful chunks that can be pronounced in one breath)
  - Automatic translation with context preservation
  - Multiple output formats (web page, PDF, raw JSON)
  - Customizable layout options:
    - Continuous format with translations
    - Side-by-side tabular format
    - Raw JSON format
    - Generation of audio files with TTS models, using customizable SSML templates
  - Comprehension questions related to the text (0-9 questions):
    - Interactive expandable/collapsible answers in web view
    - Included as a formatted section in PDF output

  - Detailed tracking of LLM usage metrics (input text length, input/output tokens)
  - Per-user usage thresholds and restrictions
  - Comprehensive usage statistics for administrators
  - Automatic prevention of threshold exceeding

  - Ilya Frank's Reading Method implementation
  - Audio materials for pronunciation mirroring
  - Comprehension questions with expandable answers to test understanding
  - ANKI cards integration (planned)

## TO DO

## Technologies Used


## Requirements


## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd learn_language_with_texts
```

2. Install dependencies:
```bash
pip install -e .
```

## Setup and Deployment

### Initial Setup
```bash
 python -m src.deploy.download_nlp
```

## Launching the FastAPI App

To start the FastAPI server on your Azure VM (or any Linux environment):

1. Ensure you have created and installed dependencies in your Python virtual environment named `.venv`.
2. If you get a "Permission denied" error, make the script executable:

```bash
chmod +x ./start_server.sh
```

3. Use the provided script to activate the virtual environment and launch the server:

```bash
./start_server.sh
```

This will:
- Activate the `.venv` virtual environment
- Start the FastAPI app with Uvicorn, listening on all interfaces at port 8000

You can then access the app at `http://<your-vm-ip>:8000/` from your browser.

## Usage

1. Start the application using the launch command above
2. Open your web browser and navigate to `http://localhost:8000`
3. Input your text in the source language
4. Select your desired output format and layout
5. Adjust the number of comprehension questions (0-9, default: 2)
6. Choose additional options like lemmatization if needed
7. Click "Go ahead" to process the text

## Project Structure

```
src/
├── api/            - FastAPI endpoints and utilities
├── data_classes/   - Core data structures
├── pdf_gen/        - PDF generation functionality
├── prompts/        - System prompts and templates
├── static/         - Web frontend assets
├── text_processing/- Text analysis and translation
└── tts/           - Text-to-speech functionality
```

## Screenshots

### Main Page
![Main Page](grafic/main_page.png)
*The application's main page where users can input text and select processing options.*

### Results Page
![Results Page](grafic/resutls_page.png)
*The results page displaying the processed bilingual text with translations and interactive comprehension questions with expandable answers.*

### Lemmatization Process
![Lemmatization](grafic/lemmatization.png)
*Visualization of the lemmatization process used for text analysis.*


## Contact

telegram: @dklmn