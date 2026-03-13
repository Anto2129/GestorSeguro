"""Configuración global del sistema"""

import os
from pathlib import Path
from typing import Optional


class PasswordPolicy:
    """Política de contraseñas del sistema"""

    MIN_LENGTH_MANUAL = 8
    MIN_LENGTH_AUTO = 12
    MAX_LENGTH = 28
    MIN_LENGTH_USERNAME = 5
    MAX_LENGTH_USERNAME = 20
    SPECIAL_CHARS = "@#.$%&*!?-_+="
    MAX_LOGIN_ATTEMPTS = 3


class Configuracion:
    """Configuración central del sistema"""

    # Directorios
    CARPETA_TRABAJO = ".GestorSeguro"

    # Nombres de archivos
    ARCHIVO_LOG = "usuarios_log.xlsx"
    ARCHIVO_BACKUP = ".usuarios_backup.xlsx"
    ARCHIVO_AUDITORIA = ".auditoria_log.json"
    ARCHIVO_CONTRASEÑAS = ".contraseñas_encriptadas.json"
    ARCHIVO_CLAVE = ".clave_maestra.key"
    ARCHIVO_CONFIG = ".config_sistema.json"

    # Seguridad (mantener compatibilidad con código existente)
    MIN_LONGITUD_CONTRASEÑA_MANUAL = 8
    MIN_LONGITUD_CONTRASEÑA_AUTO = 12
    MAX_LONGITUD_CONTRASEÑA = 28
    MIN_LONGITUD_USUARIO = 5
    MAX_LONGITUD_USUARIO = 20
    CARACTERES_ESPECIALES = "@#.$%&*!?-_+="
    MAX_INTENTOS_LOGIN = 3
    TAMAÑO_MINIMO_USB = 100 * 1024 * 1024  # 100 MB

    def __init__(self, carpeta_trabajo: str = None):
        """
        Inicializa configuración.

        Args:
            carpeta_trabajo: Ruta directa a la carpeta de trabajo (opcional).
        """
        self.carpeta_trabajo: Optional[str] = None
        self.ruta_usb: Optional[str] = None
        self._rutas_archivos = {}
        self.password_policy = PasswordPolicy()

        # Rutas como Path (usadas por storage managers)
        self.archivo_log: Optional[Path] = None
        self.archivo_backup: Optional[Path] = None
        self.archivo_auditoria: Optional[Path] = None
        self.archivo_contraseñas: Optional[Path] = None
        self.archivo_clave: Optional[Path] = None
        self.archivo_config: Optional[Path] = None

        if carpeta_trabajo:
            self.establecer_carpeta_trabajo(carpeta_trabajo)

    def establecer_carpeta_trabajo(self, ruta: str) -> None:
        """Establece carpeta de trabajo"""
        self.carpeta_trabajo = ruta
        self._actualizar_rutas()

    def establecer_ruta_usb(self, ruta: str) -> None:
        """Establece ruta USB base"""
        self.ruta_usb = ruta
        self._actualizar_rutas()

    def _actualizar_rutas(self) -> None:
        """Actualiza rutas de todos los archivos"""
        if not self.carpeta_trabajo:
            return

        self._rutas_archivos = {
            'log': os.path.join(self.carpeta_trabajo, self.ARCHIVO_LOG),
            'backup': os.path.join(self.carpeta_trabajo, self.ARCHIVO_BACKUP),
            'auditoria': os.path.join(self.carpeta_trabajo, self.ARCHIVO_AUDITORIA),
            'contraseñas': os.path.join(self.carpeta_trabajo, self.ARCHIVO_CONTRASEÑAS),
            'clave': os.path.join(self.carpeta_trabajo, self.ARCHIVO_CLAVE),
            'config': os.path.join(self.carpeta_trabajo, self.ARCHIVO_CONFIG),
        }

        # Path objects para los storage managers
        base = Path(self.carpeta_trabajo)
        self.archivo_log = base / self.ARCHIVO_LOG
        self.archivo_backup = base / self.ARCHIVO_BACKUP
        self.archivo_auditoria = base / self.ARCHIVO_AUDITORIA
        self.archivo_contraseñas = base / self.ARCHIVO_CONTRASEÑAS
        self.archivo_clave = base / self.ARCHIVO_CLAVE
        self.archivo_config = base / self.ARCHIVO_CONFIG

    def get_working_directory(self) -> Optional[str]:
        """Retorna la carpeta de trabajo actual"""
        return self.carpeta_trabajo

    def obtener_ruta(self, tipo_archivo: str) -> Optional[str]:
        """Obtiene ruta de archivo específico"""
        return self._rutas_archivos.get(tipo_archivo)

    def obtener_todas_rutas(self) -> dict:
        """Obtiene todas las rutas configuradas"""
        return self._rutas_archivos.copy()

    @staticmethod
    def validar_carpeta_trabajo(ruta: str) -> bool:
        """Valida que la carpeta de trabajo sea accesible"""
        try:
            return os.path.isdir(ruta) and os.access(ruta, os.W_OK)
        except Exception:
            return False


# Alias para compatibilidad con main.py y menu.py
AppConfig = Configuracion

# Instancia global de configuración
config_global = Configuracion()