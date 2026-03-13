"""Códigos ANSI para colores en terminal"""


class Colores:
    """Definición de colores para terminal"""
    
    # Colores básicos
    RESET = '\033[0m'
    NEGRO = '\033[30m'
    ROJO = '\033[91m'
    VERDE = '\033[92m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BLANCO = '\033[97m'
    GRIS = '\033[90m'
    
    # Estilos
    NEGRITA = '\033[1m'
    SUBRAYADO = '\033[4m'
    INVERTIDO = '\033[7m'
    
    # Fondos
    FONDO_ROJO = '\033[41m'
    FONDO_VERDE = '\033[42m'
    FONDO_AZUL = '\033[44m'
    
    @staticmethod
    def limpiar_pantalla():
        """Limpia pantalla de terminal"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def separador(longitud: int = 70, caracter: str = '=') -> str:
        """Genera separador decorativo"""
        return caracter * longitud
    
    @staticmethod
    def titulo(texto: str, longitud: int = 70) -> str:
        """Genera título formateado"""
        return f"{Colores.CYAN}{Colores.NEGRITA}{Colores.separador(longitud)}{Colores.RESET}\n{Colores.CYAN}{Colores.NEGRITA}{texto.center(longitud)}{Colores.RESET}\n{Colores.CYAN}{Colores.NEGRITA}{Colores.separador(longitud)}{Colores.RESET}"
