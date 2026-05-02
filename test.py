import json
from datetime import datetime
from data_processor import DataProcessor, DataQuality

def test():
    centers = [
        {
            "id": "1",
            "name": "Forum Les Halles",
            "city": "Paris",
            "country": "France",
            "opened_year": 1995,
            "closed_year": None,
            "status": "active",
            "stores_count": 200,
            "stores": ["H&M", "Zara"],
            "coordinates": "48.8622,2.3461",
            "url": "https://example.com/1",
            "source": "https://www.shopping-centers.net/",
            "scraped_date": datetime.now().isoformat(),
        },
        {
            "id": "2",
            "name": "Galeria Inno",
            "city": "Brussels",
            "country": "Belgium",
            "opened_year": 1970,
            "closed_year": None,
            "status": "active",
            "stores_count": 120,
            "stores": ["Zara"],
            "coordinates": "50.8505,4.3488",
            "url": "https://example.com/2",
            "source": "https://www.shopping-centers.net/",
            "scraped_date": datetime.now().isoformat(),
        }
    ]
    
    print("Testing scraper...")
    
    # Test export CSV
    DataProcessor.export_to_csv(centers, "test_centers.csv")
    print("✓ CSV export OK")
    
    # Test export JSON
    DataProcessor.export_to_json(centers, "test_centers.json")
    print("✓ JSON export OK")
    
    # Test report
    report = DataProcessor.generate_report(centers)
    print(f"✓ Report OK: {report['total_centers']} centers")
    
    # Test duplicates
    dups = DataQuality.check_duplicates(centers)
    print(f"✓ Duplicates: {len(dups)}")
    
    print("\nAll tests passed!")


if __name__ == "__main__":
    test()
