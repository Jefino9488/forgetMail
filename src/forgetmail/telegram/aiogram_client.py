from __future__ import annotations

import atexit
import asyncio
from dataclasses import dataclass
import threading
from typing import Any, Awaitable, Callable, TypeVar

from aiogram import Bot
from aiogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update

T = TypeVar("T")


def _build_summary(subject: str, reason: str) -> str:
    subject_value = " ".join(subject.split())
    reason_value = " ".join(reason.split())
    summary = f"{subject_value}. {reason_value}".strip(" .")
    if len(summary) > 220:
        return summary[:217].rstrip() + "..."
    return summary


@dataclass
class SignalNotificationPayload:
    message_id: str
    thread_id: str
    sender: str
    subject: str
    reason: str
    score: float


class AiogramBotClient:
    _loop: asyncio.AbstractEventLoop | None = None
    _bots: dict[str, Bot] = {}
    _lock = threading.RLock()
    _atexit_registered = False

    @classmethod
    def _ensure_loop_locked(cls) -> asyncio.AbstractEventLoop:
        if cls._loop is None or cls._loop.is_closed():
            cls._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(cls._loop)

        if not cls._atexit_registered:
            atexit.register(cls.close_all)
            cls._atexit_registered = True

        return cls._loop

    @classmethod
    def _run_coro_locked(cls, coro: Awaitable[T]) -> T:
        loop = cls._ensure_loop_locked()
        if loop.is_running():
            # Fallback for unexpected re-entrant calls from async contexts.
            temp_loop = asyncio.new_event_loop()
            try:
                return temp_loop.run_until_complete(coro)
            finally:
                try:
                    temp_loop.run_until_complete(temp_loop.shutdown_asyncgens())
                except Exception:
                    pass
                temp_loop.close()
        return loop.run_until_complete(coro)

    @classmethod
    def close_all(cls) -> None:
        with cls._lock:
            if cls._loop is None or cls._loop.is_closed():
                cls._bots.clear()
                cls._loop = None
                return

            loop = cls._loop
            bots = list(cls._bots.values())
            cls._bots = {}

            async def _close_sessions() -> None:
                for bot in bots:
                    try:
                        await bot.session.close()
                    except Exception:
                        pass

            try:
                loop.run_until_complete(_close_sessions())
            except Exception:
                pass

            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            except Exception:
                pass

            loop.close()
            cls._loop = None

    def _run_with_bot(self, token: str, operation: Callable[[Bot], Awaitable[T]]) -> T:
        async def _wrapped() -> T:
            bot = self._bots.get(token)
            if bot is None:
                bot = Bot(token=token)
                self._bots[token] = bot
            return await operation(bot)

        with self._lock:
            return self._run_coro_locked(_wrapped())

    def validate_token(self, token: str) -> dict[str, Any]:
        async def _operation(bot: Bot) -> dict[str, Any]:
            me = await bot.get_me()
            return {
                "id": int(me.id),
                "is_bot": bool(me.is_bot),
                "username": me.username or "",
                "first_name": me.first_name or "",
            }

        return self._run_with_bot(token, _operation)

    def prepare_polling(self, token: str, *, drop_pending_updates: bool = False) -> None:
        async def _operation(bot: Bot) -> None:
            await bot.delete_webhook(drop_pending_updates=drop_pending_updates)

        self._run_with_bot(token, _operation)

    def detect_chat_id(self, token: str) -> int:
        async def _operation(bot: Bot) -> int:
            updates = await bot.get_updates(limit=5, timeout=0)
            for update in reversed(updates):
                if update.message and update.message.chat:
                    return int(update.message.chat.id)
            raise RuntimeError(
                "No Telegram messages found for this bot. Send any message to your bot and run --onboard again."
            )

        return self._run_with_bot(token, _operation)

    def fetch_updates(
        self,
        token: str,
        offset: int | None,
        limit: int = 20,
        poll_timeout_seconds: int = 2,
    ) -> list[Update]:
        async def _operation(bot: Bot) -> list[Update]:
            updates = await bot.get_updates(
                offset=offset,
                limit=limit,
                timeout=max(0, int(poll_timeout_seconds)),
            )
            return updates

        return self._run_with_bot(token, _operation)

    def configure_bot_commands(self, token: str, commands: list[dict[str, str]]) -> None:
        async def _operation(bot: Bot) -> None:
            payload = [
                BotCommand(command=item["command"], description=item["description"])
                for item in commands
            ]
            await bot.set_my_commands(payload)

        self._run_with_bot(token, _operation)

    def send_text_message(self, token: str, chat_id: int, text: str) -> None:
        async def _operation(bot: Bot) -> None:
            await bot.send_message(chat_id=chat_id, text=text)

        self._run_with_bot(token, _operation)

    def send_text_message_with_url_button(
        self,
        token: str,
        chat_id: int,
        text: str,
        *,
        button_text: str,
        url: str,
    ) -> None:
        async def _operation(bot: Bot) -> None:
            markup = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=button_text, url=url)]]
            )
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

        self._run_with_bot(token, _operation)

    def answer_callback_query(self, token: str, callback_query_id: str, text: str) -> None:
        async def _operation(bot: Bot) -> None:
            await bot.answer_callback_query(
                callback_query_id=callback_query_id,
                text=text,
                show_alert=False,
            )

        self._run_with_bot(token, _operation)

    def send_signal_notifications(
        self,
        token: str,
        chat_id: int,
        signals: list[SignalNotificationPayload],
    ) -> set[str]:
        async def _operation(bot: Bot) -> set[str]:
            sent_ids: set[str] = set()
            for signal in signals:
                summary = _build_summary(str(signal.subject), str(signal.reason))
                text = (
                    "Important email summary\n"
                    f"From: {signal.sender}\n"
                    f"Summary: {summary}\n"
                    f"Score: {float(signal.score):.2f}"
                )
                markup = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Important",
                                callback_data=f"important:{signal.message_id}:{signal.thread_id}",
                            ),
                            InlineKeyboardButton(
                                text="Mute email",
                                callback_data=(
                                    f"notimportant:{signal.message_id}:{signal.thread_id}:message"
                                ),
                            ),
                            InlineKeyboardButton(
                                text="Mute thread",
                                callback_data=(
                                    f"notimportant:{signal.message_id}:{signal.thread_id}:thread"
                                ),
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="Undo mute",
                                callback_data=f"undo:{signal.message_id}:{signal.thread_id}",
                            ),
                            InlineKeyboardButton(
                                text="Reply", callback_data=f"reply:{signal.thread_id}"
                            ),
                        ],
                    ]
                )
                await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
                sent_ids.add(str(signal.message_id))
            return sent_ids

        return self._run_with_bot(token, _operation)
