"""Utilidades de fecha y hora"""
from datetime import datetime
from typing import Optional


class FechaUtils:
    """Utilidades de fecha y hora agrupadas"""

    @staticmethod
    def get_current_datetime_formatted() -> str:
        """Obtiene fecha/hora actual formateada"""
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    @staticmethod
    def parse_datetime_from_string(date_str: str) -> Optional[datetime]:
        """Parsea string a datetime"""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            return None

    @staticmethod
    def is_date_in_range(
        date_str: str,
        start_date: str,
        end_date: str
    ) -> bool:
        """Verifica si fecha está en rango"""
        date = FechaUtils.parse_datetime_from_string(date_str)
        start = datetime.strptime(start_date, "%d/%m/%Y")
        end = datetime.strptime(end_date, "%d/%m/%Y").replace(
            hour=23, minute=59, second=59
        )
        
        if date is None:
            return False
        
        return start <= date <= end