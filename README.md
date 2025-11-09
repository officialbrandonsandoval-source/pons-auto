# PONS AUTO 🚗💨

**AI-Powered Vehicle Publisher for Car Dealerships**

One-click publishing to Facebook Marketplace, AutoTrader, Cars.com, CarGurus  
AI descriptions • Photo optimization • Mobile-first • Preview before publish

**LIVE DEMO**: https://officialbrandonsandoval-source-pons-auto.streamlit.app

**Built by Brandon Sandoval** | [MIT Licensed](LICENSE)

---

PONS Auto is a robust, scalable platform for ingesting, normalizing, and publishing vehicle inventory across multiple automotive marketplaces and channels.

## 🏗️ Architecture

The system is built with a modular architecture consisting of:

- **Feed Integrations**: Ingest vehicle data from various sources (CSV, XML, JSON, APIs)
- **Normalization & Enrichment**: Transform and standardize vehicle data
- **Cloud Inventory**: Centralized vehicle inventory management
- **Publishing Orchestrator**: Coordinate multi-channel publishing operations
- **Publishing Bridges**: Channel-specific integration adapters
- **Monitoring & Control Plane**: System health monitoring and alerting

See [docs/shiftly_architecture.md](docs/shiftly_architecture.md) for detailed architecture documentation.

## 📋 Prerequisites

- Python 3.10 or higher
- PostgreSQL 15+
- Redis 7+
- Docker and Docker Compose (optional, for containerized deployment)

## 🚀 Quick Start

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   cd /path/to/pons-auto
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   make install-dev
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis configuration
   ```

5. **Build the project**
   ```bash
   make build
   ```

6. **Run the application**
   ```bash
   make run
   ```

The API will be available at `http://localhost:8000`

### Option 2: Docker Compose

1. **Build and start all services**
   ```bash
   make docker-up
   ```

2. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Metrics: http://localhost:8000/metrics

3. **Stop services**
   ```bash
   make docker-down
   ```

## 🛠️ Development

### Available Make Commands

```bash
make help          # Show all available commands
make install       # Install production dependencies
make install-dev   # Install development dependencies
make build         # Build the project
make test          # Run tests with coverage
make lint          # Run code linters
make format        # Format code with black and ruff
make clean         # Clean build artifacts
make run           # Run the application locally
make docker-build  # Build Docker images
make docker-up     # Start Docker containers
make docker-down   # Stop Docker containers
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_inventory.py -v

# Run with coverage report
pytest tests/ --cov=src/shiftly --cov-report=html
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Type checking
mypy src/
```

## 📚 API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

#### Feed Integrations
- `POST /api/v1/feeds/sources` - Register a new feed source
- `GET /api/v1/feeds/sources` - List feed sources
- `POST /api/v1/feeds/fetch/{source_name}` - Fetch data from a feed

#### Normalization
- `POST /api/v1/normalization/normalize` - Normalize raw vehicle data
- `POST /api/v1/normalization/enrich` - Enrich normalized data

#### Inventory
- `POST /api/v1/inventory/vehicles` - Add vehicle to inventory
- `GET /api/v1/inventory/vehicles` - List vehicles
- `GET /api/v1/inventory/vehicles/{vin}` - Get vehicle by VIN
- `PUT /api/v1/inventory/vehicles/{vin}` - Update vehicle
- `DELETE /api/v1/inventory/vehicles/{vin}` - Remove vehicle

#### Publishing
- `POST /api/v1/publishing/jobs` - Create publishing job
- `POST /api/v1/publishing/jobs/{job_id}/execute` - Execute job
- `GET /api/v1/publishing/jobs` - List publishing jobs
- `GET /api/v1/publishing/channels` - List available channels

#### Monitoring
- `GET /api/v1/monitoring/metrics` - Get system metrics
- `GET /api/v1/monitoring/alerts` - Get system alerts
- `GET /api/v1/monitoring/health` - Health check

## ⚙️ Configuration

Configuration files are located in the `config/` directory:

- **`config/tokens.yaml`**: API keys and authentication tokens
- **`config/limits.yaml`**: Rate limiting configuration
- **`config/alerts.yaml`**: Alert thresholds and notifications
- **`config/proxy.yaml`**: Proxy settings for external APIs
- **`config/onboarding.yaml`**: Onboarding flow configuration

### Example Configuration

**config/tokens.yaml**
```yaml
autotrader:
  api_key: "your-api-key"
  api_secret: "your-api-secret"

cars_com:
  api_key: "your-api-key"
```

**config/limits.yaml**
```yaml
rate_limits:
  api_requests_per_minute: 100
  concurrent_publishes: 10
  feed_fetch_interval: 3600  # seconds
```

## 📊 Monitoring

### Prometheus Metrics

The application exposes Prometheus metrics at `/metrics`:

- `shiftly_feed_ingestions_total` - Total feed ingestions
- `shiftly_vehicles_normalized_total` - Normalized vehicles count
- `shiftly_publish_jobs_total` - Publishing jobs count
- `shiftly_active_vehicles` - Active vehicles in inventory
- `shiftly_api_requests_total` - API request count

### Health Checks

- Basic: `GET /health`
- Detailed: `GET /api/v1/monitoring/health`

## 🔒 Security

- API key authentication configured via `config/tokens.yaml`
- Rate limiting to prevent abuse
- CORS configuration in settings
- Input validation using Pydantic models

## 🚢 Deployment

### Production Deployment

1. **Set environment variables**
   ```bash
   export DATABASE_URL="postgresql://user:pass@host:5432/shiftly"
   export REDIS_URL="redis://host:6379/0"
   export DEBUG=false
   ```

2. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

3. **Start the application**
   ```bash
   uvicorn shiftly.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### Docker Production

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🧪 Testing

The project includes comprehensive tests:

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/
```

## 📝 Project Structure

```
pons-auto/
├── config/                 # Configuration files
│   ├── alerts.yaml
│   ├── limits.yaml
│   ├── onboarding.yaml
│   ├── proxy.yaml
│   └── tokens.yaml
├── docs/                   # Documentation
│   └── shiftly_architecture.md
├── src/shiftly/           # Application source code
│   ├── feed_integrations/ # Feed ingestion
│   ├── normalization/     # Data normalization
│   ├── inventory/         # Inventory management
│   ├── publishing/        # Publishing orchestrator
│   ├── bridges/           # Channel adapters
│   ├── monitoring/        # Monitoring & alerts
│   ├── config.py          # Configuration
│   ├── models.py          # Database models
│   └── main.py            # FastAPI application
├── tests/                 # Test suite
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── Makefile              # Build automation
├── pyproject.toml        # Project metadata
└── requirements.txt      # Python dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`make test && make lint`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check the [documentation](docs/shiftly_architecture.md)
- Open an issue on GitHub
- Contact the development team

## 🗺️ Roadmap

- [ ] Additional feed source integrations
- [ ] Advanced VIN decoding and enrichment
- [ ] Machine learning-based pricing recommendations
- [ ] Multi-language support
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard

---

**Built with ❤️ for the automotive industry**
