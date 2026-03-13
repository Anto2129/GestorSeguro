"""Generador de contraseñas seguras"""
import secrets
import string
from typing import Set, Tuple


class GeneradorContraseña:
    """Genera contraseñas seguras que cumplen la política del sistema"""

    CARACTERES_ESPECIALES = "@#.$%&*!?-_+="
    MIN_LONGITUD = 12
    MAX_LONGITUD = 28

    def __init__(self, politica=None):
        """
        Inicializa el generador.

        Args:
            politica: Objeto PasswordPolicy o Configuracion con parámetros de política.
                      Si es None se usan los valores por defecto.
        """
        if politica is not None:
            self.min_longitud = getattr(
                politica, 'MIN_LENGTH_AUTO',
                getattr(politica, 'MIN_LONGITUD_CONTRASEÑA_AUTO', self.MIN_LONGITUD)
            )
            self.max_longitud = getattr(
                politica, 'MAX_LENGTH',
                getattr(politica, 'MAX_LONGITUD_CONTRASEÑA', self.MAX_LONGITUD)
            )
            self.especiales = getattr(
                politica, 'SPECIAL_CHARS',
                getattr(politica, 'CARACTERES_ESPECIALES', self.CARACTERES_ESPECIALES)
            )
        else:
            self.min_longitud = self.MIN_LONGITUD
            self.max_longitud = self.MAX_LONGITUD
            self.especiales = self.CARACTERES_ESPECIALES

        self.minusculas = string.ascii_lowercase
        self.mayusculas = string.ascii_uppercase
        self.numeros = string.digits
        self.todos = self.minusculas + self.mayusculas + self.numeros + self.especiales

    # ------------------------------------------------------------------
    # API principal
    # ------------------------------------------------------------------

    def generar(self, hashes_existentes: Set[str] = None) -> Tuple[str, str]:
        """
        Genera una contraseña única y su hash SHA-256.

        Args:
            hashes_existentes: Conjunto de hashes ya usados para evitar duplicados.

        Returns:
            Tupla (contraseña_en_texto_plano, hash_sha256)
        """
        if hashes_existentes is None:
            hashes_existentes = set()

        while True:
            contraseña = self._construir_contraseña()
            hash_contraseña = self._crear_hash(contraseña)

            if hash_contraseña not in hashes_existentes:
                return contraseña, hash_contraseña

    # Alias en inglés para compatibilidad con código existente (menu.py)
    def generate(self, existing_hashes: Set[str] = None) -> Tuple[str, str]:
        """Alias en inglés de :meth:`generar`."""
        return self.generar(existing_hashes)

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------

    def _construir_contraseña(self) -> str:
        """
        Construye una contraseña cumpliendo los requisitos mínimos:
        al menos 1 mayúscula, 1 minúscula, 1 número y 1 carácter especial.
        """
        longitud = secrets.randbelow(
            self.max_longitud - self.min_longitud + 1
        ) + self.min_longitud

        # Garantizar al menos un carácter de cada tipo requerido
        obligatorios = [
            secrets.choice(self.mayusculas),
            secrets.choice(self.minusculas),
            secrets.choice(self.numeros),
            secrets.choice(self.especiales),
        ]

        # Rellenar el resto con caracteres aleatorios del pool completo
        resto = [secrets.choice(self.todos) for _ in range(longitud - len(obligatorios))]

        # Mezclar para que los obligatorios no estén siempre al inicio
        todos_chars = obligatorios + resto
        # Fisher-Yates con secrets para máxima seguridad
        for i in range(len(todos_chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            todos_chars[i], todos_chars[j] = todos_chars[j], todos_chars[i]

        return ''.join(todos_chars)

    def _validar_contraseña(self, contraseña: str) -> bool:
        """Valida que la contraseña cumple todos los requisitos."""
        cumple_longitud = self.min_longitud <= len(contraseña) <= self.max_longitud
        tiene_mayuscula = any(c.isupper() for c in contraseña)
        tiene_minuscula = any(c.islower() for c in contraseña)
        tiene_numero = any(c.isdigit() for c in contraseña)
        tiene_especial = any(c in self.especiales for c in contraseña)

        return all([
            cumple_longitud,
            tiene_mayuscula,
            tiene_minuscula,
            tiene_numero,
            tiene_especial,
        ])

    @staticmethod
    def _crear_hash(contraseña: str) -> str:
        """Crea triple hash de la contraseña usando SistemaSeguridad."""
        from core.security import SistemaSeguridad
        return SistemaSeguridad.crear_hash_contraseña(contraseña)


# Alias en inglés para compatibilidad con menu.py que importa PasswordGenerator
PasswordGenerator = GeneradorContraseña
