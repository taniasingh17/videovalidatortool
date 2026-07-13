# Video Validator Tool

A Streamlit app for validating video creative assets against compliance requirements.

## Validation Rules

| Rule | Requirement |
|---|---|
| File Type | MP4 only |
| File Size | Maximum 250 MB |
| Audio Codec | AAC only |

## Features

- Drag-and-drop or click-to-upload interface
- Processes multiple files at once
- Compliant / Non-Compliant KPI counts
- Results split into separate tables with failure reasons
- All validation runs client-side in the browser — no files are uploaded to any server
- Deduplication: re-dropping the same file is a no-op

## How to Run Locally

**Requirements:** Python 3.8+, Streamlit

```bash
pip install streamlit
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

## Deploying to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account and select this repo
4. Set the main file to `app.py` and deploy

No `requirements.txt` changes are needed — the only dependency is `streamlit`.

## How It Works

The app embeds a self-contained HTML/JS page served from a local HTTP server. Video metadata (audio codec, duration) is read entirely in the browser using [MediaInfo.js](https://github.com/buzz/mediainfo.js) (WebAssembly build) — no file data leaves the user's machine.
