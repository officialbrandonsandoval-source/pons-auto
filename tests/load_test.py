"""Load testing script for Shiftly Auto API."""

from locust import HttpUser, task, between
import random


class ShiftlyUser(HttpUser):
    """Simulate user behavior for load testing."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Setup - runs once per user."""
        self.api_key = "dev-key-12345"
        self.headers = {"X-API-Key": self.api_key}
    
    @task(10)
    def list_vehicles(self):
        """List all vehicles - most common operation."""
        self.client.get("/api/inventory/vehicles", headers=self.headers)
    
    @task(5)
    def search_vehicles(self):
        """Search vehicles - second most common."""
        makes = ["Honda", "Toyota", "Ford", "Chevrolet", "Jeep"]
        make = random.choice(makes)
        self.client.get(
            f"/api/inventory/search?make={make}",
            headers=self.headers
        )
    
    @task(3)
    def get_vehicle_by_vin(self):
        """Get specific vehicle."""
        test_vins = [
            "1HGCM82633A123456",
            "5YFBURHE5HP123789",
            "1C4RJFAG1FC123456"
        ]
        vin = random.choice(test_vins)
        self.client.get(
            f"/api/inventory/vehicles/{vin}",
            headers=self.headers
        )
    
    @task(2)
    def health_check(self):
        """Health check endpoint."""
        self.client.get("/health")
    
    @task(1)
    def api_docs(self):
        """Access API documentation."""
        self.client.get("/docs")
    
    @task(1)
    def normalize_vehicle(self):
        """Normalize vehicle data."""
        payload = {
            "vin": "1HGCM82633A123456",
            "year": 2023,
            "make": "Honda",
            "model": "Accord",
            "price": 28500
        }
        self.client.post(
            "/api/normalization/normalize",
            json=payload,
            headers=self.headers
        )


class AdminUser(HttpUser):
    """Simulate admin user behavior."""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Setup admin user."""
        self.api_key = "dev-key-12345"
        self.headers = {"X-API-Key": self.api_key}
    
    @task(5)
    def view_metrics(self):
        """View system metrics."""
        self.client.get("/metrics", headers=self.headers)
    
    @task(3)
    def check_feeds(self):
        """Check feed status."""
        self.client.get("/api/feeds/sources", headers=self.headers)
    
    @task(2)
    def view_publishing_status(self):
        """Check publishing status."""
        self.client.get("/api/publishing/jobs", headers=self.headers)


# Run with: locust -f tests/load_test.py --host=http://localhost:8001
