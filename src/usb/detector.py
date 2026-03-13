"""Detección de dispositivos USB"""

import os
import platform
import subprocess
from typing import Optional


class DetectorUSB:
    """Detecta automáticamente dispositivos USB conectados"""
    
    @staticmethod
    def detectar_usb() -> Optional[str]:
        """
        Detecta la primera USB conectada según el sistema operativo
        
        Returns:
            Ruta de la USB o None si no se detecta
        """
        sistema = platform.system()
        
        if sistema == "Windows":
            return DetectorUSB._detectar_windows()
        elif sistema == "Linux":
            return DetectorUSB._detectar_linux()
        elif sistema == "Darwin":
            return DetectorUSB._detectar_macos()
        
        return None
    
    @staticmethod
    def _detectar_windows() -> Optional[str]:
        """Detección en Windows"""
        import string
        
        for letra in string.ascii_uppercase:
            unidad = f"{letra}:\\"
            if os.path.exists(unidad) and letra != 'C':
                try:
                    if DetectorUSB._es_removible_windows(unidad):
                        return unidad
                except:
                    pass
        return None
    
    @staticmethod
    def _es_removible_windows(unidad: str) -> bool:
        """Verifica si una unidad es removible en Windows"""
        try:
            import ctypes
            tipo = ctypes.windll.kernel32.GetDriveTypeW(unidad)
            return tipo == 2  # DRIVE_REMOVABLE
        except:
            return False
    
    @staticmethod
    def _detectar_linux() -> Optional[str]:
        """Detección en Linux"""
        try:
            result = subprocess.run(
                ['lsblk', '-d', '-o', 'NAME,HOTPLUG'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for linea in result.stdout.split('\n'):
                if '1' in linea:
                    dispositivo = linea.split()
                    return DetectorUSB._buscar_punto_montaje_linux(dispositivo)
        except:
            pass
        
        return None
    
    @staticmethod
    def _buscar_punto_montaje_linux(dispositivo: str) -> Optional[str]:
        """Busca punto de montaje de dispositivo en Linux"""
        for punto in ['/media', '/mnt']:
            if os.path.exists(punto):
                for carpeta in os.listdir(punto):
                    ruta = os.path.join(punto, carpeta)
                    try:
                        if os.path.ismount(ruta):
                            return ruta
                    except:
                        pass
        return None
    
    @staticmethod
    def _detectar_macos() -> Optional[str]:
        """Detección en macOS"""
        try:
            volumenes = os.listdir('/Volumes')
            for vol in volumenes:
                ruta = f'/Volumes/{vol}'
                if os.path.ismount(ruta) and vol != 'Macintosh HD':
                    return ruta
        except:
            pass
        
        return None