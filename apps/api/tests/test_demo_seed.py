import os
import sys
import types
import unittest
import uuid
import importlib.metadata


os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/nexusflow")
os.environ.setdefault("NEON_AUTH_JWKS_URL", "https://example.com/.well-known/jwks.json")
os.environ.setdefault("UPSTASH_REDIS_REST_URL", "https://example.com")
os.environ.setdefault("UPSTASH_REDIS_REST_TOKEN", "token")
os.environ.setdefault("OPENROUTER_API_KEY", "token")

email_validator = types.ModuleType("email_validator")
email_validator.__version__ = "2.0.0"
email_validator.validate_email = lambda value, **_: types.SimpleNamespace(normalized=value)
sys.modules.setdefault("email_validator", email_validator)
_metadata_version = importlib.metadata.version
importlib.metadata.version = (
    lambda package_name: "2.0.0"
    if package_name == "email-validator"
    else _metadata_version(package_name)
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.routers import demo


class DemoSeedTest(unittest.TestCase):
    def test_seed_activity_is_visible_to_dashboard(self) -> None:
        org_id = uuid.uuid4()
        user_id = "user_123"
        workflow_ids = [item["id"] for item in demo._demo_workflows(org_id, user_id)]

        executions, approvals, events = demo._demo_activity(org_id, user_id, workflow_ids)

        self.assertGreaterEqual(len(executions), 3)
        self.assertTrue(all(item["workflow_id"] in workflow_ids for item in executions))
        self.assertTrue(any(item["status"] == "completed" for item in executions))
        self.assertTrue(all(item["execution_id"] in {e["id"] for e in executions} for item in approvals))
        self.assertGreaterEqual(sum(item["tokens_input"] + item["tokens_output"] for item in events), 1)
        self.assertTrue(all(item["workflow_id"] in workflow_ids for item in events))
        self.assertTrue(any(item["agent_type"] for item in events))


if __name__ == "__main__":
    unittest.main()
