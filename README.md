# SkillMatch AI

A Streamlit app that compares the skills in a resume with those required by a job description. It uses LangChain and Groq to extract and match skills, then calculates a skill coverage score.

## Features

- Paste text or upload a PDF for either document.
- Preview extracted PDF text before analysis.
- View matched skills, missing skills, and a percentage score.
- Download a PDF analysis report.
- Adjust temperature, retry count, and request timeout in the sidebar.
- Reuse PDF text and the most recent completed analysis within the current session.

## Requirements

- Python 3.12 or newer.
- A Groq API key from the [Groq console](https://console.groq.com/keys).
- Internet access for AI requests.

## Setup

Run these commands from the repository root.

### Install with pip

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1` instead.

### Install with uv

Alternatively, install the dependencies recorded in the lockfile:

```bash
uv sync --locked
```

### Configure the AI service

Create a `.env` file in the repository root:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
AI_MODEL=openai/gpt-oss-120b
```

`GROQ_API_KEY` is required. `AI_MODEL` is optional and defaults to `openai/gpt-oss-120b`; set it to a model available to your Groq account.

The `.env` file is ignored by Git. Document text is sent to Groq for skill extraction, and extracted skill lists are sent for matching.

## Run the app

With the virtual environment activated:

```bash
python -m streamlit run ats_checker.py
```

Or with uv:

```bash
uv run streamlit run ats_checker.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

1. Provide your resume in the left column and the job description in the right column.
2. Choose **Paste Text** or **Upload PDF** independently for each document.
3. For uploaded PDFs, review the extracted text preview.
4. Click **Analyze Resume**.
5. Review the score and skill lists, then download the PDF report if needed.

PDFs must contain selectable text. Scanned or image-only documents require OCR before uploading. Unlock password-protected PDFs before use.

## How scoring works

The app extracts skills from both documents in parallel, then makes a separate AI request to compare the skill lists.

```text
Score = matched JD skills / (matched JD skills + missing JD skills) × 100
```

If no job description skills are identified, the score is 0 and the app explains that it is not meaningful. This score measures skill coverage; it is not a complete ATS evaluation or a prediction of hiring success. AI extraction and matching can make mistakes, so review the results.

## Performance and troubleshooting

- **Slow analysis:** A new analysis uses three AI requests: two parallel extraction requests followed by matching. Response time depends on document length, the configured model, service latency, and retries. The sidebar timeout applies to individual requests, not the entire analysis.
- **Repeated analysis:** The most recent successful result is reused when document content and AI settings match. Changing either document or the settings starts a new analysis. These caches are kept in the current Streamlit session.
- **PDF has no readable text:** Apply OCR or paste the text directly. Empty, invalid, and password-protected files produce an error.
- **Missing API key:** Set `GROQ_API_KEY` in `.env` and restart the app.
- **AI request fails:** Check the API key, model availability, account limits, and network connection. Increasing retries can increase total wait time.

## Tests

Run from the repository root:

```bash
python -m unittest discover -s tests -v
```

With uv:

```bash
uv run python -m unittest discover -s tests -v
```

Tests cover multi-page PDF extraction, invalid and locked files, upload controls, and reuse of completed analyses. AI requests are mocked in the app tests; they do not require a live Groq request.

## Project structure

```text
ats_checker.py    Streamlit application
models/           Pydantic skill and result schemas
prompts/          Extraction and matching prompts
services/         AI pipeline, model configuration, and scoring
utils/            PDF text extraction and report generation
tests/            Automated tests
pyproject.toml    Project metadata and uv dependencies
uv.lock           Locked dependency versions for uv
requirements.txt  Dependency minimums for pip installation
```
