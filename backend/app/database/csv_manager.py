"""CSV Database Manager for Chat Messages"""
import csv
import os
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from threading import Lock
from ..config import settings
from ..core.exceptions import DatabaseError


class CSVManager:
    """Manager for CSV-based database operations"""

    def __init__(self):
        """Initialize CSV manager"""
        self.csv_path = settings.CSV_DATA_PATH
        self.chat_messages_file = os.path.join(self.csv_path, "chat_messages.csv")
        self.lock = Lock()

        # Ensure directory exists
        os.makedirs(self.csv_path, exist_ok=True)

        # Initialize CSV files with headers if they don't exist
        self._initialize_files()

    def _initialize_files(self):
        """Initialize CSV files with headers if they don't exist"""
        # Chat messages CSV
        if not os.path.exists(self.chat_messages_file):
            with open(self.chat_messages_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "id",
                        "session_id",
                        "user_message",
                        "bot_response",
                        "transcription",
                        "audio_url",
                        "timestamp",
                        "language_code",
                    ]
                )

    async def save_chat_message(
        self,
        message_id: str,
        session_id: str,
        user_message: str,
        bot_response: str,
        transcription: Optional[str] = None,
        audio_url: Optional[str] = None,
        language_code: Optional[str] = None,
    ) -> bool:
        """
        Save a chat message to CSV

        Args:
            message_id: Unique message ID
            session_id: Session ID
            user_message: User's message
            bot_response: Bot's response
            transcription: Optional transcription (for voice)
            audio_url: Optional audio URL
            language_code: Optional language code

        Returns:
            True if successful
        """
        try:
            with self.lock:
                with open(self.chat_messages_file, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            message_id,
                            session_id,
                            user_message,
                            bot_response,
                            transcription or "",
                            audio_url or "",
                            datetime.utcnow().isoformat(),
                            language_code or "",
                        ]
                    )
            return True
        except Exception as e:
            raise DatabaseError(f"Failed to save chat message: {str(e)}")

    async def get_chat_history(
        self, session_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict]:
        """
        Get chat history for a session

        Args:
            session_id: Session ID
            limit: Maximum number of messages to retrieve
            offset: Offset for pagination

        Returns:
            List of chat messages
        """
        try:
            messages = []
            with self.lock:
                if not os.path.exists(self.chat_messages_file):
                    return messages

                with open(self.chat_messages_file, "r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row["session_id"] == session_id:
                            messages.append(
                                {
                                    "id": row["id"],
                                    "session_id": row["session_id"],
                                    "user_message": row["user_message"],
                                    "bot_response": row["bot_response"],
                                    "transcription": row["transcription"],
                                    "audio_url": row["audio_url"],
                                    "timestamp": row["timestamp"],
                                    "language_code": row["language_code"],
                                }
                            )

            # Apply pagination
            start = offset
            end = offset + limit
            return messages[start:end]

        except Exception as e:
            raise DatabaseError(f"Failed to retrieve chat history: {str(e)}")

    async def get_all_sessions(self) -> List[str]:
        """Get all unique session IDs"""
        try:
            sessions = set()
            with self.lock:
                if not os.path.exists(self.chat_messages_file):
                    return []

                with open(self.chat_messages_file, "r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        sessions.add(row["session_id"])

            return list(sessions)

        except Exception as e:
            raise DatabaseError(f"Failed to retrieve sessions: {str(e)}")

    async def delete_session(self, session_id: str) -> bool:
        """Delete all messages for a session"""
        try:
            with self.lock:
                if not os.path.exists(self.chat_messages_file):
                    return True

                # Read all messages
                messages = []
                with open(self.chat_messages_file, "r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row["session_id"] != session_id:
                            messages.append(row)

                # Write back without deleted session
                with open(self.chat_messages_file, "w", newline="", encoding="utf-8") as f:
                    if messages:
                        writer = csv.DictWriter(f, fieldnames=messages[0].keys())
                        writer.writeheader()
                        writer.writerows(messages)
                    else:
                        writer = csv.writer(f)
                        writer.writerow(
                            [
                                "id",
                                "session_id",
                                "user_message",
                                "bot_response",
                                "transcription",
                                "audio_url",
                                "timestamp",
                                "language_code",
                            ]
                        )

            return True

        except Exception as e:
            raise DatabaseError(f"Failed to delete session: {str(e)}")


# Singleton instance
csv_manager = CSVManager()
