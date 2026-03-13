"""Mostrar datos de forma formateada"""
from typing import List
from models.usuario import Usuario
from ui.colors import Colores


class Pantalla:
    """Gestiona la presentación de datos"""
    
    @staticmethod
    def show_dashboard(users: List[Usuario]):
        """Muestra dashboard de estadísticas"""
        if not users:
            print(f"\n{Colores.AMARILLO}No hay datos{Colores.RESET}")
            return
        
        total = len(users)
        activos = sum(1 for u in users if u.estado == 'Activo')
        inactivos = sum(1 for u in users if u.estado == 'Inactivo')
        
        dispositivos = set(u.dispositivo for u in users)
        usos = set(u.uso for u in users if u.uso)
        
        print(f"\n{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}")
        print(f"{Colores.CYAN}{Colores.NEGRITA}DASHBOARD - ESTADÍSTICAS{Colores.RESET}".center(70))
        print(f"{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}\n")
        
        print(f"{Colores.BLANCO}📊 {Colores.NEGRITA}RESUMEN:{Colores.RESET}")
        print(f"   {Colores.VERDE}✓ Total: {Colores.CYAN}{total}{Colores.RESET}")
        print(f"   {Colores.VERDE}✓ Activos: {Colores.CYAN}{activos}{Colores.RESET}")
        print(f"   {Colores.VERDE}✓ Inactivos: {Colores.CYAN}{inactivos}{Colores.RESET}")
        
        porcentaje = (activos / total * 100) if total > 0 else 0
        print(f"   {Colores.BLANCO}📈 Tasa: {Colores.VERDE}{porcentaje:.1f}%{Colores.RESET}\n")
        
        print(f"{Colores.BLANCO}🖥️  {Colores.NEGRITA}DISPOSITIVOS:{Colores.RESET}")
        print(f"   {Colores.VERDE}✓ Únicos: {Colores.CYAN}{len(dispositivos)}{Colores.RESET}\n")
        
        print(f"{Colores.BLANCO}🏷️  {Colores.NEGRITA}USOS:{Colores.RESET}")
        print(f"   {Colores.VERDE}✓ Únicos: {Colores.CYAN}{len(usos)}{Colores.RESET}\n")
        
        print(f"{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}\n")
    
    @staticmethod
    def show_users_table(users: List[Usuario]):
        """Muestra tabla de usuarios"""
        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*120}{Colores.RESET}")
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}LOG DE USUARIOS{Colores.RESET}".center(120))
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*120}{Colores.RESET}\n")
        
        if not users:
            print(f"{Colores.AMARILLO}Sin registros{Colores.RESET}")
        else:
            header = f"{Colores.CYAN}{'USUARIO':<15} | {'FECHA':<20} | {'ESTADO':<12} | {'USO':<20} | {'DISPOSITIVO':<30}{Colores.RESET}"
            print(header)
            print(f"{Colores.CYAN}{'-'*110}{Colores.RESET}")
            
            for user in users:
                estado_color = (
                    f"{Colores.VERDE}{user.estado}{Colores.RESET}"
                    if user.estado == 'Activo'
                    else f"{Colores.ROJO}{user.estado}{Colores.RESET}"
                )
                
                print(
                    f"{user.nombre:<15} | {user.fecha_creacion:<20} | "
                    f"{estado_color:<32} | {user.uso:<20} | {user.dispositivo:<30}"
                )
            
            print(f"\n{Colores.CYAN}{'-'*110}{Colores.RESET}")
            print(f"{Colores.VERDE}Total: {len(users)}{Colores.RESET}")
        
        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*120}{Colores.RESET}")
    
    @staticmethod
    def show_password_details(username: str, password: str):
        """Muestra detalles de contraseña"""
        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}")
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}CONTRASEÑA ENCONTRADA{Colores.RESET}".center(100))
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}\n")
        
        print(f"{Colores.BLANCO}Usuario:    {Colores.CYAN}{username}{Colores.RESET}")
        print(f"{Colores.BLANCO}Contraseña: {Colores.CYAN}{password}{Colores.RESET}")
        
        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}\n")

    @staticmethod
    def show_vault_table(vault_data: dict):
        """Muestra tabla completa de usuarios y contraseñas de la bóveda"""
        ancho = 110
        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*ancho}{Colores.RESET}")
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}BÓVEDA COMPLETA - CONTRASEÑAS EN TEXTO PLANO{Colores.RESET}".center(ancho))
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*ancho}{Colores.RESET}\n")

        if not vault_data:
            print(f"  {Colores.AMARILLO}No hay contraseñas guardadas en la bóveda.{Colores.RESET}")
            print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*ancho}{Colores.RESET}\n")
            return

        print(f"  {Colores.ROJO}{Colores.NEGRITA}⚠  INFORMACIÓN SENSIBLE - NO DEJES LA PANTALLA DESATENDIDA{Colores.RESET}\n")

        # Cabecera
        col_u, col_p, col_f = 22, 50, 22
        cabecera = (
            f"  {Colores.CYAN}{Colores.NEGRITA}"
            f"{'USUARIO':<{col_u}} {'CONTRASEÑA':<{col_p}} {'FECHA CREACIÓN':<{col_f}}"
            f"{Colores.RESET}"
        )
        separador = f"  {Colores.CYAN}{'-'*(col_u + col_p + col_f + 2)}{Colores.RESET}"
        print(cabecera)
        print(separador)

        for i, (usuario, datos) in enumerate(sorted(vault_data.items()), 1):
            password = datos.get('password', '[ERROR]')
            fecha    = datos.get('fecha_creacion', '-')
            color    = Colores.BLANCO if i % 2 == 0 else Colores.GRIS
            print(
                f"  {color}{i:<3} {usuario:<{col_u-4}} "
                f"{Colores.VERDE}{password:<{col_p}}{color} "
                f"{fecha:<{col_f}}{Colores.RESET}"
            )

        print(separador)
        print(f"  {Colores.MAGENTA}Total: {len(vault_data)} entrada(s){Colores.RESET}")
        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*ancho}{Colores.RESET}\n")