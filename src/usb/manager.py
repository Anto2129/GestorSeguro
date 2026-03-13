"""Gestión de carpetas en USB"""

import os
import platform
from typing import Optional


class GestorUSB:
    """Gestiona rutas y carpetas en la USB"""
    
    CARPETA_TRABAJO = ".GestorSeguro"
    
    @staticmethod
    def configurar_carpeta_trabajo(ruta_usb: str) -> Optional[str]:
        """
        Crea y configura carpeta de trabajo en USB
        
        Args:
            ruta_usb: Ruta base de la USB
            
        Returns:
            Ruta de carpeta de trabajo o None si hay error
        """
        carpeta = os.path.join(ruta_usb, GestorUSB.CARPETA_TRABAJO)
        
        if not os.path.exists(carpeta):
            try:
                os.makedirs(carpeta)
                GestorUSB._ocultar_carpeta(carpeta)
                return carpeta
            except Exception as e:
                print(f"Error creando carpeta: {e}")
                return None
        
        return carpeta
    
    @staticmethod
    def _ocultar_carpeta(ruta: str) -> None:
        """Oculta carpeta según SO"""
        if os.name == 'nt':  # Windows
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(ruta, 2)
            except:
                pass
        # En Linux/macOS el punto inicial oculta la carpeta
    
    @staticmethod
    def obtener_ruta_archivo(carpeta_trabajo: str, nombre_archivo: str) -> str:
        """Obtiene ruta completa del archivo"""
        return os.path.join(carpeta_trabajo, nombre_archivo)
    
    @staticmethod
    def verificar_espacio_disponible(ruta_usb: str) -> int:
        """
        Verifica espacio disponible en USB
        
        Returns:
            Espacio disponible en bytes
        """
        try:
            import shutil
            stat = shutil.disk_usage(ruta_usb)
            return stat.free
        except:
            return 0
    
    @staticmethod
    def listar_archivos_trabajo(carpeta_trabajo: str) -> list:
        """Lista archivos en carpeta de trabajo"""
        try:
            return os.listdir(carpeta_trabajo)
        except:
            return []
