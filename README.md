# 🌍 GeoSmart GIS & AI Intelligence Platform

An end-to-end geospatial data processing system and AI-powered assistant for uploading **KML** and **Shapefile ZIP** datasets, calculating high-accuracy spatial measurements (Area, Perimeter, Length), and chatting with an AI Agent (**GeoSmart AI**) enriched with live **reverse-geocoding** and **DuckDuckGo web terrain search**.

---

## 🌟 Key Features

- **📁 Multi-Format Geospatial Uploads:** Accepts `.kml` vector files and `.zip` archives containing ESRI Shapefiles (`.shp`, `.shx`, `.dbf`, `.prj`).
- **⚡ Asynchronous Background Ingestion:** Non-blocking background worker processes geospatial files using `GeoPandas`, `PyOGRIO`, and `Shapely`.
- **🌐 Automatic CRS & UTM Projection:** Detects source Coordinate Reference Systems (e.g. WGS84 `EPSG:4326`) and projects geographic data into localized UTM zones (`estimate_utm_crs()`) for accurate metric calculations ($m^2$ and $m$).
- **📐 Automated Spatial Measurements:** Computes:
  - **Polygon & MultiPolygon:** Area ($m^2$) and Perimeter ($m$).
  - **LineString & MultiLineString:** Length ($m$).
  - **Point & MultiPoint:** Spatial coordinate extraction and property parsing.
