import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from config import USER_AGENT, TIMEOUT, RETRY_ATTEMPTS, DELAY_BETWEEN_REQUESTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RobotsChecker:
    @staticmethod
    def check_robots_txt(url):
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            response = requests.get(robots_url, timeout=TIMEOUT, headers={"User-Agent": USER_AGENT})
            
            if response.status_code == 404:
                logger.info(f"No robots.txt found at {robots_url}, proceeding with caution")
                return True
            
            robots_content = response.text.lower()
            
            # Simple check - look for disallow patterns
            if "user-agent: *" in robots_content:
                lines = robots_content.split("\n")
                disallow_all = False
                for i, line in enumerate(lines):
                    if "user-agent: *" in line:
                        # Check next lines for disallow
                        for j in range(i+1, min(i+5, len(lines))):
                            if "disallow: /" in lines[j]:
                                disallow_all = True
                                break
                
                if disallow_all:
                    logger.warning(f"robots.txt forbids scraping at {url}")
                    return False
            
            logger.info(f"robots.txt allows scraping at {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error checking robots.txt: {e}")
            return True  # Proceed on error


class ShoppingCenterScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.data = []
        
    def fetch_page(self, url):
        for attempt in range(RETRY_ATTEMPTS):
            try:
                logger.info(f"Fetching {url} (attempt {attempt+1}/{RETRY_ATTEMPTS})")
                response = self.session.get(url, timeout=TIMEOUT)
                response.raise_for_status()
                time.sleep(DELAY_BETWEEN_REQUESTS)
                return response.text
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout fetching {url}")
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(2 ** attempt)
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error fetching {url}")
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(2 ** attempt)
        
        return None
    
    def parse_shopping_centers_net(self, html, source_url):
        centers = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find shopping center listings (adapt selectors as needed)
            center_items = soup.find_all('div', class_='shopping-center')
            
            if not center_items:
                # Try alternative selectors
                center_items = soup.find_all('article', class_='center-item')
            
            if not center_items:
                # Try generic divs with specific patterns
                center_items = soup.find_all('div', {'class': lambda x: x and 'center' in x.lower()})
            
            logger.info(f"Found {len(center_items)} shopping centers")
            
            for idx, item in enumerate(center_items):
                try:
                    center = {
                        "id": f"sc_{source_url.replace('https://', '').replace('http://', '').replace('/', '_')}_{idx}",
                        "name": "",
                        "city": "",
                        "country": "",
                        "opened_year": None,
                        "closed_year": None,
                        "status": "active",
                        "stores_count": None,
                        "stores": [],
                        "coordinates": None,
                        "url": "",
                        "source": source_url,
                        "scraped_date": datetime.now().isoformat(),
                    }
                    
                    # Extract name
                    name_elem = item.find('h2') or item.find('h3') or item.find('a')
                    if name_elem:
                        center["name"] = name_elem.get_text(strip=True)
                    
                    # Extract link
                    link_elem = item.find('a', href=True)
                    if link_elem:
                        center["url"] = urljoin(source_url, link_elem['href'])
                    
                    # Extract other info from text
                    text = item.get_text()
                    
                    # Try to extract city/country (simple heuristic)
                    if "," in text:
                        parts = text.split(",")
                        if len(parts) >= 2:
                            center["city"] = parts[-2].strip()[:50]
                            center["country"] = parts[-1].strip()[:50]
                    
                    if center["name"]:
                        centers.append(center)
                        
                except Exception as e:
                    logger.warning(f"Error parsing shopping center item {idx}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
        
        return centers
    
    def scrape(self, url):
        logger.info(f"Starting scrape of {url}")
        
        if not RobotsChecker.check_robots_txt(url):
            logger.error(f"Scraping forbidden by robots.txt at {url}")
            return []
        
        # Fetch page
        html = self.fetch_page(url)
        if not html:
            logger.error(f"Failed to fetch {url}")
            return []
        
        # Parse based on source
        if "shopping-centers.net" in url:
            centers = self.parse_shopping_centers_net(html, url)
        else:
            logger.error(f"Unknown source: {url}")
            return []
        
        self.data.extend(centers)
        return centers


class SourceExtractor:
    @staticmethod
    def save_source(url, html, filename):
        import os
        from config import SOURCES_DIR
        
        os.makedirs(SOURCES_DIR, exist_ok=True)
        
        filepath = os.path.join(SOURCES_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"<!-- Source: {url} -->\n")
            f.write(f"<!-- Downloaded: {datetime.now().isoformat()} -->\n")
            f.write(html)
        
        logger.info(f"Saved source to {filepath}")
