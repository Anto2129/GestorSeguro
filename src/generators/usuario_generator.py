"""Generador de nombres de usuario"""
import random
import string
from typing import Set


class GeneradorUsuario:
    """Genera nombres de usuario aleatorios"""
    
    def __init__(self):
        self.minusculas = string.ascii_lowercase
        self.mayusculas = string.ascii_uppercase
        self.numeros = string.digits
    
    def generate(self, existing_users: Set[str]) -> str:
        """Genera nombre de usuario único"""
        while True:
            length = random.randint(5, 10)
            username = self._build_username(length)
            
            if self._validate_username(username) and username not in existing_users:
                return username
    
    def _build_username(self, length: int) -> str:
        """Construye nombre de usuario"""
        username = []
        
        for i in range(length):
            if i % 2 == 0:
                char_set = random.choice([self.minusculas, self.mayusculas])
            else:
                char_set = random.choice(
                    [self.minusculas, self.mayusculas, self.numeros]
                )
            
            username.append(random.choice(char_set))
        
        return ''.join(username)
    
    def _validate_username(self, username: str) -> bool:
        """Valida nombre de usuario"""
        has_upper = any(c.isupper() for c in username)
        has_lower = any(c.islower() for c in username)
        is_alphanumeric = username.isalnum()
        
        return has_upper and has_lower and is_alphanumeric