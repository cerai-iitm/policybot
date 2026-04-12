"""db package.

Keep the package root minimal to avoid import-time circular dependencies.

Expose only the DB configuration helpers (engine/session/base/get_db). CRUD
functions and ORM models should be imported from their explicit submodules:

- config: DB engine/session/base/get_db
- schema: ORM models
- crud: CRUD helper functions

This avoids circular imports where CRUD modules import models while the
package root imports CRUD at import time.
"""

from .config import DATABASE_URL, AsyncSessionLocal, Base, get_db

__all__ = ["DATABASE_URL", "AsyncSessionLocal", "Base", "get_db"]
