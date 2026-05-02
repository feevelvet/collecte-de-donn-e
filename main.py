import logging
from config import SHOPPING_CENTERS_URLS
from scraper import ShoppingCenterScraper, SourceExtractor
from data_processor import DataProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    scraper = ShoppingCenterScraper()
    all_centers = []
    
    for url in SHOPPING_CENTERS_URLS:
        logger.info(f"Scraping: {url}")
        
        try:
            html = scraper.fetch_page(url)
            if not html:
                logger.error(f"Failed to fetch {url}")
                continue
            
            # Save source
            source_filename = f"source_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            SourceExtractor.save_source(url, html, source_filename)
            
            # Scrape data
            centers = scraper.scrape(url)
            all_centers.extend(centers)
            logger.info(f"Found {len(centers)} centers")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            continue
    
    if not all_centers:
        logger.warning("No data scraped")
        return 1
    
    # Export
    logger.info(f"Exporting {len(all_centers)} centers...")
    DataProcessor.export_to_csv(all_centers)
    DataProcessor.export_to_json(all_centers)
    
    report = DataProcessor.generate_report(all_centers)
    logger.info(f"Total: {report['total_centers']} centers")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
