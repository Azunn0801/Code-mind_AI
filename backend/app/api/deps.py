from dataclasses import dataclass

from fastapi import Depends, Header, Request

from ..core.config import Settings
from ..core.demo_auth import DemoTokenError, DemoTokenExpired, verify_demo_token
from ..core.errors import DomainError
from ..domain.models import User
from ..domain.ports import Repository
from ..infrastructure.ai import AIGateway
from ..infrastructure.runner import CodeRunner


@dataclass(slots=True)
class Container:
    repo: Repository
    runner: CodeRunner
    ai_gateway: AIGateway
    settings: Settings


def get_container(request: Request) -> Container:
    return request.app.state.container


def get_current_user(
    container: Container,
    authorization: str | None = Header(default=None),
    x_demo_user: str | None = Header(default=None),
) -> User:
    user_id: str | None = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
        if container.settings.auth_mode == "demo":
            try:
                user_id = verify_demo_token(token, container.settings.demo_token_secret)
            except DemoTokenExpired as exc:
                raise DomainError("token_expired", "Phiên demo đã hết hạn. Vui lòng tạo phiên mới.", 401) from exc
            except DemoTokenError as exc:
                raise DomainError("invalid_token", "Phiên đăng nhập không hợp lệ.", 401) from exc
    if not user_id and x_demo_user and container.settings.app_env != "production":
        user_id = x_demo_user
    if not user_id:
        raise DomainError("authentication_required", "Vui lòng đăng nhập để tiếp tục.", 401)
    user = container.repo.get_user(user_id)
    if not user:
        raise DomainError("invalid_token", "Phiên đăng nhập không hợp lệ.", 401)
    return user


def current_user(
    container: Container = Depends(get_container),
    authorization: str | None = Header(default=None),
    x_demo_user: str | None = Header(default=None),
) -> User:
    return get_current_user(container, authorization, x_demo_user)
