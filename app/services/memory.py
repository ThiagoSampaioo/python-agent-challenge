from __future__ import annotations

import time
from typing import Any


class SessionMemory:
    def __init__(self, ttl_seconds: int = 1800, max_messages: int = 4) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_messages = max_messages
        self._store: dict[str, dict[str, Any]] = {}

    def get_history(self, session_id: str | None) -> list[dict[str, Any]]:
        if not session_id:
            return []

        self._cleanup_expired()

        session = self._store.get(session_id)
        if not session:
            return []

        return session["messages"]

    def add_message(
        self,
        session_id: str | None,
        role: str,
        content: str,
        sources: list[str] | None = None,
    ) -> None:
        if not session_id:
            return

        self._cleanup_expired()

        now = time.time()
        session = self._store.get(session_id)

        if not session:
            session = {
                "updated_at": now,
                "messages": [],
            }
            self._store[session_id] = session

        session["updated_at"] = now
        session["messages"].append(
            {
                "role": role,
                "content": content.strip(),
                "sources": sources or [],
            }
        )

        session["messages"] = session["messages"][-self.max_messages :]

    def get_last_assistant_message(self, session_id: str | None) -> dict[str, Any] | None:
        history = self.get_history(session_id)
        for item in reversed(history):
            if item.get("role") == "assistant" and item.get("content", "").strip():
                return item
        return None

    def clear_session(self, session_id: str) -> None:
        self._store.pop(session_id, None)

    def _cleanup_expired(self) -> None:
        now = time.time()
        expired_keys = []

        for session_id, session_data in self._store.items():
            updated_at = session_data.get("updated_at", 0)
            if now - updated_at > self.ttl_seconds:
                expired_keys.append(session_id)

        for session_id in expired_keys:
            self._store.pop(session_id, None)