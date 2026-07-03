# SmartFarmingAI 🌱

> **AI-Powered Smart Farming Advice System**
> Built with **IBM watsonx.ai**, **IBM Granite Models**, **Flask**, **LangChain RAG**, and **ChromaDB**

---

## Overview

SmartFarmingAI is a production-ready, multi-agent agricultural intelligence platform that provides Indian farmers with:

| Feature | Technology |
|---|---|
| Crop Advisory | IBM Granite 3.x Instruct |
| Weather Intelligence | OpenWeatherMap + Granite |
| Soil Health Analysis | Rule-based + Granite AI |
| Pest & Disease Detection | IBM Granite Vision |
| Market Intelligence | Agmarknet API + Granite |
| Knowledge Base (RAG) | LangChain + ChromaDB + Granite Embeddings |
| Chatbot | Master Orchestrator (5 agents) |
| Reports | PDF + CSV + Excel |

---

## Quick Start

### 1. Clone and set up environment

```bash
git clone https://github.com/your-org/SmartFarmingAI.git
cd SmartFarmingAI
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
# Edit .env and fill in:
#   IBM_API_KEY, IBM_PROJECT_ID, IBM_WATSONX_URL
#   WEATHER_API_KEY (from openweathermap.org)
#   FLASK_SECRET_KEY
```

### 3. Run the application

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## Docker Deployment

```bash
# Development
docker-compose up --build

# Production (with Nginx)
docker-compose --profile production up -d
```

---

## Project Structure

```
SmartFarmingAI/
├── app.py                  # Flask application factory
├── config.py               # Configuration (reads from .env)
├── requirements.txt
├── .env.example            # Environment variables template
│
├── agents/                 # Multi-agent AI architecture
│   ├── base_agent.py       # Abstract base (IBM Granite client)
│   ├── crop_agent.py       # Agent 1: Crop Advisory
│   ├── weather_agent.py    # Agent 2: Weather & Irrigation
│   ├── soil_agent.py       # Agent 3: Soil Health
│   ├── pest_agent.py       # Agent 4: Pest & Disease (Granite Vision)
│   ├── market_agent.py     # Agent 5: Market Intelligence
│   └── orchestrator.py     # Master Orchestrator (intent → route → synthesise)
│
├── rag/                    # Retrieval-Augmented Generation pipeline
│   ├── loader.py           # PDF/DOCX/TXT/CSV loader
│   ├── chunker.py          # Recursive text splitter
│   ├── embeddings.py       # Granite Embedding wrapper
│   ├── vector_store.py     # ChromaDB manager
│   ├── retriever.py        # Similarity retriever
│   └── generator.py        # RAG answer generator
│
├── tools/                  # External API integrations
│   ├── weather_api.py      # OpenWeatherMap
│   ├── soil_analysis.py    # Rule-based soil expert
│   ├── market_api.py       # Agmarknet / synthetic prices
│   ├── image_classifier.py # PIL + OpenCV preprocessor
│   └── government_schemes.py # Scheme data + RAG
│
├── database/               # SQLAlchemy ORM
│   ├── db.py               # SQLAlchemy instance
│   ├── models.py           # All 10 database models
│   └── __init__.py
│
├── routes/                 # Flask blueprints
│   ├── api.py              # /api/* JSON endpoints
│   ├── main.py             # Home, Dashboard, Knowledge Base
│   ├── chat.py, weather.py, crop.py, soil.py, pest.py, market.py
│   ├── profile.py, reports.py
│   └── __init__.py
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Layout (navbar, footer, dark mode)
│   ├── index.html, dashboard.html, chatbot.html
│   ├── weather.html, crop.html, soil.html, pest.html
│   ├── market.html, profile.html, reports.html, knowledge_base.html
│
├── static/
│   ├── css/style.css       # Nature-green theme
│   └── js/app.js           # Dark mode, toast, utils
│
├── data/knowledge_base/    # Place PDF/DOCX farming documents here
├── uploads/                # User image uploads (auto-created)
├── reports/                # Generated reports (auto-created)
├── database/               # SQLite DB + ChromaDB (auto-created)
│
└── tests/test_api.py       # pytest test suite
```

---

## REST API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Master orchestrator chatbot |
| POST | `/api/crop` | Crop advisory agent |
| GET/POST | `/api/weather` | Weather + irrigation advisory |
| POST | `/api/soil` | Soil health analysis |
| POST | `/api/pest` | Pest/disease detection (image or text) |
| POST | `/api/market` | Market intelligence |
| GET | `/api/schemes` | Government schemes (with `?q=` search) |
| POST | `/api/rag` | RAG knowledge base query |
| GET | `/api/history` | Chat history for current session |
| GET | `/report/csv/recommendations` | Download CSV report |
| GET | `/report/pdf/recommendations` | Download PDF report |

### Example: Chat API

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What crop should I grow in black cotton soil?", "crop": "Cotton", "location": "Maharashtra"}'
```

### Example: Soil Analysis

```bash
curl -X POST http://localhost:5000/api/soil \
  -H "Content-Type: application/json" \
  -d '{"ph": 6.5, "nitrogen": 280, "phosphorus": 15, "potassium": 150, "moisture": 55}'
```

### Example: Pest Detection

```bash
curl -X POST http://localhost:5000/api/pest \
  -F "image=@/path/to/leaf.jpg" \
  -F "crop=Rice" \
  -F "location=Tamil Nadu"
```

---

## Adding Knowledge Base Documents

Place any of the following files in `data/knowledge_base/`:
- Government scheme PDFs
- Agricultural manuals (PDF, DOCX)
- Soil health guides
- Crop calendars (CSV)

Then trigger indexing:

```bash
python -c "
from rag import RAGGenerator
result = RAGGenerator().index_knowledge_base('./data/knowledge_base')
print(result)
"
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Security

- **Credentials** are never hardcoded — always loaded from `.env`
- **File uploads** are validated for extension and size
- **Inputs** are sanitised before database operations
- **Session** management uses Flask-Session with signed cookies

---

## Technologies

- **IBM watsonx.ai** — Foundation model inference platform
- **IBM Granite 3.x Instruct** — Main language model
- **IBM Granite Vision** — Image-based pest detection
- **IBM Granite Embedding** — RAG document embeddings
- **LangChain** — RAG pipeline orchestration
- **ChromaDB** — Vector database
- **Flask 3** — Web framework
- **SQLAlchemy + SQLite** — Relational database
- **Bootstrap 5** — Responsive UI
- **Chart.js** — Data visualisation
- **OpenCV + Pillow** — Image preprocessing

---

## License

MIT License — Free to use, modify, and distribute.

---

*Built for IBM hackathon — SmartFarmingAI 2025*