- **🤖 GeoSmart AI Assistant (LangChain + Groq):** Integrated LLM agent (`qwen/qwen3.8-27b`) that analyzes dataset measurements, reverse geocodes feature coordinates via OpenStreetMap Nominatim, and performs web searches to answer natural questions about real-world terrain, geography, topography, and environment.
- **💻 Modern Web Dashboard:** A responsive, glassmorphic UI (`frontend/index.html`) featuring real-time file upload status, metadata cards, a feature measurement data table, and an AI chat thread with **Edit Query** and **Copy Response** controls.
- **📑 Complete OpenAPI & Postman Support:** Includes automatic Swagger UI (`/docs`), ReDoc (`/redoc`), and a ready-to-import Postman Collection (`postman_collection.json`).

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| **Geospatial Engines** | [GeoPandas](https://geopandas.org/), [PyOGRIO](https://pyogrio.readthedocs.io/), [Shapely](https://shapely.readthedocs.io/), [PyPROJ](https://pyproj4.github.io/) |
| **Database & ORM** | [PostgreSQL](https://www.postgresql.org/) + [SQLAlchemy](https://www.sqlalchemy.org/) + [Psycopg 3](https://www.psycopg.org/psycopg3/) |
| **AI / LLM Orchestration** | [LangChain](https://www.langchain.com/) + [LangChain-Groq](https://python.langchain.com/docs/integrations/chat/groq/) |
| **Geocoding & Web Search** | OpenStreetMap Nominatim API + DuckDuckGo Search (`duckduckgo-search`) |
| **Package Manager** | [`uv`](https://github.com/astral-sh/uv) (Extremely fast Python package manager) |
| **Frontend** | Vanilla HTML5, Modern CSS3 (Glassmorphism), JavaScript (Fetch API) |

---

## 📁 Repository Structure

```
AEREO/
├── app/                        # Main FastAPI Backend Application
│   ├── main.py                 # FastAPI entrypoint, app mounting, and schema auto-migrations
│   ├── database.py             # PostgreSQL SQLAlchemy engine & SessionLocal configuration
│   ├── models.py               # Database models (File & Feature tables)
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── routes/
│   │   ├── files.py            # File upload, status, and measurement endpoints
│   │   └── chat.py             # GeoSmart AI Chatbot endpoint
│   └── services/
│       ├── file_process.py     # Background worker for KML/ZIP extraction & GIS parsing
│       ├── crs.py              # Coordinate Reference System & UTM projection logic
│       └── measurement.py      # Spatial measurement calculator (Area, Perimeter, Length)
│
├── Chat_bot/                   # AI Intelligence & Search Module
│   ├── main.py                 # Standalone Chatbot FastAPI service
│   ├── geospatial_chatbot.py   # LangChain chain & prompt template configuration
│   └── search_service.py       # Centroid calculation, Nominatim reverse geocoding & web search
│
├── frontend/
│   └── index.html              # Glassmorphic web frontend UI dashboard
│
├── postman_collection.json      # Complete Postman Collection (v2.1.0)
├── POSTMAN_API_GUIDE.md        # Comprehensive Postman testing guide
├── pyproject.toml              # Project dependencies and configuration
└── .env                        # Environment configuration file
```

---

## 🗄️ Database Schema

The system uses PostgreSQL to persist file metadata and spatial features:

```mermaid
erDiagram
    FILES ||--o{ FEATURES : contains
    FILES {
        string id PK "UUID string"
        string filename "Original file name"
        string file_type "KML or SHAPEFILE_ZIP"
        int feature_count "Total feature count"
        string crs "Source CRS string"
        string projected_crs "Target projected UTM CRS string"
        string status "PROCESSING | COMPLETED | FAILED"
        text error_message "Failure explanation if any"
        datetime created_at "UTC timestamp"
    }
    FEATURES {
        int id PK "Autoincrement ID"
        string file_id FK "References FILES(id)"
        int feature_index "Index of feature (1-based)"
        string geometry_type "Polygon, LineString, Point, etc."
        text geometry_wkt "WKT Geometry string"
        string crs "Source CRS"
        json properties "JSON feature properties/attributes"
        float area "Calculated area in m²"
        float perimeter "Calculated perimeter in m"
        float length "Calculated line length in m"
        string measurement_unit "m² / m or m"
        string measurement_status "SUPPORTED | NO_MEASUREMENT | UNSUPPORTED"
    }
```

---

## ⚡ Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.14+ (or Python 3.10+)
- PostgreSQL Database running locally or remotely
- [`uv`](https://github.com/astral-sh/uv) package manager installed (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 2. Environment Configuration (`.env`)
Create a `.env` file in the project root directory:

```env
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/geospatial_api
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=qwen/qwen3.8-27b
INTERNAL_API_BASE_URL=http://127.0.0.1:8000
```

### 3. Install Dependencies
```bash
uv sync
```

### 4. Launch the Server
Start the unified FastAPI server:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Once running:
- **Web Interface:** [http://127.0.0.1:8000/frontend/](http://127.0.0.1:8000/frontend/)
- **Swagger Interactive API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc API Spec:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔌 API Endpoint Reference

| Endpoint | Method | Description | Request / Body | Response |
|---|---|---|---|---|
| `/` | `GET` | System root status | None | `{"message": "...", "status": "running"}` |
| `/health` | `GET` | Health check endpoint | None | `{"status": "healthy"}` |
| `/api/files/` | `POST` | Upload `.kml` or `.zip` dataset | `form-data`: `uploaded_file` | `FileResponse` object with `id` and `status` |
| `/api/files/{file_id}/` | `GET` | Check processing status | Path `file_id` (UUID) | Updated `FileResponse` (`COMPLETED`, `FAILED`) |
| `/api/files/{file_id}/measurements/` | `GET` | Retrieve calculated spatial measurements | Path `file_id` (UUID) | Array of feature measurements (`area`, `perimeter`, `length`, `unit`) |
| `/api/files/{file_id}/chat/` | `POST` | Ask GeoSmart AI about dataset & terrain | Path `file_id`, JSON body: `{"question": "...", "session_id": "..."}` | Conversational AI answer (`answer`) |

---

## 🧪 Testing with Postman

A complete, pre-configured Postman Collection is provided in **[`postman_collection.json`](file:///Users/santoshr/Documents/AEREO/postman_collection.json)**.

### How to Test in Postman:
1. Open **Postman** and click **Import**.
2. Select **[`postman_collection.json`](file:///Users/santoshr/Documents/AEREO/postman_collection.json)**.
3. Execute requests in sequence:
   1. `POST /api/files/` (Upload a file)
   2. `GET /api/files/{file_id}/` (Verify completion)
   3. `GET /api/files/{file_id}/measurements/` (Inspect spatial metrics)
   4. `POST /api/files/{file_id}/chat/` (Ask questions like *"Can you explain the terrain of the place?"*)

Detailed step-by-step testing instructions are available in **[`POSTMAN_API_GUIDE.md`](file:///Users/santoshr/Documents/AEREO/POSTMAN_API_GUIDE.md)**.

---

## 📄 License & Attribution

Developed as a high-performance **Geospatial Measurement Engine & AI Platform**. Powered by FastAPI, GeoPandas, LangChain, OpenStreetMap, and Groq.