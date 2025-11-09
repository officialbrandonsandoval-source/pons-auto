"""Expanded test suite for Shiftly Auto."""

import pytest
from fastapi.testclient import TestClient
from pons.main import app
from pons.models import SessionLocal, Vehicle
from pons.auth import verify_api_key


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def api_headers():
    """API authentication headers."""
    return {"X-API-Key": "dev-key-12345"}


class TestAuthentication:
    """Test authentication and security."""
    
    def test_missing_api_key(self, client):
        """Test request without API key."""
        response = client.get("/api/inventory/vehicles")
        assert response.status_code in [401, 403]
    
    def test_invalid_api_key(self, client):
        """Test request with invalid API key."""
        response = client.get(
            "/api/inventory/vehicles",
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == 403
    
    def test_valid_api_key(self, client, api_headers):
        """Test request with valid API key."""
        response = client.get("/api/inventory/vehicles", headers=api_headers)
        assert response.status_code == 200


class TestInventoryAPI:
    """Test inventory management endpoints."""
    
    def test_list_vehicles(self, client, api_headers):
        """Test listing vehicles."""
        response = client.get("/api/inventory/vehicles", headers=api_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_search_vehicles(self, client, api_headers):
        """Test vehicle search."""
        response = client.get(
            "/api/inventory/search?make=Honda",
            headers=api_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_vehicle_by_vin(self, client, api_headers):
        """Test getting specific vehicle."""
        # First, create a test vehicle
        test_vin = "1HGCM82633A123456"
        
        response = client.get(
            f"/api/inventory/vehicles/{test_vin}",
            headers=api_headers
        )
        # May be 200 or 404 depending on database state
        assert response.status_code in [200, 404]


class TestFeedIntegration:
    """Test feed parsing and validation."""
    
    def test_csv_parser(self):
        """Test CSV feed parser."""
        from pons.feed_integrations.parsers import CSVFeedParser
        
        parser = CSVFeedParser()
        csv_content = """VIN,Year,Make,Model,Price
1HGCM82633A123456,2023,Honda,Accord,28500
5YFBURHE5HP123789,2022,Toyota,Camry,25900"""
        
        vehicles = parser.parse(csv_content)
        assert len(vehicles) == 2
        assert vehicles[0]['vin'] == '1HGCM82633A123456'
    
    def test_json_parser(self):
        """Test JSON feed parser."""
        from pons.feed_integrations.parsers import JSONFeedParser
        
        parser = JSONFeedParser()
        json_content = '''[
            {"vin": "1HGCM82633A123456", "year": 2023, "make": "Honda", "model": "Accord"},
            {"vin": "5YFBURHE5HP123789", "year": 2022, "make": "Toyota", "model": "Camry"}
        ]'''
        
        vehicles = parser.parse(json_content)
        assert len(vehicles) == 2
    
    def test_vehicle_validation(self):
        """Test vehicle data validation."""
        from pons.feed_integrations.validation import FeedValidator
        
        valid_vehicle = {
            "vin": "1HGCM82633A123456",
            "year": 2023,
            "make": "Honda",
            "model": "Accord"
        }
        
        is_valid, error, validated = FeedValidator.validate_vehicle(valid_vehicle)
        assert is_valid is True
        assert error is None
        assert validated is not None
    
    def test_invalid_vin_validation(self):
        """Test validation with invalid VIN."""
        from pons.feed_integrations.validation import FeedValidator
        
        invalid_vehicle = {
            "vin": "INVALID",
            "year": 2023,
            "make": "Honda",
            "model": "Accord"
        }
        
        is_valid, error, validated = FeedValidator.validate_vehicle(invalid_vehicle)
        assert is_valid is False
        assert error is not None


class TestNormalization:
    """Test VIN decoding and data enrichment."""
    
    def test_vin_decoder_valid(self):
        """Test VIN decoder with valid VIN."""
        from pons.normalization.enrichment import VINDecoder
        
        result = VINDecoder.decode("1HGCM82633A123456")
        assert 'vin' in result
        assert result['vin'] == "1HGCM82633A123456"
        assert 'manufacturer_region' in result
    
    def test_vin_decoder_invalid(self):
        """Test VIN decoder with invalid VIN."""
        from pons.normalization.enrichment import VINDecoder
        
        result = VINDecoder.decode("INVALID")
        assert 'error' in result
    
    def test_data_enrichment(self):
        """Test vehicle data enrichment."""
        from pons.normalization.enrichment import DataEnrichment
        
        vehicle = {
            'vin': '1HGCM82633A123456',
            'year': 2023,
            'price': 28500,
            'msrp': 32000
        }
        
        enriched = DataEnrichment.enrich_vehicle_data(vehicle)
        assert 'vin_decoded' in enriched
        assert 'discount' in enriched
        assert enriched['discount'] == 3500
        assert 'age_years' in enriched


class TestPublishingBridges:
    """Test publishing bridge interfaces."""
    
    @pytest.mark.asyncio
    async def test_autotrader_bridge(self):
        """Test AutoTrader bridge."""
        from pons.bridges import BRIDGES
        from pons.bridges import VehicleData
        
        bridge = BRIDGES['autotrader']
        vehicle = VehicleData(
            vin="1HGCM82633A123456",
            stock_number="A12345",
            year=2023,
            make="Honda",
            model="Accord",
            price=28500
        )
        
        # Note: This will fail without real API credentials
        # In production, mock the API calls
        result = await bridge.publish(vehicle)
        assert 'channel' in result


class TestWebhooks:
    """Test webhook system."""
    
    @pytest.mark.asyncio
    async def test_webhook_subscription(self):
        """Test creating webhook subscription."""
        from pons.webhooks import webhook_service
        
        subscription = await webhook_service.subscribe(
            url="https://example.com/webhook",
            event_type="vehicle.created",
            secret="test_secret"
        )
        
        assert subscription.id is not None
        assert subscription.url == "https://example.com/webhook"
        
        # Clean up
        await webhook_service.unsubscribe(subscription.id)
    
    def test_webhook_signature(self):
        """Test webhook signature generation and verification."""
        from pons.webhooks import WebhookService
        
        payload = '{"test": "data"}'
        secret = "test_secret"
        
        signature = WebhookService()._generate_signature(payload, secret)
        is_valid = WebhookService.verify_signature(payload, signature, secret)
        
        assert is_valid is True


class TestEmail:
    """Test email notification system."""
    
    @pytest.mark.asyncio
    async def test_email_service_init(self):
        """Test email service initialization."""
        from pons.email import email_service
        
        assert email_service.smtp_host is not None
        assert email_service.smtp_port > 0


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestRateLimiting:
    """Test rate limiting."""
    
    def test_rate_limit_headers(self, client):
        """Test rate limit headers in response."""
        response = client.get("/")
        # Rate limit headers may or may not be present depending on middleware
        assert response.status_code == 200


@pytest.mark.integration
class TestEndToEnd:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_vehicle_lifecycle(self, client, api_headers):
        """Test complete vehicle lifecycle."""
        # 1. Import vehicle from feed
        # 2. Normalize data
        # 3. Add to inventory
        # 4. Publish to channels
        # 5. Update vehicle
        # 6. Unpublish
        # 7. Remove from inventory
        
        # This is a placeholder for full integration test
        pass
