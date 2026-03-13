"""Modelo de datos para Auditoría"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Auditoria:
    """Representa un registro de auditoría"""
    timestamp: str
    accion: str  # "CREAR_USUARIO", "CAMBIAR_ESTADO", "BORRAR_USUARIO", etc.
    usuario_afectado: str
    usuario_sistema: str
    dispositivo: str
    detalles: str = ""
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para JSON"""
        return {
            'timestamp': self.timestamp,
            'accion': self.accion,
            'usuario_afectado': self.usuario_afectado,
            'usuario_sistema': self.usuario_sistema,
            'dispositivo': self.dispositivo,
            'detalles': self.detalles
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Auditoria':
        """Crea desde diccionario JSON"""
        return cls(
            timestamp=data['timestamp'],
            accion=data['accion'],
            usuario_afectado=data['usuario_afectado'],
            usuario_sistema=data['usuario_sistema'],
            dispositivo=data['dispositivo'],
            detalles=data.get('detalles', '')
        )