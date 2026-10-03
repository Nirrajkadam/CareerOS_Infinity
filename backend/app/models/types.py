from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB

# Cross-dialect JSON column type: Uses PostgreSQL JSONB in production & standard JSON in SQLite/Local
JSONType = JSON().with_variant(JSONB, "postgresql")
