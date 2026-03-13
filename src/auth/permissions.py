"""Gestión de permisos de usuario"""

from enum import Enum
from typing import Dict, List


class TipoPermiso(Enum):
    """Tipos de permisos disponibles"""
    VER = "ver"
    CREAR = "crear"
    MODIFICAR = "modificar"
    BORRAR = "borrar"
    ADMINISTRAR = "administrar"


class GestorPermisos:
    """Gestiona permisos de usuarios"""
    
    PERMISOS_ADMIN = [
        TipoPermiso.VER,
        TipoPermiso.CREAR,
        TipoPermiso.MODIFICAR,
        TipoPermiso.BORRAR,
        TipoPermiso.ADMINISTRAR,
    ]
    
    PERMISOS_USUARIO = [
        TipoPermiso.VER,
        TipoPermiso.CREAR,
    ]
    
    def __init__(self, es_admin: bool = True):
        """
        Inicializa gestor de permisos
        
        Args:
            es_admin: Si el usuario es administrador
        """
        self.es_admin = es_admin
        self.permisos = self.PERMISOS_ADMIN if es_admin else self.PERMISOS_USUARIO
    
    def tiene_permiso(self, permiso: TipoPermiso) -> bool:
        """Verifica si tiene permiso"""
        return permiso in self.permisos
    
    def verificar_permiso_o_error(self, permiso: TipoPermiso) -> bool:
        """Verifica permiso y retorna resultado"""
        return self.tiene_permiso(permiso)
    
    def obtener_permisos(self) -> List[str]:
        """Obtiene lista de permisos como strings"""
        return [p.value for p in self.permisos]
    
    @staticmethod
    def permisos_para_admin() -> List[TipoPermiso]:
        """Retorna permisos de administrador"""
        return GestorPermisos.PERMISOS_ADMIN
    
    @staticmethod
    def permisos_para_usuario() -> List[TipoPermiso]:
        """Retorna permisos de usuario normal"""
        return GestorPermisos.PERMISOS_USUARIO