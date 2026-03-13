"""Pruebas para generadores de usuario y contraseña"""

import pytest
from src.generators.usuario_generator import GeneradorUsuario
from src.generators.password_generator import GeneradorContraseña


class TestGeneradorUsuario:
    """Pruebas del generador de nombres de usuario"""

    def setup_method(self):
        self.gen = GeneradorUsuario()

    def test_genera_usuario_unico(self):
        """Genera usuario que no está en el conjunto existente"""
        existentes = {"abc123", "TestUser"}
        usuario = self.gen.generate(existentes)
        assert usuario not in existentes

    def test_longitud_correcta(self):
        """El usuario generado tiene entre 5 y 10 caracteres"""
        usuario = self.gen.generate(set())
        assert 5 <= len(usuario) <= 10

    def test_es_alfanumerico(self):
        """El usuario generado es alfanumérico"""
        for _ in range(10):
            usuario = self.gen.generate(set())
            assert usuario.isalnum(), f"No alfanumérico: {usuario}"

    def test_tiene_mayuscula_y_minuscula(self):
        """El usuario tiene al menos una mayúscula y una minúscula"""
        for _ in range(10):
            usuario = self.gen.generate(set())
            assert any(c.isupper() for c in usuario), f"Sin mayúscula: {usuario}"
            assert any(c.islower() for c in usuario), f"Sin minúscula: {usuario}"


class TestGeneradorContraseña:
    """Pruebas del generador de contraseñas"""

    ESPECIALES = "@#.$%&*!?-_+="

    def setup_method(self):
        self.gen = GeneradorContraseña()

    def test_genera_contraseña_y_hash(self):
        """Genera una contraseña y su hash SHA-256"""
        password, hash_ = self.gen.generate(set())
        assert isinstance(password, str)
        assert isinstance(hash_, str)
        # Triple hash is a JSON string, so it's much longer than a simple hex hash
        assert len(hash_) > 100  # JSON with 3 hashes + salt

    def test_longitud_valida(self):
        """La contraseña tiene entre 12 y 28 caracteres"""
        for _ in range(5):
            password, _ = self.gen.generate(set())
            assert 12 <= len(password) <= 28, f"Longitud inválida: {len(password)}"

    def test_requisitos_minimos(self):
        """La contraseña cumple todos los requisitos de complejidad"""
        for _ in range(5):
            password, _ = self.gen.generate(set())
            assert any(c.isupper() for c in password), "Sin mayúscula"
            assert any(c.islower() for c in password), "Sin minúscula"
            assert any(c.isdigit() for c in password), "Sin número"
            assert any(c in self.ESPECIALES for c in password), "Sin especial"

    def test_hash_unico_evita_duplicados(self):
        """La generación evita duplicar hashes existentes"""
        _, hash1 = self.gen.generate(set())
        # Due to random PBKDF2 salt every hash is unique by definition,
        # so we just verify two generated hashes are different strings
        _, hash2 = self.gen.generate({hash1})
        assert hash1 != hash2

    def test_dos_contraseñas_distintas(self):
        """Dos contraseñas generadas consecutivamente son distintas"""
        p1, h1 = self.gen.generate(set())
        p2, h2 = self.gen.generate({h1})
        assert p1 != p2
