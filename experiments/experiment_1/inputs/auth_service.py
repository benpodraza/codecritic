import json
from fastapi import Depends, HTTPException, Header, APIRouter, Request
from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher, exceptions
from jose import jwt, JWTError
import httpx, os, logging

from core_microservice.app.schemas.kafka.rbac import (
    LoginFailureEvent,
    LoginSuccessEvent,
    TokenIssuedEvent,
    LogoutEvent,
    TokenRevokedEvent,
    AuthorizationUseEvent
)

from core_microservice.app.schemas.redis.rbac import (
    TokenCacheSchema,
    RevokedTokenCacheSchema,
    UserRolesCacheSchema,
    RoleEntitlementsCacheSchema,
)

from core_microservice.app.schemas.kafka.alert import AlertEvent
from core_microservice.app.enums.alert_enums import AlertTypeEnum, AlertScopeEnum, AlertSourceEnum

from fastapi import HTTPException, Request
from datetime import datetime, timezone
import httpx
import logging

logger = logging.getLogger(__name__)
DATA_MICROSERVICE_URL = os.environ.get("DATA_MICROSERVICE_URL", "http://data-microservice.data.svc.cluster.local:8000")
SYSTEM_MICROSERVICE_URL = os.getenv("SYSTEM_MICROSERVICE_URI", "http://system-microservice.system.svc.cluster.local:8000")
JWT_ALGORITHM = os.environ.get("AUTH_ALGORITHM", "HS256")
JWT_ACTIVE_KID = os.environ.get("JWT_ACTIVE_KID", "default")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("AUTH_TOKEN_EXP_MINUTES", "30"))

JWT_KEYS = {
    JWT_ACTIVE_KID: os.environ.get("AUTH_SECRET_KEY", "REPLACE_ME")
}

router = APIRouter()
logger = logging.getLogger(__name__)
ph = PasswordHasher()

SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "change-this-key")
ALGORITHM = os.getenv("AUTH_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("AUTH_TOKEN_EXP_MINUTES", "30"))
JWT_KEYS = json.loads(os.getenv("JWT_KEYS", '{"default": "dev-secret"}'))
JWT_ACTIVE_KID = os.getenv("JWT_ACTIVE_KID", "default")
JWT_ALGORITHM = os.getenv("AUTH_ALGORITHM", "HS256")


def emit_alert(alert_type: AlertTypeEnum, payload: dict):
    alert = AlertEvent(
        alert_type=alert_type,
        alert_source=AlertSourceEnum.system_microservice,
        alert_scope=AlertScopeEnum.system,
        alert_payload=payload,
        alert_time=datetime.now(timezone.utc),
    )
    try:
        httpx.post(
            f"{SYSTEM_MICROSERVICE_URL}/kafka/publish",
            json={
                "topic": "alerts",
                "schema": "AlertEvent",
                "payload": alert.model_dump()
            },
            timeout=3.0
        )
    except Exception as e:
        logger.warning(f"Failed to emit alert to Kafka via route: {e}")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, plain)
    except exceptions.VerifyMismatchError:
        return False


