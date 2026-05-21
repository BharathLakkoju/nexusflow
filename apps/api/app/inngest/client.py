# Implements: F-036 (background jobs via Inngest)
"""
Inngest client setup.
"""
import inngest

from app.config import settings

inngest_client = inngest.Inngest(
    app_id="nexusflow-ai",
    event_key=settings.INNGEST_EVENT_KEY,
    signing_key=settings.INNGEST_SIGNING_KEY,
    is_production=not settings.DEBUG,
)
