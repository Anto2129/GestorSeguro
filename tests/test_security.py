"""Pruebas para seguridad"""

import pytest
import json
from src.core.security import SistemaSeguridad


class TestSistemaSeguridad:
    """Pruebas del sistema de seguridad"""

    def test_crear_hash_devuelve_json(self):
        """El triple hash devuelve un JSON con los 3 métodos + salt"""
        contraseña = "TestPassword123"
        hash_json = SistemaSeguridad.crear_hash_contraseña(contraseña)

        data = json.loads(hash_json)
        assert "s512" in data  # SHA-512
        assert "b2b"  in data  # BLAKE2b
        assert "pb2"  in data  # PBKDF2-HMAC-SHA512
        assert "salt" in data

        # SHA-512 produce 128 hex chars, BLAKE2b-512 produce 128 hex chars
        assert len(data["s512"]) == 128
        assert len(data["b2b"])  == 128
        # PBKDF2 produce 64 bytes → 128 hex chars
        assert len(data["pb2"])  == 128

    def test_hash_verificacion_correcta(self):
        """verificar_hash devuelve True para la contraseña correcta"""
        contraseña = "TestPassword123"
        stored = SistemaSeguridad.crear_hash_contraseña(contraseña)
        assert SistemaSeguridad.verificar_hash(contraseña, stored) is True

    def test_hash_verificacion_incorrecta(self):
        """verificar_hash devuelve False para contraseña errónea"""
        stored = SistemaSeguridad.crear_hash_contraseña("ContraseñaReal")
        assert SistemaSeguridad.verificar_hash("ContraseñaFalsa", stored) is False

    def test_salt_unico_por_hash(self):
        """Cada llamada genera un salt diferente → hashes distintos"""
        contraseña = "MismaContraseña"
        hash1 = SistemaSeguridad.crear_hash_contraseña(contraseña)
        hash2 = SistemaSeguridad.crear_hash_contraseña(contraseña)

        # Los hashes completos son distintos (por el salt aleatorio en PBKDF2)
        assert hash1 != hash2
        # Pero SHA-512 y BLAKE2b son deterministas → los s512/b2b coinciden
        d1, d2 = json.loads(hash1), json.loads(hash2)
        assert d1["s512"] == d2["s512"]
        assert d1["b2b"]  == d2["b2b"]
        # PBKDF2 difiere por el salt
        assert d1["pb2"]  != d2["pb2"]

    def test_hashes_diferentes_para_distintas_contraseñas(self):
        """Contraseñas diferentes producen hashes distintos (SHA-512 y BLAKE2b)"""
        d1 = json.loads(SistemaSeguridad.crear_hash_contraseña("pass1"))
        d2 = json.loads(SistemaSeguridad.crear_hash_contraseña("pass2"))
        assert d1["s512"] != d2["s512"]
        assert d1["b2b"]  != d2["b2b"]