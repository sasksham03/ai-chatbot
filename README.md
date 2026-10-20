# CodeBuddy - AI Chatbot (Python + Flask + NLP)

A ready-to-use chatbot with a modern web chat interface. It understands user messages using
**TF-IDF + cosine similarity** (scikit-learn), works fully **offline** and needs **no API key**.

## Features
- NLP intent matching (word + character n-grams, tolerant to small typos)
- Web chat UI: typing indicator, quick-reply chips, timestamps, clear button, mobile friendly
- Remembers your name ("my name is Saksham")
- Safe calculator ("calculate 12*8")
- Live time and date, jokes, programming help, resume/interview/study tips
- Easy to extend: just edit `intents.json`

## Project structure
```
ai-chatbot/
├── app.py              # Flask server (routes: / and /chat)
├── chatbot.py          # NLP engine (also runs in the terminal)
├── intents.json        # Training data: patterns and responses
├── requirements.txt
├── templates/index.html
└── static/
    ├── style.css
    └── script.js
```

## Run it
```bash
# 1. (optional) create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 2. install dependencies
pip install -r requirements.txt

# 3. start the web app
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

Terminal-only mode: `python chatbot.py`

## Add your own answers
Open `intents.json` and add a new block:
```json
{
  "tag": "college",
  "patterns": ["tell me about your college", "which college"],
  "responses": ["I'm a bot, but my creator studies at NIET!"]
}
```
Restart the app. No retraining step is needed.

## How it works
1. Every example sentence in `intents.json` is turned into a TF-IDF vector.
2. Your message is converted to the same kind of vector.
3. Cosine similarity finds the closest example; if the score is above `THRESHOLD`
   (0.30 in `chatbot.py`) its intent's reply is used, otherwise a fallback reply is returned.

## Ideas to extend
- Connect an LLM API (Claude/OpenAI) for open-ended answers when the score is low
- Add a database (MySQL) to store chat history
- Add voice input using the browser Web Speech API
- Deploy free on Render or PythonAnywhere

## Resume description
**AI-Based Chatbot** | Python, Flask, scikit-learn, NLP, HTML, CSS, JavaScript
- Built an NLP chatbot using TF-IDF vectorization and cosine similarity for intent classification across 20+ intents.
- Developed a responsive Flask web interface with a REST `/chat` endpoint, typing indicator and quick-reply suggestions.
