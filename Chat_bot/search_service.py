import logging
import re
import urllib.parse
import httpx
import shapely.wkt
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "GeoSmartBot/1.0 (Geospatial AI Assistant)"
}

TERRAIN_KEYWORDS = [
    "terrain", "geography", "place", "location", "landscape", "topography",
    "elevation", "mountain", "river", "soil", "climate", "surroundings",
    "environment", "where is", "where", "area", "region", "where is this"
]


def is_location_or_terrain_query(question: str) -> bool:
    """Check if question asks about terrain, location, or geography."""
    q_lower = question.lower()
    return any(keyword in q_lower for keyword in TERRAIN_KEYWORDS)


def compute_dataset_centroid(features: list) -> tuple[float, float] | None:
    """Compute average latitude and longitude (lat, lon) from feature WKTs."""
    lats = []
    lons = []

    for f in features:
        wkt = f.get("geometry_wkt")
        if not wkt:
            continue
        try:
            geom = shapely.wkt.loads(wkt)
            if geom.is_empty:
                continue
            centroid = geom.centroid
            # Assuming WGS84: x = lon (-180 to 180), y = lat (-90 to 90)
            x, y = centroid.x, centroid.y
            if -90 <= y <= 90 and -180 <= x <= 180:
                lats.append(y)
                lons.append(x)
        except Exception:
            continue

    if not lats or not lons:
        return None

    avg_lat = sum(lats) / len(lats)
    avg_lon = sum(lons) / len(lons)
    return (avg_lat, avg_lon)


def reverse_geocode(lat: float, lon: float) -> str | None:
    """Reverse geocode coordinates using OpenStreetMap Nominatim API."""
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    try:
        with httpx.Client(timeout=6.0, headers=HEADERS) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                display_name = data.get("display_name")
                address = data.get("address", {})
                parts = []
                for k in ["suburb", "city", "county", "state", "country"]:
                    if k in address:
                        parts.append(address[k])
                short_name = ", ".join(parts) if parts else display_name
                return short_name or display_name
    except Exception as exc:
        logger.warning(f"Reverse geocoding failed: {exc}")
    return None


def search_web_terrain(query: str, max_results: int = 4) -> list[str]:
    """Search DuckDuckGo web for terrain and location details."""
    snippets = []
    try:
        ddg = DDGS()
        results = list(ddg.text(query, max_results=max_results))
        for r in results:
            body = r.get("body", "").strip()
            title = r.get("title", "").strip()
            if body:
                snippets.append(f"• {title}: {body}")
    except Exception as exc:
        logger.warning(f"DuckDuckGo search failed, using fallback: {exc}")
        # Fallback HTML query if DDGS library has network issues
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            with httpx.Client(timeout=6.0, headers=HEADERS) as client:
                resp = client.get(url)
                if resp.status_code in (200, 202):
                    matches = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', resp.text, re.DOTALL)
                    for m in matches[:max_results]:
                        clean_text = re.sub(r'<[^>]+>', '', m).strip()
                        if clean_text:
                            snippets.append(f"• {clean_text}")
        except Exception as inner_exc:
            logger.warning(f"Fallback search failed: {inner_exc}")

    return snippets


def get_terrain_and_location_context(features: list, question: str) -> str:
    """Generate search-enhanced location & terrain context for the chatbot."""
    if not is_location_or_terrain_query(question):
        return ""

    centroid = compute_dataset_centroid(features)
    if not centroid:
        return "\nLocation Coordinates: Unavailable in dataset."

    lat, lon = centroid
    location_name = reverse_geocode(lat, lon)

    location_str = f"Lat {lat:.4f}, Lon {lon:.4f}"
    if location_name:
        location_str += f" ({location_name})"

    search_query = f"terrain geography landscape topography of {location_name or location_str}"
    web_results = search_web_terrain(search_query)

    context_lines = [
        f"\n--- GEOLOCATION & TERRAIN SEARCH INFO ---",
        f"Dataset Coordinates: Latitude {lat:.5f}, Longitude {lon:.5f}",
        f"Reverse Geocoded Location: {location_name or 'Unknown Region'}",
    ]

    if web_results:
        context_lines.append("\nWeb Search Results about Terrain & Geography:")
        context_lines.extend(web_results)
    else:
        context_lines.append(f"Web Search Summary: Located at {location_str}.")

    context_lines.append("----------------------------------------\n")
    return "\n".join(context_lines)
