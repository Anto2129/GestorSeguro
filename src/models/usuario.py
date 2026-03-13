"""Modelo de datos para Usuario"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Usuario:
    """Representa un usuario del sistema"""
    nombre: str
    contraseña_hash: str
    fecha_creacion: str
    uso: str
    estado: str  # "Activo" o "Inactivo"
    dispositivo: str
    fecha_modificacion: str = ""
    notas: str = ""
    
    @classmethod
    def from_excel_row(cls, row: tuple) -> 'Usuario':
        """Crea Usuario desde fila de Excel"""
        return cls(
            nombre=row[0],
            contraseña_hash=row[1],
            fecha_creacion=row[2],
            uso=row[3],
            estado=row[4],
            dispositivo=row[5],
            fecha_modificacion=row[6] if len(row) > 6 else "",
            notas=row[7] if len(row) > 7 else ""
        )
    
    def to_excel_row(self) -> tuple:
        """Convierte Usuario a fila de Excel"""
        return (
            self.nombre,
            self.contraseña_hash,
            self.fecha_creacion,
            self.uso,
            self.estado,
            self.dispositivo,
            self.fecha_modificacion,
            self.notas
        )