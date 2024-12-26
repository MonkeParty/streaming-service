from fastapi import HTTPException, Header, status
from jose import jwt, JWTError

import httpx

from .config import settings


def get_current_user_id(token: str = Header(..., alias="Authorization")):
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing Authorization header")

    try:
        payload = jwt.decode(token[len("Bearer "):], settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload.get('id')
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def user_is_admin(user_id: int) -> bool:
    try:
        return httpx.get(f'{settings.auth_service_address}/{user_id}/is_admin').status_code == status.HTTP_200_OK
    except:
        return False

def can_user_action_on_movie(user_id: int, action: str, movie_id: int) -> bool:
    try:
        return httpx.get(f'{settings.auth_service_address}/can-user-{action}-movie/{user_id}/{movie_id}').status_code == status.HTTP_200_OK
    except:
        return False