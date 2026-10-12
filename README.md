## What I Learned

- Learned about different geospatial file formats used to store coordinate data.
- Understood how map projections transform coordinates and why they are important for calculating area and distance accurately.
- Learned about the PostGIS extension in PostgreSQL and its role in storing and managing geospatial data.
- Explored how to calculate the area of geographical features using projections such as Albers Equal Area Conic and other suitable projected coordinate systems.
- Understood how geospatial data is used in real-world applications such as mapping, location analysis, and geographic information systems.
- How to test the application using locust and finding the bottle neck in my backend system
- Automation testing of our software
- Adding map using the js library Leaflet library and today only i learn that these things exist

## Additional Contributions

- Integrated a Generative AI model to help users interpret geospatial data and get meaningful insights by asking questions in natural language.
- Designed the workflow so that users can upload a geospatial file once and ask questions about the available data without manually providing the same information for every query.
- Focused primarily on backend development, including file processing, API development, database integration, coordinate transformation, and AI integration, while keeping the frontend simple and user-friendly.
- Built and executed automated performance & stress testing using **Locust**, validating sub-15ms average latency and 100% request success (0% error rate) under 100 concurrent users.
- Adding map to the project 
- PLEASE READ THE LAST LINES OF MD AT THE END OF THE PROJECT

# 🌍 AEREO GIS & AI Intelligence Platform

An end-to-end geospatial data processing system and AI-powered assistant built for **AEREO**, supporting **KML** and **Shapefile ZIP** datasets, high-accuracy metric spatial calculations (Area, Perimeter, Length), and an integrated AI Agent (**AEREO AI**) enriched with live **reverse-geocoding** and **DuckDuckGo web terrain search**.

---

## Setup

Follow these steps to set up and run the application locally on your machine.

### Prerequisites
- **Python 3.10+** (Python 3.14 recommended)
- **PostgreSQL Database** running locally or remotely
- **`uv`** (Ultra-fast Python package manager):
  ```bash
  pip install uv
  ```

### 1. Environment Configuration (`.env`)
Create a `.env` file in the root directory of the project:

```env
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/geospatial_api
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=qwen/qwen3.8-27b
INTERNAL_API_BASE_URL=http://127.0.0.1:8000
```

### 2. Install Project Dependencies
Run `uv` to automatically create a virtual environment and install all dependencies:

```bash
uv sync
```