async def authenticate_user(username: str, password: str, request: Request):
    try:
        ip = request.client.host

        async with httpx.AsyncClient() as client:
            try:
                await client.post(f"{DATA_MICROSERVICE_URL}/redis/login-attempts/ip/{ip}")
                await client.post(f"{DATA_MICROSERVICE_URL}/redis/login-attempts/user/{username}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise HTTPException(status_code=429, detail=e.response.json()["detail"])
                raise

            resp = await client.get(f"{DATA_MICROSERVICE_URL}/internal/users/by-username/{username}")
            resp.raise_for_status()
            user = resp.json()

            if not verify_password(password, user["hashed_pw"]):
                event = LoginFailureEvent(
                    username=username,
                    reason="invalid_password",
                    timestamp=datetime.now(timezone.utc)
                )
                httpx.post(
                    f"{SYSTEM_MICROSERVICE_URL}/kafka/rbac/login/failure",
                    json=event.model_dump(),
                    timeout=3.0
                )
                emit_alert(AlertTypeEnum.failed_login, {"username": username, "reason": "invalid_password"})
                raise HTTPException(status_code=401, detail="Invalid credentials")

            roles = (await client.get(f"{DATA_MICROSERVICE_URL}/internal/users/{user['id']}/roles")).json()
            entitlements = (await client.get(f"{DATA_MICROSERVICE_URL}/internal/users/{user['id']}/entitlements")).json()

            roles_payload = UserRolesCacheSchema(
                user_id=int(user['id']),
                role_ids=[r['id'] for r in roles],
                last_updated=datetime.now(timezone.utc)
            ).model_dump()
            await client.post(f"{DATA_MICROSERVICE_URL}/redis/rbac/user/{user['id']}/roles", json=roles_payload)

            for role in roles:
                ents = (await client.get(f"{DATA_MICROSERVICE_URL}/internal/roles/{role['id']}/entitlements")).json()
                ent_payload = RoleEntitlementsCacheSchema(
                    role_id=role['id'],
                    entitlement_ids=[e['id'] for e in ents],
                    last_updated=datetime.now(timezone.utc)
                ).model_dump()
                await client.post(f"{DATA_MICROSERVICE_URL}/redis/rbac/role/{role['id']}/entitlements", json=ent_payload)

        event = LoginSuccessEvent(user_id=int(user["id"]), timestamp=datetime.now(timezone.utc))
        httpx.post(
            f"{SYSTEM_MICROSERVICE_URL}/kafka/rbac/login/success",
            json=event.model_dump(),
            timeout=3.0
        )

        return user, roles, entitlements

    except httpx.HTTPError:
        event = LoginFailureEvent(username=username, reason="user_not_found", timestamp=datetime.now(timezone.utc))
        httpx.post(
            f"{SYSTEM_MICROSERVICE_URL}/kafka/rbac/login/failure",
            json=event.model_dump(),
            timeout=3.0
        )
        emit_alert(AlertTypeEnum.failed_login, {"username": username, "reason": "user_not_found"})
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=500, detail="Unable to authenticate user")


def create_access_token(user_id: UUID, username: str, roles: list[str], entitlements: list[str]) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=30)  # 30 minutes expiration (you can modify this)
    jti = str(uuid4())  # Generate a unique ID for the token

    payload = {
        "sub": str(user_id),
        "username": username,
        "roles": roles,
        "entitlements": entitlements,
        "jti": jti,
        "iat": now.timestamp(),
        "exp": expire.timestamp(),
        "kid": JWT_ACTIVE_KID,
    }

    # JWT encoding
    return jwt.encode(payload, JWT_KEYS[JWT_ACTIVE_KID], algorithm="HS256", headers={"kid": JWT_ACTIVE_KID})

def validate_access_token(token: str) -> dict:
    try:
        unverified = jwt.get_unverified_header(token)
        kid = unverified.get("kid")
        if kid is None or kid not in JWT_KEYS:
            raise HTTPException(status_code=403, detail="Unknown or missing token key ID")

        payload = jwt.decode(token, JWT_KEYS[kid], algorithms=[JWT_ALGORITHM])
        jti = payload.get("jti")
        if not jti:
            raise HTTPException(status_code=403, detail="Missing token ID")

        try:
            resp = httpx.get(f"{DATA_MICROSERVICE_URL}/redis/rbac/token/{jti}/revoked", timeout=3.0)
            if resp.status_code == 200:
                emit_alert(AlertTypeEnum.revoked_token_use, {"jti": jti})
                raise HTTPException(status_code=403, detail="Revoked token used")
        except httpx.HTTPStatusError as e:
            # Log the error and raise a 500 if the status code is not 404
            if e.response.status_code != 404:
                logger.error(f"Error during token validation: {str(e)}")
                raise HTTPException(status_code=500, detail="Token validation failure")
                
        # Ensure TTL refresh logic (only on success)
        try:
            httpx.post(
                f"{DATA_MICROSERVICE_URL}/redis/update-ttl",
                json={"key": f"auth:token:{jti}", "ttl_seconds": int(ACCESS_TOKEN_EXPIRE_MINUTES * 60)},
                timeout=3.0
            )
        except Exception as e:
            logger.warning(f"Failed to refresh token TTL for {jti}: {e}")

        return payload

    except JWTError as e:
        logger.warning(f"JWT decode failure: {str(e)}")
        raise HTTPException(status_code=403, detail="Invalid token")

