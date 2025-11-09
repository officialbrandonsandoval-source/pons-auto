"""Unit tests for feed parsers and validation."""

from typing import Any, Dict, List
from pons.feed_integrations.parsers import CSVFeedParser, JSONFeedParser
from pons.feed_integrations.validation import FeedValidator


def test_csv_parser() -> None:
    """Test CSV feed parser."""
    csv_content = """VIN,StockNumber,Year,Make,Model,Price
1HGCM82633A123456,A123,2023,Honda,Accord,28500
5YFBURHE5HP123789,B456,2022,Toyota,Camry,25900"""
    
    parser = CSVFeedParser()
    vehicles = parser.parse(csv_content)
    
    assert len(vehicles) == 2
    assert vehicles[0]['vin'] == '1HGCM82633A123456'
    assert vehicles[1]['make'] == 'Toyota'


def test_json_parser() -> None:
    """Test JSON feed parser."""
    json_content = '''[
        {"vin": "1HGCM82633A123456", "year": 2023, "make": "Honda", "model": "Accord"},
        {"vin": "5YFBURHE5HP123789", "year": 2022, "make": "Toyota", "model": "Camry"}
    ]'''
    
    parser = JSONFeedParser()
    vehicles = parser.parse(json_content)
    
    assert len(vehicles) == 2
    assert vehicles[0]['vin'] == '1HGCM82633A123456'


def test_feed_validator_valid() -> None:
    """Test feed validation with valid data."""
    vehicle_data: Dict[str, Any] = {
        'vin': '1HGCM82633A123456',
        'year': 2023,
        'make': 'Honda',
        'model': 'Accord',
        'price': 28500
    }
    
    is_valid, error, _ = FeedValidator.validate_vehicle(vehicle_data)
    
    assert is_valid is True
    assert error is None


def test_feed_validator_invalid_vin() -> None:
    """Test feed validation with invalid VIN."""
    vehicle_data: Dict[str, Any] = {
        'vin': 'INVALID',
        'year': 2023,
        'make': 'Honda',
        'model': 'Accord'
    }
    
    is_valid, error, validated = FeedValidator.validate_vehicle(vehicle_data)
    
    assert is_valid is False
    assert error is not None


def test_batch_validation() -> None:
    """Test batch vehicle validation."""
    vehicles: List[Dict[str, Any]] = [
        {'vin': '1HGCM82633A123456', 'year': 2023, 'make': 'Honda', 'model': 'Accord'},
        {'vin': 'INVALID', 'year': 2022, 'make': 'Toyota', 'model': 'Camry'},
        {'vin': '5YFBURHE5HP123789', 'year': 2021, 'make': 'Ford', 'model': 'F-150'}
    ]
    
    result = FeedValidator.validate_batch(vehicles)
    
    assert len(result['valid']) == 2
    assert len(result['invalid']) == 1
