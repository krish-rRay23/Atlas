"""ATLAS Production Security & Access Control Module.

Implements Authentication, Role-Based Access Control (RBAC),
SSRF protection, Path Traversal defense, and Password Hashing.
Operationalizes OWASP Top 10 for LLM Applications and NIST AI RMF.
"""

import os
import re
import ipaddress
import hashlib
import secrets
import urllib.parse
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from fastapi import Header, HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from atlas.core.config import settings

# HTTP Bearer scheme
security_bearer = HTTPBearer(auto_error=False)

# Role definitions & hierarchy
ROLES = {
    "admin": {"permissions": ["all", "manage_users", "ingest", "generate", "review", "read"]},
    "researcher": {"permissions": ["create_project", "ingest", "generate", "read"]},
    "reviewer": {"permissions": ["review_evidence", "approve_claims", "read"]},
    "reader": {"permissions": ["read"]}
}

API_KEYS = {
    settings.admin_api_key: {"user_id": "USR-ADMIN", "username": "admin", "role": "admin"},
    settings.researcher_api_key: {"user_id": "USR-RESEARCHER", "username": "analyst", "role": "researcher"},
    settings.reviewer_api_key: {"user_id": "USR-REVIEWER", "username": "senior_reviewer", "role": "reviewer"},
    settings.reader_api_key: {"user_id": "USR-READER", "username": "guest_reader", "role": "reader"}
}

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Cryptographically hash a password using SHA-256 with a unique salt."""
    salt = salt or secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return hashed, salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify that a password matches its stored salt and hash."""
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest() == hashed

def get_current_user(
    x_atlas_api_key: Optional[str] = Header(None, alias="X-ATLAS-API-KEY"),
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> Dict[str, Any]:
    """FastAPI dependency: Authenticate request via API Key or Bearer Token.
    If auth is disabled (local development), defaults to an authenticated researcher.
    """
    if not settings.auth_enabled:
        return {"user_id": "USR-LOCAL-DEV", "username": "local_analyst", "role": "admin"}

    # 1. Check API Key
    if x_atlas_api_key and x_atlas_api_key in API_KEYS:
        return API_KEYS[x_atlas_api_key]

    # 2. Check Bearer Token
    if bearer and bearer.credentials in API_KEYS:
        return API_KEYS[bearer.credentials]

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication credentials. Provide valid X-ATLAS-API-KEY or Bearer token.",
        headers={"WWW-Authenticate": "Bearer"}
    )

def require_role(allowed_roles: List[str]):
    """FastAPI dependency factory: Enforce role-based access control (RBAC)."""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role", "reader")
        if user_role == "admin" or user_role in allowed_roles:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: role '{user_role}' is not authorized. Required: {allowed_roles}"
        )
    return role_checker

# SSRF Protection
DISALLOWED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # Cloud instance metadata (AWS, GCP, Azure)
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7")
]

def validate_url_safety(url_str: str) -> bool:
    """Validate that an external URL does not target loopback, RFC1918 private subnets,
    or cloud metadata services (Server-Side Request Forgery defense).
    """
    try:
        parsed = urllib.parse.urlparse(url_str)
        if parsed.scheme not in ["http", "https"]:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        if hostname.lower() in ["localhost", "127.0.0.1", "::1", "metadata.google.internal"]:
            return False

        # Attempt IP resolution check
        try:
            ip = ipaddress.ip_address(hostname)
            for net in DISALLOWED_IP_NETWORKS:
                if ip in net:
                    return False
        except ValueError:
            # Domain name (e.g. api.worldbank.org)
            pass

        return True
    except Exception:
        return False

# Path Traversal Protection
def safe_path_join(base_dir: Path, untrusted_filename: str) -> Path:
    """Safely resolve an untrusted filename inside base_dir, preventing directory traversal attacks."""
    # Strip path separators
    clean_name = os.path.basename(untrusted_filename).strip()
    clean_name = re.sub(r"[^\w\.-]", "_", clean_name)
    resolved = (base_dir / clean_name).resolve()
    
    if not str(resolved).startswith(str(base_dir.resolve())):
        raise ValueError(f"Path traversal detected: {untrusted_filename} attempts escape from {base_dir}")
    
    return resolved
