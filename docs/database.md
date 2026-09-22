# Database & Migrations Guide

Cornerstone uses **SQLAlchemy** for database ORM modeling and **Alembic** for schema migrations with SQLite by default.

---

## 🏛️ Database Lifecycle

1. **Initialization:** `init_db()` is called explicitly when the desktop app launches (in `start.py`) or via `stone db init`. Pending migrations are automatically applied up to `head`.
2. **Transactions:** Bridge methods execute database transactions using `get_session()` from `app/database.py`. It provides session-per-call context with automatic commit on success and rollback on error.

```python
from app.database import get_session
from app.models import User

# Example usage inside a bridge method:
with get_session() as session:
    users = session.query(User).all()
    return [u.to_dict() for u in users]
```

---

## 🗃️ Models

Models are defined in `app/models.py`. Always implement a `to_dict()` method on models because ORM instances cannot be serialized directly across the `pywebview` bridge.

```python
from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
```

---

## 🔄 Sequential Alembic Migrations

Cornerstone uses zero-padded 4-digit sequential IDs (`0001`, `0002`, `0003`, ...) for migration versions, stored in `app/migrations/versions/`.

### Migration Message Taxonomy

When creating a migration with `stone db migrate -m "<message>"`, follow the structured verb taxonomy:

| Action            | Format                           | Example Command                                           | Output Filename                             |
|:------------------|:---------------------------------|:----------------------------------------------------------|:--------------------------------------------|
| **Create Table**  | `create_<table_name>_table`      | `stone db migrate -m "create_users_table"`                | `0002_create_users_table.py`                |
| **Add Column**    | `add_<col>_to_<table_name>`      | `stone db migrate -m "add_email_to_users"`                | `0003_add_email_to_users.py`                |
| **Alter Column**  | `alter_<col>_in_<table_name>`    | `stone db migrate -m "alter_status_in_orders"`            | `0004_alter_status_in_orders.py`            |
| **Rename Column** | `rename_<old>_to_<new>_in_<tbl>` | `stone db migrate -m "rename_name_to_full_name_in_users"` | `0005_rename_name_to_full_name_in_users.py` |
| **Drop Column**   | `drop_<col>_from_<table_name>`   | `stone db migrate -m "drop_avatar_from_users"`            | `0006_drop_avatar_from_users.py`            |
| **Drop Table**    | `drop_<table_name>_table`        | `stone db migrate -m "drop_temp_notes_table"`             | `0007_drop_temp_notes_table.py`             |
| **Add Index**     | `add_index_<name>_on_<table>`    | `stone db migrate -m "add_index_email_on_users"`          | `0008_add_index_email_on_users.py`          |
| **Data Seed**     | `seed_<table_name>`              | `stone db migrate -m "seed_default_roles"`                | `0009_seed_default_roles.py`                |

---

## 🛠️ Database CLI Commands

```bash
# Inspect database status and table count
stone db info

# Generate a new migration revision
stone db migrate -m "create_projects_table"

# Apply pending migrations
stone db upgrade

# Roll back the previous revision
stone db downgrade

# Inspect current revision
stone db current

# View migration history
stone db history

# List table schemas
stone db tables

# Run an ad-hoc query
stone db query "SELECT * FROM users" --json

# Reset the database file
stone db reset --yes
```
