"""Isolated test configuration: never use deployment secrets or external AI calls."""
import os

os.environ["SECRET_KEY"] = "test-only-key-not-for-deployment-0123456789"
os.environ["ENABLE_SANDBOX_ATS"] = "true"
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "true"
