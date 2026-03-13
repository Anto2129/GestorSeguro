"""Pruebas para módulos de storage"""

import pytest
from pathlib import Path
from src.config.settings import Configuracion
from src.storage.backup_manager import GestorBackup
from src.storage.vault_manager import GestorBoveda
from src.core.security import SistemaSeguridad


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config(tmp_path):
    """Configuración apuntando a directorio temporal"""
    cfg = Configuracion()
    cfg.establecer_carpeta_trabajo(str(tmp_path))
    return cfg


@pytest.fixture
def security(config):
    """Instancia de SistemaSeguridad con clave temporal"""
    return SistemaSeguridad(config.archivo_clave)


@pytest.fixture
def backup_manager(config):
    return GestorBackup(config)


@pytest.fixture
def vault_manager(config, security):
    return GestorBoveda(config, security)


# ---------------------------------------------------------------------------
# GestorBackup
# ---------------------------------------------------------------------------

class TestGestorBackup:

    def test_backup_false_sin_archivo_origen(self, backup_manager):
        """Si no existe el archivo Excel origen, create_backup devuelve False"""
        result = backup_manager.create_backup()
        assert result is False

    def test_backup_exists_false_inicial(self, backup_manager):
        """Sin backup previo, backup_exists devuelve False"""
        assert backup_manager.backup_exists() is False

    def test_backup_y_restauracion(self, backup_manager, config):
        """Crea archivo origen, hace backup y lo restaura"""
        # Crear archivo origen mínimo
        config.archivo_log.write_text("datos")

        assert backup_manager.create_backup() is True
        assert backup_manager.backup_exists() is True

        # Borrar original y restaurar
        config.archivo_log.unlink()
        assert backup_manager.restore_backup() is True
        assert config.archivo_log.exists()


# ---------------------------------------------------------------------------
# GestorBoveda
# ---------------------------------------------------------------------------

class TestGestorBoveda:

    def test_usuario_inexistente_devuelve_none(self, vault_manager):
        """Obtener contraseña de usuario inexistente devuelve None"""
        result = vault_manager.get_password("usuario_fantasma")
        assert result is None

    def test_guardar_y_recuperar_contraseña(self, vault_manager):
        """Guarda una contraseña y la recupera correctamente"""
        ok = vault_manager.save_password("testuser", "MiContraseña1@")
        assert ok is True

        recovered = vault_manager.get_password("testuser")
        assert recovered == "MiContraseña1@"

    def test_usuario_existe_en_boveda(self, vault_manager):
        """user_exists_in_vault devuelve True tras guardar"""
        vault_manager.save_password("existente", "Pass1@segura")
        assert vault_manager.user_exists_in_vault("existente") is True
        assert vault_manager.user_exists_in_vault("fantasma") is False

    def test_obtener_todas_las_contraseñas(self, vault_manager):
        """get_all_passwords devuelve todas las entradas guardadas"""
        vault_manager.save_password("user1", "Pass1@segura")
        vault_manager.save_password("user2", "Pass2@segura")

        all_pwd = vault_manager.get_all_passwords()
        assert "user1" in all_pwd
        assert "user2" in all_pwd
        # get_all_passwords now returns {'password': ..., 'fecha_creacion': ...}
        assert all_pwd["user1"]["password"] == "Pass1@segura"
        assert all_pwd["user2"]["password"] == "Pass2@segura"
