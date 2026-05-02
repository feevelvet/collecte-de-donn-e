import csv
import json
import logging
from datetime import datetime
from config import CSV_COLUMNS, PROCESSED_DIR
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    @staticmethod
    def validate_center(center):
        required_fields = ['name', 'source', 'scraped_date']
        return all(center.get(field) for field in required_fields)
    
    @staticmethod
    def clean_data(centers):
        """Clean and normalize data"""
        cleaned = []
        for center in centers:
            if DataProcessor.validate_center(center):
                # Clean strings
                for key in ['name', 'city', 'country']:
                    if center.get(key):
                        center[key] = ' '.join(center[key].split())
                cleaned.append(center)
            else:
                logger.warning(f"Invalid center data: {center}")
        return cleaned
    
    @staticmethod
    def export_to_csv(centers, filename="shopping_centers.csv"):
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        filepath = os.path.join(PROCESSED_DIR, filename)
        
        cleaned_data = DataProcessor.clean_data(centers)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                
                for center in cleaned_data:
                    row = {col: center.get(col, "") for col in CSV_COLUMNS}
                    # Convert stores list to JSON string
                    if isinstance(row['stores'], list):
                        row['stores'] = json.dumps(row['stores'])
                    writer.writerow(row)
            
            logger.info(f"Exported {len(cleaned_data)} centers to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return None
    
    @staticmethod
    def export_to_json(centers, filename="shopping_centers.json"):
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        filepath = os.path.join(PROCESSED_DIR, filename)
        
        cleaned_data = DataProcessor.clean_data(centers)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(cleaned_data)} centers to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return None
    
    @staticmethod
    def generate_report(centers):
        report = {
            "total_centers": len(centers),
            "scraped_date": datetime.now().isoformat(),
            "by_status": {},
            "by_country": {},
            "sources": {},
            "errors": [],
        }
        
        for center in centers:
            # Count by status
            status = center.get("status", "unknown")
            report["by_status"][status] = report["by_status"].get(status, 0) + 1
            
            # Count by country
            country = center.get("country", "unknown")
            report["by_country"][country] = report["by_country"].get(country, 0) + 1
            
            # Count by source
            source = center.get("source", "unknown")
            report["sources"][source] = report["sources"].get(source, 0) + 1
        
        return report


class DataQuality:
    @staticmethod
    def check_duplicates(centers):
        duplicates = []
        seen_names = {}
        
        for center in centers:
            name = center.get("name", "").lower()
            if name in seen_names:
                duplicates.append({
                    "original": seen_names[name],
                    "duplicate": center
                })
            else:
                seen_names[name] = center
        
        return duplicates
    
    @staticmethod
    def check_completeness(centers):
        if not centers:
            return {}
        
        completeness = {}
        for column in CSV_COLUMNS:
            filled = sum(1 for c in centers if c.get(column))
            completeness[column] = {
                "filled": filled,
                "total": len(centers),
                "percentage": round(filled / len(centers) * 100, 2)
            }
        
        return completeness
