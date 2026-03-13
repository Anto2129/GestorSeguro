"""Configuración de pytest"""

import sys
import pytest
import os
from pathlib import Path

# Añadir src/ al path para que los imports internos de los módulos funcionen
# (e.g. `from config.settings import ...` dentro de backup_manager.py)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def temp_usb_dir(tmp_path):
    """Crea directorio temporal para simular USB"""
    usb_dir = tmp_path / ".GestorSeguro"
    usb_dir.mkdir()
    return str(usb_dir)


@pytest.fixture
def configuracion(temp_usb_dir):
    """Crea configuración con directorio temporal"""
    from src.config.settings import Configuracion

    config = Configuracion()
    config.establecer_carpeta_trabajo(temp_usb_dir)
    return config