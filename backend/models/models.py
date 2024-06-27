from sqlalchemy import MetaData, Table, Column, Integer, String, JSON, TIMESTAMP, ForeignKey, Boolean
import datetime

metadata = MetaData()

status = Table(
    "status",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("permissions", JSON)
)

users = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.UTC),
    Column("status_id", Integer, ForeignKey("status.id")),
    Column("email", String(length=320), unique=True, index=True, nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False)
)
