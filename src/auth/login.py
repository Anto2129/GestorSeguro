"""Sistema de autenticación"""

import os
import json
import getpass
from datetime import datetime
from core.security import SistemaSeguridad
from ui.colors import Colores


class SistemaLogin:
    """Gestiona autenticación del sistema"""

    def __init__(self, ruta_config: str):
        """
        Inicializa sistema de login

        Args:
            ruta_config: Ruta del archivo de configuración
        """
        self.ruta_config = ruta_config

    def primera_ejecucion(self) -> bool:
        """Verifica si es primera ejecución"""
        return not os.path.exists(self.ruta_config)

    def configurar_contraseña_maestra(self) -> bool:
        """
        Configura contraseña maestra en primera ejecución

        Returns:
            True si se configuró exitosamente
        """
        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}CONFIGURAR CONTRASEÑA MAESTRA{Colores.RESET}".center(70))
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}\n")

        print(f"{Colores.AMARILLO}⚠️  IMPORTANTE:{Colores.RESET}")
        print(f"{Colores.BLANCO}Esta contraseña protege el acceso al gestor{Colores.RESET}")
        print(f"{Colores.BLANCO}Si la olvidas, NO podrá recuperarse{Colores.RESET}\n")

        while True:
            contraseña = getpass.getpass(
                f"{Colores.AMARILLO}Ingresa contraseña (mín. 8 caracteres): {Colores.RESET}"
            )

            if len(contraseña) < 8:
                print(f"{Colores.ROJO}✗ Mínimo 8 caracteres{Colores.RESET}")
                continue

            confirmacion = getpass.getpass(
                f"{Colores.AMARILLO}Confirma la contraseña: {Colores.RESET}"
            )

            if contraseña != confirmacion:
                print(f"{Colores.ROJO}✗ Las contraseñas no coinciden{Colores.RESET}\n")
                continue

            break

        hash_contraseña = SistemaSeguridad.crear_hash_contraseña(contraseña)

        config = {
            'contraseña_maestra_hash': hash_contraseña,
            'fecha_creacion': datetime.now().isoformat(),
            'version': '7.0.0'
        }

        try:
            with open(self.ruta_config, 'w') as f:
                json.dump(config, f, indent=2)

            self._ocultar_archivo()
            print(f"\n{Colores.VERDE}✓ Contraseña maestra configurada{Colores.RESET}\n")
            return True
        except Exception as e:
            print(f"{Colores.ROJO}Error guardando configuración: {e}{Colores.RESET}")
            return False

    def autenticar(self, max_intentos: int = 3) -> bool:
        """
        Autentica usuario

        Args:
            max_intentos: Número máximo de intentos

        Returns:
            True si autenticación exitosa
        """
        if self.primera_ejecucion():
            return self.configurar_contraseña_maestra()

        print(f"\n{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}")
        print(f"{Colores.CYAN}{Colores.NEGRITA}AUTENTICACIÓN{Colores.RESET}".center(70))
        print(f"{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}\n")

        intentos = max_intentos
        while intentos > 0:
            contraseña = getpass.getpass(
                f"{Colores.AMARILLO}Contraseña maestra: {Colores.RESET}"
            )

            if self._verificar_contraseña(contraseña):
                print(f"{Colores.VERDE}✓ Autenticado{Colores.RESET}\n")
                return True

            intentos -= 1
            if intentos > 0:
                print(f"{Colores.ROJO}✗ Incorrecta. Intentos restantes: {intentos}{Colores.RESET}")
            else:
                print(f"{Colores.ROJO}✗ Acceso denegado{Colores.RESET}")

        return False

    # Alias en inglés para compatibilidad
    def authenticate(self, max_attempts: int = 3) -> bool:
        """Alias en inglés de :meth:`autenticar`"""
        return self.autenticar(max_attempts)

    def _verificar_contraseña(self, contraseña: str) -> bool:
        """Verifica contraseña maestra"""
        try:
            with open(self.ruta_config, 'r') as f:
                config = json.load(f)

            hash_almacenado = config.get('contraseña_maestra_hash')
            return SistemaSeguridad.verificar_hash(contraseña, hash_almacenado)
        except Exception:
            return False

    def _ocultar_archivo(self) -> None:
        """Oculta archivo de configuración"""
        if os.name == 'nt':
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(self.ruta_config, 2)
            except Exception:
                pass


# Alias en inglés para compatibilidad
LoginManager = SistemaLogin