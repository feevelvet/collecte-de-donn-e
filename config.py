SHOPPING_CENTERS_URLS = [
    "https://www.shopping-centers.net/shopping-center/",
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
TIMEOUT = 10
RETRY_ATTEMPTS = 3
DELAY_BETWEEN_REQUESTS = 1

DATA_DIR = "data"
SOURCES_DIR = "sources"
PROCESSED_DIR = "processed"

CSV_COLUMNS = [
    "id", "name", "city", "country", "opened_year", "closed_year",
    "status", "stores_count", "stores", "coordinates", "url", "source", "scraped_date",
]
