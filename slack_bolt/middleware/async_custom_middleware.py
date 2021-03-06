import inspect
from logging import Logger
from typing import Callable, Awaitable, Any, Sequence

from slack_bolt.kwargs_injection.async_utils import build_async_required_kwargs
from slack_bolt.logger import get_bolt_app_logger
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse
from .async_middleware import AsyncMiddleware


class AsyncCustomMiddleware(AsyncMiddleware):
    app_name: str
    func: Callable[..., Awaitable[Any]]
    arg_names: Sequence[str]
    logger: Logger

    def __init__(self, *, app_name: str, func: Callable[..., Awaitable[Any]]):
        self.app_name = app_name
        if inspect.iscoroutinefunction(func):
            self.func = func
        else:
            raise ValueError("Async middleware function must be an async function")

        self.arg_names = inspect.getfullargspec(func).args
        self.logger = get_bolt_app_logger(self.app_name, self.func)

    async def async_process(
        self,
        *,
        req: AsyncBoltRequest,
        resp: BoltResponse,
        next: Callable[[], Awaitable[BoltResponse]],
    ) -> BoltResponse:
        return await self.func(
            **build_async_required_kwargs(
                logger=self.logger,
                required_arg_names=self.arg_names,
                request=req,
                response=resp,
                next_func=next,
                this_func=self.func,
            )
        )

    @property
    def name(self) -> str:
        return f"AsyncCustomMiddleware(func={self.func.__name__})"
