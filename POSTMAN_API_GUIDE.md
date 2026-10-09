# 🚀 AEREO Platform - Postman & API Testing Guide

This guide walks you through **how to view your APIs**, **how to import the Postman collection**, and **how to test every single API endpoint step-by-step** for the **AEREO GIS & AI Platform**.

---

## 1. Start the API Server

Before testing with Postman or viewing the API docs, launch your server in the terminal:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

- **Base URL:** `http://127.0.0.1:8000`
- **Frontend Dashboard:** `http://127.0.0.1:8000/frontend/`

---

## 2. How to See Interactive API Documentation (Swagger & ReDoc)

FastAPI automatically generates interactive visual API docs where you can see all available routes, request schemas, and test endpoints directly in your browser:

1. **Swagger UI (Interactive API Tester):**  
   👉 Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

2. **ReDoc (Clean API Specification):**  
   👉 Open [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) in your browser.

---

## 3. How to Import the Ready-to-Use Postman Collection

A pre-configured Postman Collection file has been generated for you in your project directory:  
📁 [`postman_collection.json`](file:///Users/santoshr/Documents/AEREO/postman_collection.json)

### Steps to Import in Postman:
1. Open **Postman**.
2. Click **Import** (top left corner of Postman).
3. Select or drag-and-drop the file [`postman_collection.json`](file:///Users/santoshr/Documents/AEREO/postman_collection.json).
4. Click **Import**. You will see the **AEREO Geospatial & AI Chatbot API Collection** in your left sidebar with all requests ready!

---

## 4. Step-by-Step API Testing Instructions

---

### 🟢 Endpoint 1: Check System Root Status
Verifies the backend API is running.

- **Method:** `GET`
- **URL:** `http://127.0.0.1:8000/`
- **Postman Setup:**
  - Click **Send**.
- **Expected Response (200 OK):**
  ```json
  {
    "message": "Geospatial File Measurement API",
    "status": "running"
  }
  ```

---

### 🟢 Endpoint 2: Health Check
Checks backend health.

- **Method:** `GET`
- **URL:** `http://127.0.0.1:8000/health`
- **Postman Setup:**
  - Click **Send**.
- **Expected Response (200 OK):**
  ```json
  {
    "status": "healthy"
  }
  ```

---

### 🔵 Endpoint 3: Upload Geospatial File (`.kml` or `.zip`)
Uploads a KML file or Shapefile ZIP archive to process spatial features and measurements.

- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/api/files/`
- **Postman Setup:**
  1. Go to the **Body** tab.
  2. Select **form-data**.
  3. In the **KEY** column, type: `uploaded_file`.
  4. Hover over `uploaded_file` key dropdown and change type from **Text** to **File**.
  5. In the **VALUE** column, click **Select Files** and pick a `.kml` file or `.zip` (Shapefile).
  6. Click **Send**.
- **Expected Response (200 OK):**
  ```json
  {
    "id": "42a73b46-2f59-444b-84c0-13fe54253be0",
    "filename": "sample.kml",
    "file_type": "KML",
    "feature_count": 1,
    "crs": "EPSG:4326",
    "projected_crs": "EPSG:32611",
    "status": "PROCESSING",
    "error_message": null,
    "created_at": "2026-10-09T18:50:00"
  }
  ```

---

### 🟢 Endpoint 4: Get File Processing Status
Checks if background feature parsing and spatial measurement calculation has completed.

- **Method:** `GET`
- **URL:** `http://127.0.0.1:8000/api/files/{file_id}/`
- **Example URL:** `http://127.0.0.1:8000/api/files/42a73b46-2f59-444b-84c0-13fe54253be0/`

---

### 🟢 Endpoint 5: Get Feature Spatial Measurements
Retrieves calculated area, perimeter, length, unit, and geometry types for all parsed features.

- **Method:** `GET`
- **URL:** `http://127.0.0.1:8000/api/files/{file_id}/measurements/`

---

### 🟣 Endpoint 6: Ask AEREO AI Chatbot (Terrain & Spatial Analysis)
Queries the AEREO AI Chatbot for conversational analysis of your uploaded dataset, real-world reverse-geocoded location, and web-searched terrain info.

- **Method:** `POST`
- **URL:** `http://127.0.0.1:8000/api/files/{file_id}/chat/`
- **Body (JSON):**
  ```json
  {
    "question": "can you explain the terrain of the place ?",
    "session_id": "postman_session_01"
  }
  ```

---

## 📊 Summary Table of API Endpoints

| Endpoint | Method | Path | Description |
|---|---|---|---|
| **Root Status** | `GET` | `/` | Verify API backend status |
| **Health Check** | `GET` | `/health` | Verify server health |
| **Upload File** | `POST` | `/api/files/` | Upload `.kml` or `.zip` file |
| **File Status** | `GET` | `/api/files/{file_id}/` | Get status (`COMPLETED`, `PROCESSING`, `FAILED`) |
| **Measurements** | `GET` | `/api/files/{file_id}/measurements/` | Get area, perimeter, length for features |
| **AI Chatbot** | `POST` | `/api/files/{file_id}/chat/` | Ask AEREO AI about dataset & terrain |
