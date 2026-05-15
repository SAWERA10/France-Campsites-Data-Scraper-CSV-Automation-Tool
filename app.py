import requests
import pandas as pd
import logging
import re
import time
from typing import Dict, List, Optional

# ---------------- LOGGING ----------------

logger = logging.getLogger("france_campsites")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------- CONFIG ----------------

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",
    "https://api.openstreetmap.fr/oapi/interpreter",
]

HEADERS = {
    "User-Agent": "FranceCampsitesScraper/1.0"
}

OUTPUT_CSV = "france_campsites_cleaned.csv"

# ---------------- OVERPASS QUERY ----------------

def build_query() -> str:
    """
    Query all camp sites and caravan sites in France.
    """

    return """
[out:json][timeout:300];

area["ISO3166-1"="FR"][admin_level=2]->.france;

(
  node["tourism"="camp_site"](area.france);
  way["tourism"="camp_site"](area.france);
  relation["tourism"="camp_site"](area.france);

  node["tourism"="caravan_site"](area.france);
  way["tourism"="caravan_site"](area.france);
  relation["tourism"="caravan_site"](area.france);
);

out center tags;
""".strip()

# ---------------- FETCH DATA ----------------

def fetch_overpass(query: str) -> dict:

    for mirror in OVERPASS_MIRRORS:

        try:
            logger.info(f"Trying mirror: {mirror}")

            response = requests.post(
                mirror,
                data={"data": query},
                headers=HEADERS,
                timeout=600
            )

            response.raise_for_status()

            data = response.json()

            logger.info(
                f"Success from mirror: {mirror} | "
                f"Elements: {len(data.get('elements', []))}"
            )

            return data

        except Exception as e:
            logger.warning(f"Mirror failed: {mirror} | {e}")
            time.sleep(2)

    raise RuntimeError("All Overpass mirrors failed.")

# ---------------- HELPERS ----------------

def safe_get(tags: Dict, *keys) -> str:

    for key in keys:
        value = tags.get(key)

        if value:
            return str(value).strip()

    return ""

def normalize_phone(phone: Optional[str]) -> str:

    if not phone:
        return ""

    phone = str(phone).strip()

    return re.sub(r"[^\d+]", "", phone)

def normalize_website(url: Optional[str]) -> str:

    if not url:
        return ""

    url = str(url).strip()

    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url

# ---------------- PARSER ----------------

def parse_element(element: dict) -> Optional[Dict]:

    tags = element.get("tags", {})

    tourism = tags.get("tourism", "").lower()

    if tourism == "camp_site":
        category = "Camping"

    elif tourism == "caravan_site":
        category = "Aire"

    else:
        return None

    # ---------------- NAME ----------------

    name = safe_get(tags, "name", "operator", "brand")

    if not name:
        osm_id = element.get("id", "")
        name = f"Unnamed {category} {osm_id}"

    # ---------------- ADDRESS ----------------

    street = safe_get(tags, "addr:street")
    house = safe_get(tags, "addr:housenumber")
    city = safe_get(
        tags,
        "addr:city",
        "addr:town",
        "addr:village"
    )

    postcode = safe_get(tags, "addr:postcode")

    full_address = " ".join(
        x for x in [house, street] if x
    ).strip()

    # ---------------- COORDINATES ----------------

    lat = None
    lon = None

    if element["type"] == "node":

        lat = element.get("lat")
        lon = element.get("lon")

    else:

        center = element.get("center", {})

        lat = center.get("lat")
        lon = center.get("lon")

    if lat is None or lon is None:
        return None

    # ---------------- CONTACT INFO ----------------

    website = normalize_website(
        safe_get(tags, "website", "url")
    )

    phone = normalize_phone(
        safe_get(tags, "phone", "contact:phone")
    )

    # ---------------- RETURN RECORD ----------------

    return {
        "Business Name": name,
        "Category": category,
        "Full Address": full_address,
        "City": city,
        "Postal Code": postcode,
        "Latitude": float(lat),
        "Longitude": float(lon),
        "Website URL": website,
        "Phone Number": phone,
    }

# ---------------- EXTRACT ----------------

def extract_records(data: dict) -> pd.DataFrame:

    records = []

    elements = data.get("elements", [])

    logger.info(f"Processing {len(elements)} elements")

    skipped = 0

    for element in elements:

        try:

            record = parse_element(element)

            if record:
                records.append(record)
            else:
                skipped += 1

        except Exception as e:
            logger.warning(f"Parse error: {e}")
            skipped += 1

    logger.info(f"Valid records: {len(records)}")
    logger.info(f"Skipped records: {skipped}")

    return pd.DataFrame(records)

# ---------------- CLEANING ----------------

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    logger.info("Cleaning dataframe")

    df = df.copy()

    df = df.fillna("")

    text_columns = [
        "Business Name",
        "Full Address",
        "City",
        "Postal Code",
        "Website URL",
        "Phone Number"
    ]

    for col in text_columns:

        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )

    # ---------------- DEDUP ----------------

    df["dedup_key"] = (

        df["Business Name"]
        .str.lower()

        + "|"

        + df["Latitude"]
        .round(5)
        .astype(str)

        + "|"

        + df["Longitude"]
        .round(5)
        .astype(str)
    )

    before = len(df)

    df = df.drop_duplicates(
        subset=["dedup_key"]
    )

    after = len(df)

    logger.info(
        f"Removed duplicates: {before - after}"
    )

    df = df.drop(columns=["dedup_key"])

    return df

# ---------------- MAIN ----------------

def main():

    logger.info("Starting France campsites extraction")

    query = build_query()

    data = fetch_overpass(query)

    if not data:
        logger.error("No data returned")
        return

    df = extract_records(data)

    if df.empty:
        logger.error("No valid campsite records extracted")
        return

    df = clean_dataframe(df)

    logger.info(f"Final records: {len(df)}")

    df.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8"
    )

    logger.info(
        f"CSV exported successfully: {OUTPUT_CSV}"
    )

# ---------------- ENTRY ----------------

if __name__ == "__main__":
    main() 