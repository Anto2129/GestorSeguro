"""Identificación de hardware (HWID) para registro y control de acceso"""

import os
import json
import hashlib
import platform
import subprocess
from typing import Optional
from pathlib import Path


class GestorHWID:
    """Gestiona la identificación de hardware del dispositivo"""

    # Clave usada en config_sistema.json
    _KEY_DISPOSITIVOS = "dispositivos_autorizados"
    _KEY_PRIMER_DISPOSITIVO = "dispositivo_maestro"

    # ──────────────────────────────────────────────────────────────────────
    # Obtención del HWID bruto
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def get_hwid() -> str:
        """
        Obtiene el identificador de hardware único del equipo.
        Usa el número de serie del disco duro (Windows/Linux/macOS).
        Como fallback usa combinación de hostname + plataforma.
        """
        sistema = platform.system()

        try:
            if sistema == "Windows":
                return GestorHWID._hwid_windows()
            elif sistema == "Linux":
                return GestorHWID._hwid_linux()
            elif sistema == "Darwin":
                return GestorHWID._hwid_macos()
        except Exception:
            pass

        return GestorHWID._hwid_fallback()

    @staticmethod
    def _hwid_windows() -> str:
        """Número de serie del disco C: vía WMI"""
        result = subprocess.run(
            ["wmic", "diskdrive", "get", "SerialNumber"],
            capture_output=True, text=True, timeout=5
        )
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip() and l.strip().lower() != "serialnumber"]
        if lines:
            return lines[0]
        # Alternativa: número de serie del volumen C:
        result2 = subprocess.run(
            ["vol", "C:"],
            capture_output=True, text=True, shell=True, timeout=5
        )
        for line in result2.stdout.splitlines():
            if "número de serie del volumen" in line.lower() or "volume serial number" in line.lower():
                return line.split()[-1]
        return GestorHWID._hwid_fallback()

    @staticmethod
    def _hwid_linux() -> str:
        """Machine ID en Linux"""
        for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
            try:
                return Path(path).read_text().strip()
            except Exception:
                pass
        return GestorHWID._hwid_fallback()

    @staticmethod
    def _hwid_macos() -> str:
        """IOPlatformSerialNumber en macOS"""
        result = subprocess.run(
            ["ioreg", "-l"], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if "IOPlatformSerialNumber" in line:
                return line.split("=")[-1].strip().strip('"')
        return GestorHWID._hwid_fallback()

    @staticmethod
    def _hwid_fallback() -> str:
        """Fallback: hostname + SO"""
        import socket
        return f"{socket.gethostname()}_{platform.node()}_{platform.machine()}"

    # ──────────────────────────────────────────────────────────────────────
    # Hash del HWID
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def get_hwid_hash() -> str:
        """Devuelve hash SHA-512 del HWID (para almacenamiento seguro)"""
        raw = GestorHWID.get_hwid()
        return hashlib.sha512(raw.encode()).hexdigest()

    # ──────────────────────────────────────────────────────────────────────
    # Registro y verificación de dispositivos
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def registrar_dispositivo(ruta_config: str, nombre_dispositivo: str = None) -> bool:
        """
        Registra el HWID actual como dispositivo autorizado.
        Si el archivo de config no existe o está vacío, este dispositivo
        se convierte en el dispositivo maestro.

        Args:
            ruta_config: Ruta de .config_sistema.json
            nombre_dispositivo: Etiqueta opcional (ej. "PC-Anton")

        Returns:
            True si el dispositivo fue registrado correctamente
        """
        hwid_hash = GestorHWID.get_hwid_hash()
        hwid_raw  = GestorHWID.get_hwid()

        if nombre_dispositivo is None:
            import socket
            nombre_dispositivo = socket.gethostname()

        # Cargar config existente
        config = {}
        if os.path.exists(ruta_config):
            try:
                with open(ruta_config, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception:
                config = {}

        # Inicializar lista de autorizados
        autorizados = config.get(GestorHWID._KEY_DISPOSITIVOS, {})
        es_primero  = len(autorizados) == 0

        # Registrar
        autorizados[hwid_hash] = {
            "nombre": nombre_dispositivo,
            "hwid_preview": hwid_raw[:12] + "...",  # Solo un fragmento por seguridad
            "registrado": _timestamp_now(),
            "maestro": es_primero
        }

        config[GestorHWID._KEY_DISPOSITIVOS] = autorizados
        if es_primero:
            config[GestorHWID._KEY_PRIMER_DISPOSITIVO] = hwid_hash

        try:
            with open(ruta_config, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            # Ocultar en Windows
            if os.name == "nt":
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(ruta_config, 2)
                except Exception:
                    pass

            return True
        except Exception:
            return False

    @staticmethod
    def verificar_dispositivo(ruta_config: str) -> bool:
        """
        Verifica si el dispositivo actual está autorizado.

        Returns:
            True si está autorizado (o si no hay ningún config → primer acceso)
        """
        if not os.path.exists(ruta_config):
            return True  # Primera ejecución: no hay restricciones todavía

        try:
            with open(ruta_config, "r", encoding="utf-8") as f:
                config = json.load(f)

            autorizados = config.get(GestorHWID._KEY_DISPOSITIVOS, {})

            if not autorizados:
                return True  # Sin dispositivos registrados aún

            hwid_hash = GestorHWID.get_hwid_hash()
            return hwid_hash in autorizados

        except Exception:
            return True  # En caso de error no bloqueamos el acceso

    @staticmethod
    def listar_dispositivos(ruta_config: str) -> list:
        """
        Obtiene lista de dispositivos registrados.

        Returns:
            Lista de dicts con info de cada dispositivo
        """
        if not os.path.exists(ruta_config):
            return []
        try:
            with open(ruta_config, "r", encoding="utf-8") as f:
                config = json.load(f)
            autorizados = config.get(GestorHWID._KEY_DISPOSITIVOS, {})
            result = []
            for hwid_h, info in autorizados.items():
                result.append({
                    "hwid_hash": hwid_h[:16] + "...",
                    "nombre": info.get("nombre", "Desconocido"),
                    "registrado": info.get("registrado", "-"),
                    "maestro": info.get("maestro", False)
                })
            return result
        except Exception:
            return []


# ──────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────

def _timestamp_now() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
