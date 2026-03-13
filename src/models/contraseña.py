"""Modelo de datos para Contraseña encriptada"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Contraseña:
    """Representa una contraseña encriptada en la bóveda"""
    usuario: str
    contraseña_encriptada: str
    fecha_creacion: str
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para JSON"""
        return {
            'contraseña': self.contraseña_encriptada,
            'fecha_creacion': self.fecha_creacion
        }
    
    @classmethod
    def from_dict(cls, usuario: str, data: dict) -> 'Contraseña':
        """Crea desde diccionario JSON"""
        return cls(
            usuario=usuario,
            contraseña_encriptada=data['contraseña'],
            fecha_creacion=data['fecha_creacion']
        )
