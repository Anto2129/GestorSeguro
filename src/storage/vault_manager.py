"""Gestión de bóveda de contraseñas encriptadas"""
import json
from pathlib import Path
from typing import Optional, Dict
from config.settings import AppConfig
from core.security import SecurityManager
from models.contraseña import Contraseña
from ui.colors import Colores


class GestorBoveda:
    """Gestiona la bóveda de contraseñas encriptadas"""
    
    def __init__(self, config: AppConfig, security: SecurityManager):
        self.config = config
        self.security = security
    
    def save_password(self, username: str, password: str) -> bool:
        """Guarda contraseña encriptada"""
        try:
            print(f"\n{Colores.AZUL}   Encriptando contraseña...{Colores.RESET}")
            
            # Leer existentes
            vault = self._load_vault()
            
            # Encriptar
            encrypted = self.security.encrypt_password(password)
            if encrypted is None:
                return False
            
            # Agregar
            from utils.date_utils import FechaUtils
            vault[username] = {
                'contraseña': encrypted,
                'fecha_creacion': FechaUtils.get_current_datetime_formatted()
            }
            
            # Guardar
            print(f"{Colores.AZUL}   Guardando en bóveda...{Colores.RESET}")
            self.config.archivo_contraseñas.write_text(
                json.dumps(vault, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            
            # Validar
            print(f"{Colores.AZUL}   Validando integridad...{Colores.RESET}")
            vault_check = self._load_vault()
            
            if username in vault_check:
                test_password = self.security.decrypt_password(
                    vault_check[username]['contraseña']
                )
                
                if test_password == password:
                    print(f"{Colores.VERDE}      ✓ Validación OK{Colores.RESET}")
                    return True
        
        except Exception as e:
            print(f"{Colores.ROJO}   ❌ Error: {e}{Colores.RESET}")
        
        return False
    
    def get_password(self, username: str) -> Optional[str]:
        """Obtiene contraseña desencriptada"""
        try:
            vault = self._load_vault()
            
            if username not in vault:
                return None
            
            encrypted = vault[username]['contraseña']
            return self.security.decrypt_password(encrypted)
        
        except Exception as e:
            print(f"{Colores.ROJO}Error: {e}{Colores.RESET}")
            return None
    
    def get_all_passwords(self) -> Dict[str, dict]:
        """
        Obtiene todas las contraseñas desencriptadas con sus metadatos.

        Returns:
            Dict { username: {'password': str, 'fecha_creacion': str} }
        """
        result = {}
        vault = self._load_vault()

        for username, data in vault.items():
            password = self.security.decrypt_password(data['contraseña'])
            if password:
                result[username] = {
                    'password':       password,
                    'fecha_creacion': data.get('fecha_creacion', '-')
                }

        return result
    
    def user_exists_in_vault(self, username: str) -> bool:
        """Verifica si usuario existe en bóveda"""
        vault = self._load_vault()
        return username in vault
    
    def _load_vault(self) -> Dict:
        """Carga bóveda desde archivo"""
        if not self.config.archivo_contraseñas.exists():
            return {}
        
        try:
            content = self.config.archivo_contraseñas.read_text(encoding='utf-8')
            if content.strip():
                return json.loads(content)
        except Exception:
            pass
        
        return {}