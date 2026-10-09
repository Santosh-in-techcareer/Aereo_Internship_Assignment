THE THINGS I LEARNED HERE ARE :
-------------------------------
-> DIFFRENT KIND OF FILES FOR COORDINATES
-
-> TYPE OF FLATTENING DONE TO GET THE RIGHT AREA OF THE PLACE USING COORDINATES 
--
-> THEIR IS POSTGIS EXTENTION IN POSTGRESQL TO SAVE THE GIS DATAS
---
-> CALCULATING THE AREA OF COORDINATED BY TRANSFORMING THE COORDINATE DATA USING "ALBERS EQUAL AREA CONICS"
----
-> LEARNED HOW AND WHERE DOES THESE COORDINATES DATA IS USED 
-----------------
MY STUFF--
->IN ADD-ON WITH THIS I HAD ADDED A GEN AI MODEL LIKE A RAPPER SO THAT WE CAN GET ANY KIND OF INTERPREDATION OF THE DATA AND MAKE US EASILY FIND EACH AND EVERYTHING ABOUT THE SPECIFIC PLACE 
-------
->YOU DONT NEED TO SPECIFICALLY DATA FOR CHATBOT..JUST ONE UPLOAD..YOU GET EACH AND EVERY DATA ABOUT THE PLACE 
--------
->AS THEY ASK FOR A BACKEND INTERN I DONT WORK MORE ON THE FRONTEND WHICH WOULD BE A SIMPLE U/I

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

### 1. Application Structure

The application is structured into decoupled modules separating backend routes, GIS services, database models, AI agents, and frontend assets:

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
│       └── measurement.py      # Spatial measurement engine
├── Chat_bot/                   # AI Intelligence & Search Services
│   ├── geospatial_chatbot.py   # LangChain LLM chain setup
│   └── search_service.py       # Centroid calculation, Nominatim geocoding & DDG web search
├── frontend/
│   └── index.html              # Glassmorphic UI Dashboard
├── postman_collection.json      # Postman testing collection
└── POSTMAN_API_GUIDE.md        # Step-by-step Postman testing guide
```

---

### 2. File-Processing Flow

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

### 3. Measurement Calculation Flow

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

### 4. CRS Handling

Geographic Coordinate Reference Systems (such as WGS84 `EPSG:4326`) use angular units (degrees), which **cannot be directly used to calculate accurate metric area ($m^2$) or length ($m$)**.

To solve this:
1. **Source CRS Detection:** GeoPandas inspects `gdf.crs`. If no CRS is defined, processing fails with a clear error.
2. **UTM Projection Estimation:** `gdf.estimate_utm_crs()` dynamically identifies the optimal local **Universal Transverse Mercator (UTM)** zone for the dataset's location.
3. **Reprojection:** The dataset is reprojected using `gdf.to_crs(projected_crs)`.
4. **Measurement Computation:** Metric measurements are computed on the reprojected UTM geometries, while original WGS84 geometries are preserved for mapping/display.

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

---

## Future Scope

- **🛰️ Raster & DEM Satellite Support:** Extend file ingestion to process GeoTIFF, Sentinel-2, and Digital Elevation Models (DEM) to calculate 3D surface slope, contours, and true elevation profiles.
- **🗺️ Interactive Map Viewer (Leaflet / Mapbox):** Integrate 2D/3D interactive map rendering in the web dashboard for real-time visualization of uploaded vector layers.
- **🗄️ Native PostGIS Spatial Queries:** Upgrade spatial storage to native PostGIS geometry columns (`ST_Area`, `ST_Perimeter`, `ST_Buffer`) for complex spatial SQL queries at scale.
- **🔐 Multi-Tenant Workspace & Auth:** Implement JWT authentication, role-based access control (RBAC), and team project sharing.
- **📊 Multi-Format Spatial Export:** Provide automated data export options for parsed measurements in GeoJSON, CSV, DXF (AutoCAD), and PDF report formats.