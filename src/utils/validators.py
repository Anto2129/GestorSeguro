"""Validadores de entrada"""
from config.settings import PasswordPolicy


class Validadores:
    """Validadores de entrada a través de utilidades"""

    @staticmethod
    def validate_username(username: str, min_length: int = 5) -> tuple[bool, str]:
        """Valida nombre de usuario"""
        if len(username) < min_length:
            return False, f"Mínimo {min_length} caracteres"
        
        if not username.isalnum():
            return False, "Solo alfanuméricos permitidos"
        
        return True, "Válido"

    @staticmethod
    def validate_password_manual(
        password: str, 
        policy: PasswordPolicy
    ) -> tuple[bool, dict]:
        """Valida contraseña manual (requisitos reducidos)"""
        has_special = any(c in policy.SPECIAL_CHARS for c in password)
        has_upper = any(c.isupper() for c in password)
        is_alphanumeric = all(
            c.isalnum() or c in policy.SPECIAL_CHARS for c in password
        )
        length_valid = len(password) >= policy.MIN_LENGTH_MANUAL
        
        details = {
            'Longitud mínima 8 caracteres': length_valid,
            'Alfanuméricos + caracteres especiales': is_alphanumeric,
            'Al menos una mayúscula': has_upper,
            'Al menos un carácter especial': has_special
        }
        
        return all(details.values()), details

    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """Valida formato de fecha DD/MM/YYYY"""
        from datetime import datetime
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False