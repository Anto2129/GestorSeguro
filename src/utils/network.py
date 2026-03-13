"""Utilidades de red"""
import socket
from typing import Optional


class RedUtils:
    """Utilidades de red e información del sistema"""

    @staticmethod
    def get_device_ip() -> str:
        """Obtiene la dirección IP del dispositivo"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            try:
                return socket.gethostbyname(socket.gethostname())
            except Exception:
                return "IP No disponible"

    @staticmethod
    def get_system_username() -> str:
        """Obtiene nombre de usuario del sistema"""
        import getpass
        try:
            return getpass.getuser()
        except Exception:
            return "Usuario desconocido"

    @staticmethod
    def get_device_info() -> str:
        """Obtiene información del dispositivo en formato @usuario | IP: xxx"""
        username = RedUtils.get_system_username()
        ip = RedUtils.get_device_ip()
        return f"@{username} | IP: {ip}"