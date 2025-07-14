from typing import Dict, List, Optional

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from src.logger import logger


class ChatManager:
    def __init__(self) -> None:
        # Structure: {session_id: InMemoryChatMessageHistory}
        self.sessions: Dict[str, InMemoryChatMessageHistory] = {}

    def get_history(self, session_id: str) -> List[BaseMessage]:
        if session_id not in self.sessions:
            self.sessions[session_id] = InMemoryChatMessageHistory()
            logger.info(
                f"No chat history found for session_id '{session_id}', initializing new session."
            )
        return self.sessions[session_id].messages

    def add_message(
        self,
        session_id: str,
        role: str,
        message: str,
        chunks: Optional[List[str]] = None,
    ) -> None:
        if session_id not in self.sessions:
            self.sessions[session_id] = InMemoryChatMessageHistory()

        if role == "user":
            self.sessions[session_id].add_user_message(message)
        elif role == "assistant":
            additional_kwargs = {"chunks": chunks} if chunks else {}
            ai_message = AIMessage(content=message, additional_kwargs=additional_kwargs)
            self.sessions[session_id].add_message(ai_message)
        elif role == "system":
            self.sessions[session_id].add_message(SystemMessage(content=message))
        elif role == "context":
            self.sessions[session_id].add_message(
                BaseMessage(content=message, role="context")
            )
        else:
            logger.error(
                f"Invalid role '{role}' provided to add_message for session_id '{session_id}'"
            )
            raise ValueError("Role must be 'user', 'assistant', or 'system'")

    def get_last_n_messages(self, session_id: str, n: int = 5) -> List[BaseMessage]:
        if session_id not in self.sessions:
            logger.info(
                f"No chat history found for session_id '{session_id}' when requesting last {n} messages."
            )
            return []
        return self.sessions[session_id].messages[-n:]
