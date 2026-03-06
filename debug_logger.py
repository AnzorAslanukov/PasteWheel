"""
Debug Logger - Writes debug messages to debug.txt
"""
import os
from datetime import datetime

DEBUG_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug.txt")


class DebugLogger:
    """
    A simple logger that writes debug messages to debug.txt.
    Each Python file that uses this logger should define a module-level
    DEBUG boolean variable. When set to True, debug messages will be written.
    """

    @staticmethod
    def log(message: str) -> None:
        """
        Write a debug message to debug.txt with a timestamp.

        Args:
            message: The string message to log.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}\n"
        try:
            with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            # Fallback: silently fail if we can't write to the log file
            pass

    @staticmethod
    def log_section(section_title: str) -> None:
        """
        Write a section separator to debug.txt.

        Args:
            section_title: The title of the section.
        """
        separator = "=" * 60
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"\n{separator}\n[{timestamp}] {section_title}\n{separator}\n"
        try:
            with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            pass