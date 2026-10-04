# 📝 Text Summarization System

A modern **Extractive Text Summarization** web application built with **Python Flask** and pure NLP techniques — designed for college Natural Language Processing (NLP) lab demonstrations.

---

## 🌟 Features

- **Extractive Summarization**: Identifies and extracts the most informative sentences from the input article using:
  - **Sentence Tokenization** via regular expressions
  - **Word Frequency Scoring** (normalized term frequency, stopwords removed)
  - **Sentence Scoring** with length normalization: `score = Σ tf(w) / √N`
  - **Coherent Summary Output**: Top-scored sentences re-ordered by original position

- **Analytics Dashboard**:
  - Original vs. Summary word counts
  - Compression Ratio (% reduction in text)
  - Sentences selected / total sentences
  - Top keyword frequency breakdown

- **Interactive UI**:
  - Compression target slider (10%–70%)
  - Sentence Highlighting in original text
  - Sentence Score Analytics Table
  - Copy, Download (.txt), and Text-to-Speech output controls
  - Sample article presets (AI & NLP, Quantum Computing, Renewable Energy)

---

## 🗂️ Project Structure

```
TSA4/
├── app.py              # Flask server & API routes
├── summarizer.py       # Extractive NLP summarization engine
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Main HTML UI template
├── static/
│   ├── css/
│   │   └── style.css   # Dark glassmorphism styling
│   └── js/
│       └── main.js     # Frontend interactivity & API calls
└── README.md
```

---

## 🚀 Setup & Running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App
```bash
python app.py
```

### 3. Open in Browser
Visit → [http://127.0.0.1:5003](http://127.0.0.1:5003)

---

## 🧠 NLP Algorithm Details

| Step | Description |
|------|-------------|
| **Tokenization** | Split text into sentences using regex boundary detection (`[.!?]\s+`) |
| **Stopword Removal** | Filter common English stopwords from word list |
| **Frequency Scoring** | Compute normalized term frequency for all content words |
| **Sentence Ranking** | Score = sum of word frequencies ÷ √(sentence word count) |
| **Extraction** | Select top-N sentences by score; re-order to original sequence |

---

## 📚 Tech Stack

- **Backend**: Python 3, Flask
- **NLP**: Custom extractive algorithm (no external NLP libraries required)
- **Frontend**: HTML5, Vanilla CSS (glassmorphism), Vanilla JavaScript
- **Fonts**: Plus Jakarta Sans, JetBrains Mono (Google Fonts)
- **Icons**: Font Awesome 6

---

## 📋 API Endpoint

### `POST /api/summarize`

**Request Body (JSON)**:
```json
{
  "text": "Your long article or paragraph text here...",
  "compression": 30
}
```

**Response (JSON)**:
```json
{
  "success": true,
  "summary": "Extracted summary sentences...",
  "original_word_count": 150,
  "summary_word_count": 45,
  "compression_ratio": 70.0,
  "top_keywords": { "language": 4, "nlp": 3 },
  "sentence_scores": [ ... ],
  "selected_indices": [0, 2]
}
```

---

*NLP Lab Project — College Demo Application*
