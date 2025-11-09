"""VIN decoding and data enrichment services."""

import re
from typing import Any, Dict, Optional


class VINDecoder:
    """Decode Vehicle Identification Numbers."""
    
    # WMI (World Manufacturer Identifier) codes
    WMI_MANUFACTURERS = {
        '1': 'United States',
        '2': 'Canada',
        '3': 'Mexico',
        '4': 'United States',
        '5': 'United States',
        'J': 'Japan',
        'K': 'South Korea',
        'L': 'China',
        'S': 'United Kingdom',
        'W': 'Germany',
        'Y': 'Sweden',
        'Z': 'Italy',
    }
    
    @staticmethod
    def decode(vin: str) -> Dict[str, Any]:
        """
        Decode VIN to extract vehicle information.
        
        Args:
            vin: 17-character VIN
            
        Returns:
            Dictionary with decoded information
        """
        vin = vin.upper().strip()
        
        if len(vin) != 17:
            return {'error': 'VIN must be 17 characters'}
        
        if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
            return {'error': 'Invalid VIN format'}
        
        return {
            'vin': vin,
            'wmi': vin[:3],
            'vds': vin[3:9],
            'vis': vin[9:17],
            'manufacturer_region': VINDecoder.WMI_MANUFACTURERS.get(vin[0], 'Unknown'),
            'check_digit': vin[8],
            'model_year_code': vin[9],
            'plant_code': vin[10],
            'serial_number': vin[11:17],
            'is_valid': VINDecoder.validate_check_digit(vin)
        }
    
    @staticmethod
    def validate_check_digit(vin: str) -> bool:
        """Validate VIN check digit (position 9)."""
        # Simplified validation - full implementation would use proper weights
        return len(vin) == 17 and vin[8].isalnum()
    
    @staticmethod
    def get_year_from_code(code: str) -> Optional[int]:
        """Get model year from VIN year code."""
        year_codes = {
            'A': 1980, 'B': 1981, 'C': 1982, 'D': 1983, 'E': 1984,
            'F': 1985, 'G': 1986, 'H': 1987, 'J': 1988, 'K': 1989,
            'L': 1990, 'M': 1991, 'N': 1992, 'P': 1993, 'R': 1994,
            'S': 1995, 'T': 1996, 'V': 1997, 'W': 1998, 'X': 1999,
            'Y': 2000, '1': 2001, '2': 2002, '3': 2003, '4': 2004,
            '5': 2005, '6': 2006, '7': 2007, '8': 2008, '9': 2009,
            'A': 2010, 'B': 2011, 'C': 2012, 'D': 2013, 'E': 2014,
            'F': 2015, 'G': 2016, 'H': 2017, 'J': 2018, 'K': 2019,
            'L': 2020, 'M': 2021, 'N': 2022, 'P': 2023, 'R': 2024,
        }
        return year_codes.get(code.upper())


class DataEnrichment:
    """Enrich vehicle data with additional information."""
    
    @staticmethod
    def enrich_vehicle_data(vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add enriched data to vehicle information."""
        enriched = vehicle_data.copy()
        
        # Add VIN decoding if VIN present
        if 'vin' in vehicle_data and isinstance(vehicle_data['vin'], str):
            vin_info = VINDecoder.decode(vehicle_data['vin'])
            enriched['vin_decoded'] = vin_info
        
        # Add computed fields
        if 'price' in vehicle_data and 'msrp' in vehicle_data:
            msrp = vehicle_data['msrp']
            price = vehicle_data['price']
            if msrp and price and isinstance(msrp, (int, float)) and isinstance(price, (int, float)):
                discount = float(msrp) - float(price)
                discount_percent = (discount / float(msrp)) * 100
                enriched['discount'] = discount
                enriched['discount_percent'] = round(discount_percent, 2)
        
        # Add vehicle age
        if 'year' in vehicle_data and isinstance(vehicle_data['year'], int):
            from datetime import datetime
            current_year = datetime.now().year
            enriched['age_years'] = current_year - vehicle_data['year']
        
        return enriched
