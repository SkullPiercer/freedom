from typing import Annotated

from fastapi import Cookie, Depends, Header

from app.exceptions.auth import InvalidTokenException
from app.services.user import TokenService


async def get_current_user_id(
    access_token_cookie: Annotated[
        str | None,
        Cookie(alias="access_token"),
    ] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> int:
    token = access_token_cookie

    if token is None and authorization:
        scheme, _, credentials = authorization.partition(" ")
        if scheme.lower() == "bearer" and credentials:
            token = credentials

    if token is None:
        raise InvalidTokenException()

    payload = TokenService().decode_access_token(token)
    user_id = payload.get("user_id")
    if user_id is None:
        raise InvalidTokenException()

    return int(user_id)


CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]