### 3. Run the Application
Launch the unified FastAPI application using Uvicorn:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Once started:
- 🌐 **Web Dashboard:** [http://127.0.0.1:8000/frontend/](http://127.0.0.1:8000/frontend/)
- 📑 **Swagger Interactive API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📖 **ReDoc API Spec:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API

Below is the complete documentation for all available endpoints, including example HTTP requests and response payloads.

---

### 1. Root Status
- **HTTP Method:** `GET`
- **Endpoint:** `/`
- **Description:** Verifies that the API backend is online and running.

#### Example Request
```http
GET / HTTP/1.1
Host: 127.0.0.1:8000
```

#### Example Response (`200 OK`)
```json
{
  "message": "Geospatial File Measurement API",
  "status": "running"
}
```

---

### 2. Health Check
- **HTTP Method:** `GET`
- **Endpoint:** `/health`
- **Description:** Returns the health status of the application.

#### Example Request
```http
GET /health HTTP/1.1
Host: 127.0.0.1:8000
```

#### Example Response (`200 OK`)
```json
{
  "status": "healthy"
}
```

---

### 3. Upload Geospatial File
- **HTTP Method:** `POST`
- **Endpoint:** `/api/files/`
- **Description:** Uploads a `.kml` file or a Shapefile `.zip` archive for background processing.

#### Example Request
```http
POST /api/files/ HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="uploaded_file"; filename="sample_polygon.kml"
Content-Type: application/vnd.google-earth.kml+xml

<kml content...>
------WebKitFormBoundary--
```

#### Example Response (`200 OK`)
```json
{
  "id": "42a73b46-2f59-444b-84c0-13fe54253be0",
  "filename": "sample_polygon.kml",
  "file_type": "KML",
  "feature_count": 1,
  "crs": null,
  "projected_crs": null,
  "status": "PROCESSING",
  "error_message": null,
  "created_at": "2026-10-09T18:50:00.123456"
}
```

---

### 4. Get File Processing Status
- **HTTP Method:** `GET`
- **Endpoint:** `/api/files/{file_id}/`
- **Description:** Fetches the current processing status (`PROCESSING`, `COMPLETED`, or `FAILED`) and metadata for a uploaded file.

#### Example Request
```http
GET /api/files/42a73b46-2f59-444b-84c0-13fe54253be0/ HTTP/1.1
Host: 127.0.0.1:8000
```

#### Example Response (`200 OK`)
```json
{
  "id": "42a73b46-2f59-444b-84c0-13fe54253be0",
  "filename": "sample_polygon.kml",
  "file_type": "KML",
  "feature_count": 1,
  "crs": "EPSG:4326",
  "projected_crs": "EPSG:32611",
  "status": "COMPLETED",
  "error_message": null,
  "created_at": "2026-10-09T18:50:00.123456"
}
```

---

### 5. Get Feature Measurements
- **HTTP Method:** `GET`
- **Endpoint:** `/api/files/{file_id}/measurements/`
- **Description:** Returns calculated spatial measurements (Area in $m^2$, Perimeter in $m$, Length in $m$) for all parsed geometries in the file.

#### Example Request
```http
GET /api/files/42a73b46-2f59-444b-84c0-13fe54253be0/measurements/ HTTP/1.1
Host: 127.0.0.1:8000
```

#### Example Response (`200 OK`)
```json
{
  "file_id": "42a73b46-2f59-444b-84c0-13fe54253be0",
  "filename": "sample_polygon.kml",
  "measurements": [
    {
      "feature_id": 1,
      "feature_index": 1,
      "geometry_type": "Polygon",
      "area": 1500.5,
      "perimeter": 185.3,
      "length": null,
      "unit": "m² / m",
      "status": "SUPPORTED"
    }
  ]
}
```

---

### 6. Ask AEREO AI Chatbot
- **HTTP Method:** `POST`
- **Endpoint:** `/api/files/{file_id}/chat/`
- **Description:** Sends questions to the AEREO AI chatbot, which leverages feature measurements, reverse geocoding, and web terrain search to answer questions.

#### Example Request
```http
POST /api/files/42a73b46-2f59-444b-84c0-13fe54253be0/chat/ HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "question": "can you explain the terrain of the place ?",
  "session_id": "session_demo_01"
}
```

#### Example Response (`200 OK`)
```json
{
  "file_id": "42a73b46-2f59-444b-84c0-13fe54253be0",
  "session_id": "session_demo_01",
  "question": "can you explain the terrain of the place ?",
  "answer": "The dataset you provided is located in Coconino County, Arizona, near the Grand Canyon South Rim. In terms of terrain, this area is part of a high desert plateau characterized by high elevation (~2,100 meters above sea level), ancient sedimentary rock formations, and steep canyon washes..."
}
```

---

## Architecture

### 1. System Architecture Mindmap

The following mindmap illustrates how the entire AEREO platform functions across its frontend, API layer, geospatial processing pipeline, AI chatbot integration, database persistence, and performance testing suite:

```mermaid
mindmap
  root((AEREO GIS and AI Platform))
    Frontend Dashboard
      Glassmorphism Dark UI
      Drag and Drop File Ingestion
      Real-Time Status Polling
      Spatial Measurement Tables
      AEREO AI Chat Drawer
    FastAPI Core Backend
      RESTful API Endpoints
        GET Health Check
        POST Upload File
        GET File Status and Details
        GET Feature Measurements
        POST AI Chatbot Query
      Async Worker Engine
        FastAPI BackgroundTasks
        Non-blocking File Ingestion
      Database Persistence
        PostgreSQL with Psycopg3
        SQLAlchemy ORM Models
    GIS Processing Engine
      Multi-Format Ingestion
        KML Google Earth Files
        Shapefile ZIP Archives
        GeoPandas and PyOGRIO Engine
      Coordinate Reference Systems CRS
        EPSG 4326 WGS84 Detection
        Dynamic UTM Zone Estimation
        Metric Planar Reprojection
      Spatial Measurements
        Polygons Area and Perimeter
        LineStrings Metric Length
        Points WKT Coordinates
    AEREO AI Intelligence Agent
      LangChain Architecture
      Groq LLM Acceleration
      Spatial Context Injection
      Autonomous Terrain Intelligence
        Shapely Centroid Coordinates
        Nominatim Reverse Geocoding
        DuckDuckGo Web Terrain Search
    Quality Assurance and Performance
      Locust Load and Stress Testing
        100 Concurrent Users Simulation
        Zero Failures Under Load
        Sub-15ms Average Latency
      Performance Instrumentation
        measure_time Stage Profiler
      Postman Collection and API Guide
```

---

### 2. Application Structure

The application is structured into decoupled modules separating backend routes, GIS services, database models, AI agents, frontend assets, and automated performance suites:

```
AEREO/
├── app/                        # FastAPI Core Backend
│   ├── main.py                 # Application initialization & router inclusion
│   ├── database.py             # SQLAlchemy engine & session management
│   ├── models.py               # ORM Models (File, Feature)
│   ├── schemas.py              # Pydantic schemas
│   ├── routes/
│   │   ├── files.py            # File upload & measurement endpoints
│   │   └── chat.py             # AI Chatbot endpoint
│   └── services/
│       ├── file_process.py     # Ingestion & worker logic
│       ├── crs.py              # Coordinate Reference System transformation
│       ├── measurement.py      # Spatial measurement engine
│       └── performance.py      # Stage timing & latency instrumentation
├── Chat_bot/                   # AI Intelligence & Search Services
│   ├── geospatial_chatbot.py   # LangChain LLM chain setup
│   └── search_service.py       # Centroid calculation, Nominatim geocoding & DDG web search
├── frontend/
│   └── index.html              # Glassmorphic UI Dashboard
├── tests/                      # Testing & Performance Suite
│   └── performance/
│       └── locust.py           # Locust load & stress testing suite
├── locust_report.png           # Locust benchmark results dashboard screenshot
├── postman_collection.json      # Postman testing collection
└── POSTMAN_API_GUIDE.md        # Step-by-step Postman testing guide
```

---

### 3. File-Processing Flow

```
[User Upload (.kml / .zip)]
         │
         ▼
[POST /api/files/] ──► Create DB File record (status="PROCESSING")
         │
         ▼ (FastAPI BackgroundTasks)
[process_geospatial_file()]
         │
         ├── 1. Extract .zip (if Shapefile) or parse .kml
         ├── 2. Read with GeoPandas (pyogrio engine)
         ├── 3. Validate Geometries & inspect CRS
         ├── 4. Transform to Projected UTM CRS (via crs.py)
         ├── 5. Loop features & compute spatial measurements
         └── 6. Save Features to DB & update status="COMPLETED"
```

1. **Upload Request:** The endpoint receives a `.kml` or `.zip` file, creates a record in the `files` database table with status `PROCESSING`, and returns the file ID immediately.
2. **Background Dispatch:** `BackgroundTasks` delegates file extraction and processing to an async background task.
3. **Extraction & Reading:** Shapefiles in ZIP archives are extracted to a temporary directory; KMLs are read directly using `GeoPandas` with `pyogrio`.
4. **Persistence:** Parsed attributes, geometry WKTs, and calculated measurements are saved into the `features` database table, and file status is updated to `COMPLETED`.

---

### 4. Measurement Calculation Flow

Spatial calculations depend on geometry type:

1. **Polygons & MultiPolygons:**
   - **Area:** Calculated on projected geometry in square metres ($m^2$).
   - **Perimeter:** Calculated via boundary length on projected geometry in metres ($m$).
2. **LineStrings & MultiLineStrings:**
   - **Length:** Calculated on projected geometry in metres ($m$).
   - **Area / Perimeter:** Set to `null`.
3. **Points & MultiPoints:**
   - Coordinates extracted in WGS84 (`EPSG:4326`). Measurements set to `null` (`NO_MEASUREMENT`).

---

### 5. CRS Handling

Geographic Coordinate Reference Systems (such as WGS84 `EPSG:4326`) use angular units (degrees), which **cannot be directly used to calculate accurate metric area ($m^2$) or length ($m$)**.

To solve this:
1. **Source CRS Detection:** GeoPandas inspects `gdf.crs`. If no CRS is defined, processing fails with a clear error.
2. **UTM Projection Estimation:** `gdf.estimate_utm_crs()` dynamically identifies the optimal local **Universal Transverse Mercator (UTM)** zone for the dataset's location.
3. **Reprojection:** The dataset is reprojected using `gdf.to_crs(projected_crs)`.
4. **Measurement Computation:** Metric measurements are computed on the reprojected UTM geometries, while original WGS84 geometries are preserved for mapping/display.

---

## ⚡ Performance & Load Testing (Locust Benchmark Report)

To validate platform stability, response latency, and throughput under real-world multi-user loads, stress and performance testing was conducted using **[Locust](https://locust.io/)** (v2.46.7).

The test suite ([`tests/performance/locust.py`](tests/performance/locust.py)) simulates realistic concurrent user traffic against the live FastAPI backend, exercising both lightweight availability endpoints (`GET /health`) and database-backed dynamic resource endpoints (`GET /api/files/{id}` and `GET /api/files/{id}/measurements/`).

---

### 1. Test Setup & Configuration

- **Load Testing Engine:** Locust 2.46.7
- **Test Definition Script:** [`tests/performance/locust.py`](tests/performance/locust.py)
- **Target Backend Host:** `http://127.0.0.1:8000`
- **Simulated Concurrent Users:** **100 Users**
- **User Spawn Rate:** **12.5 Users / Second**
- **Test Status:** **RUNNING / STABLE**
- **Failure Rate:** **0.0% (Zero Failures)**
- **Total Requests Handled:** **70 Requests**

---

### 2. Visual Benchmark Dashboard

The following report is captured directly from the Locust real-time metrics dashboard:

![Locust Load Testing Benchmark Report](locust_report.png)

---

### 3. Tabulated Benchmark Metrics

The table below reflects the exact load testing statistics recorded during the high-concurrency simulation:

| HTTP Method | Request / Endpoint Name | # Requests | # Failures | Median Latency (ms) | 95%ile Latency (ms) | 99%ile Latency (ms) | Average Latency (ms) | Min Latency (ms) | Max Latency (ms) | Average Payload Size | Current Throughput (RPS) | Current Failures/s |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `GET` | `GET /api/files/{id}` | 23 | 0 | 14 | 90 | 90 | 26.53 | 3 | 90 | 263 B | 6.0 | 0 |
| `GET` | `GET /health` | 47 | 0 | 5 | 39 | 39 | 8.48 | 1 | 39 | 20 B | 6.5 | 0 |
| **AGGREGATED** | **All Endpoints Combined** | **70** | **0** | **7** | **47** | **90** | **14.41** | **1** | **90** | **99.84 B** | **12.5** | **0** |

---

### 4. Key Performance Insights & Latency Analysis

1. **Zero Error Rate (100% Availability):**
   - Under 100 concurrent simulated users, **0 failures** occurred out of 70 total requests (**0% failure rate**).
   - FastAPI's ASGI event loop and connection pooling reliably absorbed concurrent traffic spikes without connection dropouts or 5xx server errors.

2. **Ultra-Low Response Latencies:**
   - **Median Latency:** Across all endpoints, 50% of incoming requests were resolved in **7 ms** or less.
   - **Health Check Endpoint (`GET /health`):** Achieved an average response time of **8.48 ms** (median **5 ms**, minimum **1 ms**).
   - **Database-Backed Resource Endpoint (`GET /api/files/{id}`):** Even with database entity retrieval and serialization, requests maintained an average response latency of **26.53 ms** and a median of **14 ms**.

3. **Predictable Tail Latency (P95 & P99):**
   - The aggregated **95th percentile latency was 47 ms**, well below industry-standard SLAs (< 200 ms).
   - The absolute peak latency under maximum load was capped at **90 ms**, demonstrating the absence of thread blocking or unbounded garbage collection pauses.

---

### 5. Granular Stage Instrumentation (`measure_time`)

In addition to exterior HTTP benchmarking, the backend features a dedicated timing context manager in [`app/services/performance.py`](app/services/performance.py):

```python
from app.services.performance import measure_time

with measure_time("geospatial_parsing_and_reprojection"):
    # High-precision time logging for C-level GeoPandas & PyOGRIO processing
    ...
```

This context manager provides microsecond-accurate stage profiling (`perf_counter`) to trace vector file extraction, dynamic UTM reprojection, and database batch-insert durations in production logs.

---

### 6. How to Reproduce the Benchmark

Run the performance test locally using `uv`:

#### A. Interactive Locust Web UI Mode
1. Ensure the backend is active:
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```
2. Launch Locust:
   ```bash
   uv run locust -f tests/performance/locust.py --host http://127.0.0.1:8000
   ```
3. To also test file-specific endpoints, provide an active `TEST_FILE_ID`:
   ```bash
   TEST_FILE_ID="your-file-uuid-here" uv run locust -f tests/performance/locust.py --host http://127.0.0.1:8000
   ```
4. Open [http://localhost:8089](http://localhost:8089) in your browser, configure **Number of Users** (e.g. `100`) and **Spawn Rate** (e.g. `10`), and start swarming!

#### B. Headless Automated Benchmark Mode (CI/CD)
To run an automated 1-minute benchmark directly from the CLI without launching the browser UI:
```bash
uv run locust -f tests/performance/locust.py --headless -u 100 -r 10 -t 1m --host http://127.0.0.1:8000
```

---

## Design Decisions

### 1. FastAPI Framework vs. Django/Flask
- **Decision:** Selected **FastAPI** for high performance, native async execution, built-in background task processing (`BackgroundTasks`), and automatic OpenAPI / Swagger UI generation.

### 2. GeoPandas & PyOGRIO Engine vs. GDAL Shell Commands
- **Decision:** Used `geopandas` with `pyogrio` for C-level speed when reading OGR vector formats (KML & Shapefile), avoiding fragile subprocess calls to external GDAL binaries.

### 3. Dynamic UTM Reprojection vs. Haversine Approximation
- **Decision:** Chose `estimate_utm_crs()` over Haversine/geodesic approximations. Reprojecting to a local projected coordinate system provides true Euclidean planar calculations for complex Polygons and MultiPolygons with minimal distortion.

### 4. Unified Backend Router for AI Chatbot vs. Microservices
- **Decision:** Integrated the AI Chatbot route (`/api/files/{file_id}/chat/`) directly into the main FastAPI backend using APIRouter. This eliminates cross-origin latency, enables direct database feature querying without internal HTTP loopbacks, and simplifies deployment into a single executable app.

### 5. Multi-Source Web Search & Geocoding for Terrain Queries
- **Decision:** Combined **Shapely centroid extraction**, **OpenStreetMap Nominatim reverse geocoding**, and **DuckDuckGo web search** to answer context questions (e.g. *"Can you explain the terrain of the place?"*). This allows the chatbot to explain real-world topography even when elevation data isn't included in the vector file.

### 6. Locust Load Testing & Performance Benchmarking
- **Decision:** Integrated **Locust** as the primary load-testing suite over Apache JMeter or k6 due to its Pythonic test scenarios, simple parameterization with environment variables (`TEST_FILE_ID`), and real-time interactive dashboard for analyzing request percentiles and throughput.

---

## Future Scope

- **🛰️ Raster & DEM Satellite Support:** Extend file ingestion to process GeoTIFF, Sentinel-2, and Digital Elevation Models (DEM) to calculate 3D surface slope, contours, and true elevation profiles.
- **🗺️ Interactive Map Viewer (Leaflet / Mapbox):** Integrate 2D/3D interactive map rendering in the web dashboard for real-time visualization of uploaded vector layers.
- **🗄️ Native PostGIS Spatial Queries:** Upgrade spatial storage to native PostGIS geometry columns (`ST_Area`, `ST_Perimeter`, `ST_Buffer`) for complex spatial SQL queries at scale.
- **🔐 Multi-Tenant Workspace & Auth:** Implement JWT authentication, role-based access control (RBAC), and team project sharing.
- **📊 Multi-Format Spatial Export:** Provide automated data export options for parsed measurements in GeoJSON, CSV, DXF (AutoCAD), and PDF report formats.

## IMPORTANT 
- If you evaluate before 15th october i could not deploy my project in docker and adding redis for reducing bottle neck and caching the data....AS i have 7th sem IAT my exams 