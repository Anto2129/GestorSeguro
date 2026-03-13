"""Módulo de seguridad y encriptación"""
import os
import json
import hashlib
import secrets
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from ui.colors import Colores


class SistemaSeguridad:
    """Gestiona encriptación, hashing y validación"""

    # Parámetros PBKDF2
    _PBKDF2_ITER  = 390_000   # OWASP 2023 recommendation for SHA-512
    _PBKDF2_DK_LEN = 64       # 512 bits de salida

    def __init__(self, key_path: Path):
        self.key_path = key_path

    # ------------------------------------------------------------------
    # Gestión de clave Fernet
    # ------------------------------------------------------------------

    def generar_clave_encriptacion(self) -> bytes:
        """Genera nueva clave Fernet (AES-128)"""
        print(f"{Colores.AZUL}   Generando clave NUEVA...{Colores.RESET}")
        key = Fernet.generate_key()
        self.key_path.write_bytes(key)

        if os.name == 'nt':
            import ctypes
            ctypes.windll.kernel32.SetFileAttributesW(str(self.key_path), 2)

        print(f"{Colores.VERDE}   ✓ Clave nueva generada{Colores.RESET}")
        return key

    def obtener_clave_encriptacion(self) -> bytes:
        """Obtiene la clave existente o genera una nueva"""
        if not self.key_path.exists():
            return self.generar_clave_encriptacion()
        try:
            key = self.key_path.read_bytes()
            Fernet(key)   # Validar
            return key
        except Exception:
            print(f"{Colores.ROJO}✗ Clave corrupta - Generando nueva...{Colores.RESET}")
            self.key_path.unlink(missing_ok=True)
            return self.generar_clave_encriptacion()

    generate_encryption_key = generar_clave_encriptacion
    get_encryption_key      = obtener_clave_encriptacion

    # ------------------------------------------------------------------
    # Encriptación / Desencriptación (Fernet AES)
    # ------------------------------------------------------------------

    def encriptar_contraseña(self, contraseña: str) -> Optional[str]:
        """Encripta contraseña con Fernet"""
        try:
            key    = self.obtener_clave_encriptacion()
            cipher = Fernet(key)
            enc    = cipher.encrypt(contraseña.encode())
            print(f"{Colores.VERDE}      ✓ Contraseña encriptada{Colores.RESET}")
            return enc.decode()
        except Exception as e:
            print(f"{Colores.ROJO}Error encriptando: {e}{Colores.RESET}")
            return None

    def desencriptar_contraseña(self, contraseña_encriptada: str) -> Optional[str]:
        """Desencripta contraseña con Fernet"""
        try:
            key    = self.obtener_clave_encriptacion()
            cipher = Fernet(key)
            dec    = cipher.decrypt(contraseña_encriptada.encode())
            return dec.decode()
        except Exception:
            print(f"{Colores.ROJO}✗ Error desencriptando{Colores.RESET}")
            return None

    encrypt_password = encriptar_contraseña
    decrypt_password = desencriptar_contraseña

    # ------------------------------------------------------------------
    # Triple Hash  (SHA-512 + BLAKE2b + PBKDF2-HMAC-SHA512)
    # ------------------------------------------------------------------

    @staticmethod
    def crear_hash_contraseña(contraseña: str) -> str:
        """
        Crea un triple hash de la contraseña.

        Los tres métodos utilizados son:
          1. SHA-512           – hash directo, 128 hex chars
          2. BLAKE2b           – más moderno, resistente a length-extension attacks
          3. PBKDF2-HMAC-SHA512 – key-derivation function con salt aleatorio e
                                   iteraciones, resistente a fuerza bruta

        Returns:
            JSON string con claves 's512', 'b2b', 'pb2', 'salt'
        """
        salt = secrets.token_bytes(32)
        salt_hex = salt.hex()

        # 1. SHA-512
        h_sha512 = hashlib.sha512(contraseña.encode()).hexdigest()

        # 2. BLAKE2b (512 bits)
        h_blake2b = hashlib.blake2b(contraseña.encode(), digest_size=64).hexdigest()

        # 3. PBKDF2-HMAC-SHA512 con salt
        h_pbkdf2 = hashlib.pbkdf2_hmac(
            'sha512',
            contraseña.encode(),
            salt,
            SistemaSeguridad._PBKDF2_ITER,
            dklen=SistemaSeguridad._PBKDF2_DK_LEN
        ).hex()

        return json.dumps({
            "s512": h_sha512,
            "b2b":  h_blake2b,
            "pb2":  h_pbkdf2,
            "salt": salt_hex
        }, separators=(',', ':'))

    @staticmethod
    def verificar_hash(contraseña: str, stored: str) -> bool:
        """
        Verifica una contraseña contra los tres hashes almacenados.
        Los TRES deben coincidir para considerar la contraseña válida.

        Args:
            contraseña: Contraseña en texto plano a verificar
            stored:     JSON string generado por `crear_hash_contraseña`

        Returns:
            True solo si los tres hashes coinciden
        """
        try:
            data = json.loads(stored)
        except (json.JSONDecodeError, TypeError):
            # Fallback: hash legacy (SHA-256 simple) → solo comprobamos SHA-256
            return hashlib.sha256(contraseña.encode()).hexdigest() == stored

        salt = bytes.fromhex(data["salt"])

        # 1. SHA-512
        ok1 = hashlib.sha512(contraseña.encode()).hexdigest() == data["s512"]

        # 2. BLAKE2b
        ok2 = hashlib.blake2b(contraseña.encode(), digest_size=64).hexdigest() == data["b2b"]

        # 3. PBKDF2-HMAC-SHA512
        pb2_check = hashlib.pbkdf2_hmac(
            'sha512',
            contraseña.encode(),
            salt,
            SistemaSeguridad._PBKDF2_ITER,
            dklen=SistemaSeguridad._PBKDF2_DK_LEN
        ).hex()
        ok3 = pb2_check == data["pb2"]

        return ok1 and ok2 and ok3

    # Alias en inglés
    @staticmethod
    def create_hash_password(contraseña: str) -> str:
        return SistemaSeguridad.crear_hash_contraseña(contraseña)

    @staticmethod
    def verify_hash(contraseña: str, stored: str) -> bool:
        return SistemaSeguridad.verificar_hash(contraseña, stored)


# Alias para compatibilidad
SecurityManager = SistemaSeguridad