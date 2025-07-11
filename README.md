# Learn Language with Texts

A comprehensive tool for language learning that implements various effective learning techniques including the Ilya Frank's Reading Method, audio mirroring, and ANKI cards integration (upcoming).

## Features

- **Text Analysis and Translation**
  - Split text into syntagmas (meaningful chunks that can be pronounced in one breath)
  - Automatic translation with context preservation
  - Multiple output formats (web page, PDF, raw JSON)
  - Customizable layout options:
    - Continuous format with translations
    - Side-by-side tabular format
    - Raw JSON format
    - Generation of audio files with TTS models,  using customizable SSML templates.

- **Usage Tracking and Limits**
  - Detailed tracking of LLM usage metrics (input text length, input/output tokens)
  - Per-user usage thresholds and restrictions
  - Comprehensive usage statistics for administrators
  - Automatic prevention of threshold exceeding

- **Learning Methods**
  - Ilya Frank's Reading Method implementation
  - Audio materials for pronunciation mirroring
  - ANKI cards integration (planned)

## Technologies Used

- **Large Language Models (LLM):** Used for advanced text analysis and translation tasks.
- **Text-to-Speech (TTS) and SSML:** Converts text to audio using TTS models and Speech Synthesis Markup Language (SSML) for expressive speech output.
- **Lemmatization Libraries:** Utilizes NLP libraries (such as spaCy) for lemmatization and syntagma splitting.
- **FastAPI:** Backend API framework for serving endpoints.
- **Pure HTML, CSS, JavaScript:** For the web frontend.

## Requirements

- Python 3.12+
- FastAPI
- Modern web browser
- Additional dependencies listed in `pyproject.toml`

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

### Launch
```bash
uvicorn src.main:app --reload
```

## Usage

1. Start the application using the launch command above
2. Open your web browser and navigate to `http://localhost:8000`
3. Input your text in the source language
4. Select your desired output format and layout
5. Click "Go ahead" to process the text

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

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Add your license information here]

## Contact

[Add your contact information here]