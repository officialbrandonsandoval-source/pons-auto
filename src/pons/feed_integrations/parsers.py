"""Feed parsers for various formats."""

import csv
import xml.etree.ElementTree as ET
import json
import io
from typing import Any, Dict, List
from pydantic import BaseModel, ValidationError


class CSVFeedParser:
    """Parse CSV vehicle feeds."""
    
    def parse(self, content: str) -> List[Dict[str, Any]]:
        """Parse CSV content into vehicle dictionaries."""
        vehicles: List[Dict[str, Any]] = []
        reader = csv.DictReader(io.StringIO(content))
        
        for row in reader:
            vehicle = self._normalize_row(row)
            if vehicle:
                vehicles.append(vehicle)
        
        return vehicles
    
    def _normalize_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize CSV row field names."""
        # Common CSV field mappings
        field_map: Dict[str, str] = {
            'VIN': 'vin',
            'StockNumber': 'stock_number',
            'Year': 'year',
            'Make': 'make',
            'Model': 'model',
            'Trim': 'trim',
            'Price': 'price',
            'Mileage': 'mileage',
            'Color': 'exterior_color',
            'ExteriorColor': 'exterior_color',
        }
        
        normalized: Dict[str, Any] = {}
        for key, value in row.items():
            normalized_key = field_map.get(key, key.lower().replace(' ', '_'))
            normalized[normalized_key] = value
        
        return normalized


class XMLFeedParser:
    """Parse XML vehicle feeds."""
    
    def parse(self, content: str) -> List[Dict[str, Any]]:
        """Parse XML content into vehicle dictionaries."""
        vehicles: List[Dict[str, Any]] = []
        
        try:
            root = ET.fromstring(content)
            
            # Handle different XML structures
            vehicle_elements = root.findall('.//Vehicle') or root.findall('.//vehicle')
            
            for vehicle_elem in vehicle_elements:
                vehicle = self._parse_vehicle_element(vehicle_elem)
                if vehicle:
                    vehicles.append(vehicle)
        
        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
        
        return vehicles
    
    def _parse_vehicle_element(self, elem: ET.Element) -> Dict[str, Any]:
        """Parse a single vehicle XML element."""
        vehicle: Dict[str, Any] = {}
        
        for child in elem:
            tag = child.tag.lower()
            vehicle[tag] = child.text or ''
        
        return vehicle


class JSONFeedParser:
    """Parse JSON vehicle feeds."""
    
    def parse(self, content: str) -> List[Dict[str, Any]]:
        """Parse JSON content into vehicle dictionaries."""
        try:
            data = json.loads(content)
            
            # Handle different JSON structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Check for common wrapper keys
                for key in ['vehicles', 'data', 'items', 'results']:
                    if key in data and isinstance(data[key], list):
                        return data[key]
                return [data]
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
        
        return []


# Parser registry
PARSERS = {
    'csv': CSVFeedParser(),
    'xml': XMLFeedParser(),
    'json': JSONFeedParser(),
}


def get_parser(feed_type: str):
    """Get appropriate parser for feed type."""
    return PARSERS.get(feed_type.lower())
