"""Unit tests for normalization and enrichment."""

from typing import Any, Dict
from pons.normalization.enrichment import VINDecoder, DataEnrichment


def test_vin_decoder_valid() -> None:
    """Test VIN decoding with valid VIN."""
    vin = "1HGCM82633A123456"
    result = VINDecoder.decode(vin)
    
    assert result['vin'] == vin
    assert result['wmi'] == "1HG"
    assert len(result['serial_number']) == 6


def test_vin_decoder_invalid_length() -> None:
    """Test VIN decoder with invalid length."""
    result = VINDecoder.decode("SHORT")
    assert 'error' in result


def test_vin_decoder_invalid_characters() -> None:
    """Test VIN decoder with invalid characters."""
    result = VINDecoder.decode("1HGCM82633A12345O")  # Contains 'O'
    assert 'error' in result


def test_data_enrichment() -> None:
    """Test vehicle data enrichment."""
    vehicle_data: Dict[str, Any] = {
        'vin': '1HGCM82633A123456',
        'year': 2020,
        'make': 'Honda',
        'model': 'Accord',
        'price': 25000,
        'msrp': 30000
    }
    
    enriched = DataEnrichment.enrich_vehicle_data(vehicle_data)
    
    assert 'vin_decoded' in enriched
    assert 'discount' in enriched
    assert enriched['discount'] == 5000
    assert 'discount_percent' in enriched
    assert 'age_years' in enriched


def test_enrichment_without_pricing() -> None:
    """Test enrichment when pricing data is missing."""
    vehicle_data: Dict[str, Any] = {
        'vin': '1HGCM82633A123456',
        'year': 2023,
        'make': 'Toyota',
        'model': 'Camry'
    }
    
    enriched = DataEnrichment.enrich_vehicle_data(vehicle_data)
    
    assert 'vin_decoded' in enriched
    assert 'discount' not in enriched
    assert 'age_years' in enriched
