"""Unit tests for feed integrations."""

import pytest
from pons.feed_integrations import FeedIntegrationService, FeedSource


@pytest.fixture
def feed_service() -> FeedIntegrationService:
    """Create a feed service instance."""
    return FeedIntegrationService()


@pytest.mark.asyncio
async def test_register_feed(feed_service: FeedIntegrationService) -> None:
    """Test registering a new feed source."""
    source = FeedSource(
        name="test_source",
        type="json",
        url="https://example.com/vehicles.json",
        schedule="0 */6 * * *"
    )
    
    await feed_service.register_feed(source)
    
    assert "test_source" in feed_service.sources
    assert feed_service.sources["test_source"].name == "test_source"


@pytest.mark.asyncio
async def test_fetch_nonexistent_feed(feed_service: FeedIntegrationService) -> None:
    """Test fetching from a non-existent feed source."""
    with pytest.raises(ValueError):
        await feed_service.fetch_feed("nonexistent")
