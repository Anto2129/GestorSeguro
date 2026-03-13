"""Gestión de backups"""
import shutil
from pathlib import Path
from config.settings import AppConfig
from ui.colors import Colores


class GestorBackup:
    """Gestiona backups automáticos"""
    
    def __init__(self, config: AppConfig):
        self.config = config
    
    def create_backup(self) -> bool:
        """Crea backup del archivo Excel"""
        try:
            if self.config.archivo_log.exists():
                shutil.copy2(
                    self.config.archivo_log,
                    self.config.archivo_backup
                )
                
                # Ocultar en Windows
                if self._should_hide_file():
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(
                        str(self.config.archivo_backup), 2
                    )
                
                return True
        except Exception as e:
            print(f"{Colores.ROJO}Error en backup: {e}{Colores.RESET}")
        
        return False
    
    def restore_backup(self) -> bool:
        """Restaura desde backup"""
        try:
            if self.config.archivo_backup.exists():
                shutil.copy2(
                    self.config.archivo_backup,
                    self.config.archivo_log
                )
                return True
        except Exception as e:
            print(f"{Colores.ROJO}Error restaurando: {e}{Colores.RESET}")
        
        return False
    
    def backup_exists(self) -> bool:
        """Verifica si backup existe"""
        return self.config.archivo_backup.exists()
    
    @staticmethod
    def _should_hide_file() -> bool:
        """Verifica si se debe ocultar archivo"""
        import os
        return os.name == 'nt'
