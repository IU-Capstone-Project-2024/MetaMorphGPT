from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, Text
import datetime

metadata = MetaData()

status = Table(
    "status",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("permissions", Boolean)
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

user_models = Table(
    "user_models",
    metadata,
    Column("token", String, primary_key=True),
    Column("model_name", String, nullable=False),
    Column("model_description", String, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"))
)

chat = Table(
    "chat",
    metadata,
    Column("user_id", Integer, primary_key=True),
    Column("history", Text, nullable=False),
    Column("current_token", String, ForeignKey("user_models.token"))
)
