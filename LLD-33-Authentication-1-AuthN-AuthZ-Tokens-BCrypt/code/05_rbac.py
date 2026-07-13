"""
05 — Authorization: Role-Based Access Control (RBAC)
====================================================

Authentication answered "who are you?". AUTHORIZATION answers "what may you
do?". RBAC is the common model: users have ROLES, roles grant PERMISSIONS.
You check a permission, never a role name, at the point of action — so adding
a role never means hunting down scattered `if role == "admin"` checks.

(This is the same association-class shape as LLD-29's Membership: the User x
Group pairing carried a role.)

Needs:  pip install pytest
"""

import pytest

ROLE_PERMISSIONS = {
    "viewer": {"event:read"},
    "editor": {"event:read", "event:write"},
    "admin":  {"event:read", "event:write", "event:delete", "user:manage"},
}


class User:
    def __init__(self, name: str, roles: set[str]):
        self.name = name
        self.roles = roles

    def permissions(self) -> set[str]:
        perms: set[str] = set()
        for role in self.roles:
            perms |= ROLE_PERMISSIONS.get(role, set())   # roles compose
        return perms

    def can(self, permission: str) -> bool:
        return permission in self.permissions()


def require(user: User, permission: str) -> None:
    if not user.can(permission):
        raise PermissionError(f"{user.name} lacks {permission}")


# ─────────────────────────── the tests ───────────────────────────

def test_a_viewer_can_read_but_not_write():
    viewer = User("vipul", {"viewer"})
    assert viewer.can("event:read")
    assert not viewer.can("event:write")

def test_an_editor_inherits_read_and_adds_write():
    editor = User("mallory", {"editor"})
    assert editor.can("event:read") and editor.can("event:write")
    assert not editor.can("event:delete")

def test_multiple_roles_compose_their_permissions():
    user = User("root", {"viewer", "editor"})
    assert user.permissions() == {"event:read", "event:write"}

def test_admin_can_manage_users():
    assert User("boss", {"admin"}).can("user:manage")

def test_require_raises_for_a_missing_permission():
    viewer = User("vipul", {"viewer"})
    require(viewer, "event:read")                    # allowed -> no raise
    with pytest.raises(PermissionError):
        require(viewer, "event:delete")              # denied -> raises

def test_we_check_permissions_not_role_names():
    # a new "moderator" role could grant event:delete tomorrow; code that checks
    # can("event:delete") keeps working, code that checks role == "admin" wouldn't.
    ROLE_PERMISSIONS["moderator"] = {"event:read", "event:delete"}
    try:
        assert User("mod", {"moderator"}).can("event:delete")
    finally:
        del ROLE_PERMISSIONS["moderator"]


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
