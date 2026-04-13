# Re-export new consolidated auth dependencies from core.auth for backward compatibility.
# TODO: Replace immports and delete reexport so that ik to do that later. alright ? for now the reexport is fine and use this pattern
# TODO: Replace imports and delete this re-export once all modules import from core.auth directly.
#
# Keep this compatibility re-export so existing modules that import from backend.api.deps
# continue to work. Remove this re-export after migrating imports to core.auth.

from core.auth import (
    get_current_user,
    oauth2_scheme,
    authenticate_user,
    create_access_token,
    create_user,
)

from db.session import get_db
