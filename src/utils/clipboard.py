"""Utilidades de portapapeles"""
from typing import Optional


class PortapapelesUtils:
    """Utilidades de portapapeles"""

    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """Copia texto al portapapeles"""
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except Exception:
            return False

    @staticmethod
    def get_from_clipboard() -> Optional[str]:
        """Obtiene texto del portapapeles"""
        try:
            import pyperclip
            return pyperclip.paste()
        except Exception:
            return None