def get_current_user(token: str):
    from system_microservice.app.services.auth_service import validate_access_token
    payload = validate_access_token(token)
    user_id = payload.get("sub")
    try:
        user = httpx.get(f"{DATA_MICROSERVICE_URL}/internal/users/{user_id}").json()
        rbac = httpx.get(f"{DATA_MICROSERVICE_URL}/rbac/entitlements/{user_id}").json()
        return user, rbac["roles"], rbac["entitlements"]
    except Exception as e:
        logger.error(f"User context retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Unable to retrieve user context")


def revoke_token_and_logout(token: str = Header(...)): 
    payload = validate_access_token(token)
    jti = payload["jti"]
    user_id = payload["sub"]  # Keep user_id as a string (UUID) instead of converting to int

    try:
        resp = httpx.get(f"{DATA_MICROSERVICE_URL}/redis/rbac/token/{jti}", timeout=3.0)
        if resp.status_code == 200:
            emit_alert(AlertTypeEnum.token_reuse, {"jti": jti, "user_id": user_id})

    except httpx.HTTPStatusError as e:
        if e.response.status_code != 404:
            raise HTTPException(status_code=500, detail="Error during token validation")

    try:
        payload_data = RevokedTokenCacheSchema(
            token_id=jti,
            revoked_at=datetime.now(timezone.utc),
            reason="manual_logout"
        ).model_dump()
        httpx.post(f"{DATA_MICROSERVICE_URL}/redis/rbac/revoked/{jti}", json=payload_data, timeout=3.0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke token: {e}")

    for path in (f"{DATA_MICROSERVICE_URL}/redis/delete/auth:token:{jti}", f"{DATA_MICROSERVICE_URL}/redis/delete/auth:user:{user_id}:roles"):  # noqa
        try:
            httpx.delete(path, timeout=3.0)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to clear user session: {e}")

    now = datetime.now(timezone.utc)
    logout_event = LogoutEvent(user_id=user_id, session_id=jti, timestamp=now)
    revoked_event = TokenRevokedEvent(
        token_id=jti,
        revoked_at=now,
        revoked_by_user_id=user_id,
        reason="manual_logout"
    )
    httpx.post(f"{SYSTEM_MICROSERVICE_URL}/kafka/rbac/logout", json=logout_event.model_dump(), timeout=3.0)
    httpx.post(f"{SYSTEM_MICROSERVICE_URL}/kafka/rbac/token/revoked", json=revoked_event.model_dump(), timeout=3.0)

    return {"status": "revoked"}


def require_entitlement(name: str):
    def wrapper(user_context=Depends(get_current_user)):
        user, roles, entitlements = user_context
        uid = int(user["id"])
        entitlement_names = [e["name"] for e in entitlements]

        matching_ent = next((e for e in entitlements if e["name"] == name), None)
        group_name = matching_ent.get("group_name") if matching_ent else None

        if name not in entitlement_names:
            emit_alert(AlertTypeEnum.role_violation, {
                "user_id": uid,
                "required_entitlement": name,
                "granted": entitlement_names
            })
            event = AuthorizationUseEvent(
                token_id=user.get("jti", "unknown"),
                user_id=uid,
                action=name,
                resource="unknown",
                timestamp=datetime.now(timezone.utc),
                result="denied",
                reason="role_violation",
                group_name=None
            )
            httpx.post(f"{SYSTEM_MICROSERVICE_URL}/kafka/rbac/authorization/use", json=event.model_dump(), timeout=3.0)
            raise HTTPException(status_code=403, detail="Insufficient entitlement")
        else:
            event = AuthorizationUseEvent(
                token_id=user.get("jti", "unknown"),
                user_id=uid,
                action=name,
                resource="unknown",
                timestamp=datetime.now(timezone.utc),
                result="allowed",
                group_name=group_name
            )
            httpx.post(f"{SYSTEM_MICROSERVICE_URL}/kafka/rbac/authorization/use", json=event.model_dump(), timeout=3.0)

    return wrapper

