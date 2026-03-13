import pytest
import os
import json
import hashlib
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.hardware_binding import GestorHWID

class TestGestorHWID:

    @patch('platform.system')
    @patch('subprocess.run')
    def test_hwid_windows(self, mock_run, mock_system):
        mock_system.return_value = "Windows"
        
        # Simular respuesta de wmic
        mock_result = MagicMock()
        mock_result.stdout = "VolumeSerialNumber\r\nABCD-1234\r\n"
        mock_run.return_value = mock_result
        
        hwid = GestorHWID.get_hwid("E:\\")
        
        assert hwid == "ABCD-1234"
        mock_run.assert_called_with(["wmic", "logicaldisk", "where", "name='E:'", "get", "VolumeSerialNumber"], capture_output=True, text=True, timeout=5)

    @patch('platform.system')
    @patch('subprocess.run')
    def test_hwid_windows_fallback(self, mock_run, mock_system):
        mock_system.return_value = "Windows"
        
        # Mock de wmic que falla
        mock_result1 = MagicMock()
        mock_result1.stdout = ""
        
        # Mock de vol que funciona
        mock_result2 = MagicMock()
        mock_result2.stdout = " El volumen de la unidad E es USB\n El número de serie del volumen es: 1234-ABCD\n"
        
        mock_run.side_effect = [mock_result1, mock_result2]
        
        hwid = GestorHWID.get_hwid("E:\\")
        
        assert hwid == "1234-ABCD"

    @patch('platform.system')
    @patch('subprocess.run')
    def test_hwid_linux(self, mock_run, mock_system):
        mock_system.return_value = "Linux"
        
        mock_result = MagicMock()
        mock_result.stdout = "123e4567-e89b-12d3-a456-426614174000\n"
        mock_run.return_value = mock_result
        
        hwid = GestorHWID.get_hwid("/media/usb")
        
        assert hwid == "123e4567-e89b-12d3-a456-426614174000"
        mock_run.assert_called_with(["findmnt", "-n", "-o", "UUID", "/media/usb"], capture_output=True, text=True, timeout=5)

    @patch('platform.system')
    @patch('subprocess.run')
    def test_hwid_macos(self, mock_run, mock_system):
        mock_system.return_value = "Darwin"
        
        mock_result = MagicMock()
        mock_result.stdout = "   Volume UUID: 12345678-1234-1234-1234-123456789ABC\n"
        mock_run.return_value = mock_result
        
        hwid = GestorHWID.get_hwid("/Volumes/USB")
        
        assert hwid == "12345678-1234-1234-1234-123456789ABC"
        mock_run.assert_called_with(["diskutil", "info", "/Volumes/USB"], capture_output=True, text=True, timeout=5)

    @patch('core.hardware_binding.GestorHWID.get_hwid')
    def test_get_hwid_hash(self, mock_get_hwid):
        mock_get_hwid.return_value = "fake-usb-id"
        hash_esperado = hashlib.sha512(b"fake-usb-id").hexdigest()
        
        res = GestorHWID.get_hwid_hash("E:\\")
        
        assert res == hash_esperado
        mock_get_hwid.assert_called_once_with("E:\\")

    @patch('core.hardware_binding.GestorHWID.get_hwid')
    def test_registrar_dispositivo(self, mock_get_hwid, tmp_path):
        mock_get_hwid.return_value = "fake-usb-id"
        ruta_config = str(tmp_path / ".config_sistema.json")
        
        # Registrar por primera vez
        res = GestorHWID.registrar_dispositivo(ruta_config, "E:\\", "USB-Test")
        
        assert res is True
        assert os.path.exists(ruta_config)
        
        with open(ruta_config, "r") as f:
            data = json.load(f)
            
        hash_esperado = hashlib.sha512(b"fake-usb-id").hexdigest()
        assert data[GestorHWID._KEY_PRIMER_DISPOSITIVO] == hash_esperado
        assert hash_esperado in data[GestorHWID._KEY_DISPOSITIVOS]
        assert data[GestorHWID._KEY_DISPOSITIVOS][hash_esperado]["nombre"] == "USB-Test"
        assert data[GestorHWID._KEY_DISPOSITIVOS][hash_esperado]["maestro"] is True

    @patch('core.hardware_binding.GestorHWID.get_hwid')
    def test_verificar_dispositivo(self, mock_get_hwid, tmp_path):
        mock_get_hwid.return_value = "fake-usb-id"
        ruta_config = str(tmp_path / ".config_sistema.json")
        
        # Al no existir el archivo, debería retornar True (primer acceso)
        res = GestorHWID.verificar_dispositivo(ruta_config, "E:\\")
        assert res is True
        
        # Registrar y verificar
        GestorHWID.registrar_dispositivo(ruta_config, "E:\\", "USB-Test")
        res = GestorHWID.verificar_dispositivo(ruta_config, "E:\\")
        assert res is True
        
        # Probar con otro ID
        mock_get_hwid.return_value = "otro-usb-id"
        res = GestorHWID.verificar_dispositivo(ruta_config, "E:\\")
        assert res is False
