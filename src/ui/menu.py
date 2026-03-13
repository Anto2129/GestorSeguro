"""Menú principal y submenús de la aplicación"""
import getpass
from pathlib import Path
from config.settings import AppConfig
from usb.manager import GestorUSB
from core.security import SistemaSeguridad
from storage.excel_manager import GestorExcel
from storage.vault_manager import GestorBoveda
from storage.audit_logger import RegistradorAuditoria
from storage.backup_manager import GestorBackup
from generators.usuario_generator import GeneradorUsuario
from generators.password_generator import GeneradorContraseña
from models.usuario import Usuario
from ui.colors import Colores
from ui.display import Pantalla
from utils.clipboard import PortapapelesUtils
from utils.network import RedUtils
from utils.validators import Validadores
from utils.date_utils import FechaUtils


class MenuPrincipal:
    """Gestiona menús y flujos de la aplicación"""
    
    def __init__(self, config: AppConfig, usb_manager: GestorUSB):
        self.config = config
        self.usb_manager = usb_manager
        
        # Inicializar managers
        self.security = SistemaSeguridad(config.archivo_clave)
        self.excel_manager = GestorExcel(config)
        self.vault_manager = GestorBoveda(config, self.security)
        self.audit_logger = RegistradorAuditoria(config)
        self.backup_manager = GestorBackup(config)
        self.usuario_gen = GeneradorUsuario()
        self.password_gen = GeneradorContraseña(config.password_policy)
        
        self.running = True
    
    def run(self):
        """Loop principal"""
        while self.running:
            self._show_main_menu()
            option = input(f"{Colores.AMARILLO}Opción (1-7): {Colores.RESET}").strip()
            self._handle_main_menu(option)
    
    def _show_main_menu(self):
        """Muestra menú principal"""
        print(f"\n{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}")
        print(f"{Colores.CYAN}{Colores.NEGRITA}GESTOR SEGURO DE CONTRASEÑAS USB{Colores.RESET}".center(70))
        print(f"{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}")
        print(f"\n{Colores.AMARILLO}1.{Colores.RESET} Crear usuario automático")
        print(f"{Colores.AMARILLO}2.{Colores.RESET} Crear usuario personalizado")
        print(f"{Colores.AMARILLO}3.{Colores.RESET} Ver y gestionar usuarios")
        print(f"{Colores.AMARILLO}4.{Colores.RESET} Dashboard - Estadísticas")
        print(f"{Colores.AMARILLO}5.{Colores.RESET} Búsqueda Avanzada")
        print(f"{Colores.AMARILLO}6.{Colores.RESET} {Colores.ROJO}BÓVEDA DE CONTRASEÑAS{Colores.RESET}")
        print(f"{Colores.AMARILLO}7.{Colores.RESET} Salir")
        print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
    
    def _handle_main_menu(self, option: str):
        """Maneja opciones del menú principal"""
        if option == '1':
            self._create_auto_user()
        elif option == '2':
            self._create_custom_user()
        elif option == '3':
            self._manage_users_menu()
        elif option == '4':
            self._show_dashboard()
        elif option == '5':
            self._advanced_search()
        elif option == '6':
            self._show_vault()
        elif option == '7':
            self.running = False
            print(f"\n{Colores.MAGENTA}👋 ¡Hasta luego!{Colores.RESET}\n")
    
    # ==================== CREAR USUARIOS ====================
    
    def _create_auto_user(self):
        """Crear usuario automático"""
        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}CREAR USUARIO AUTOMÁTICO{Colores.RESET}".center(70))
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
        
        existing_users = self.excel_manager.get_existing_usernames()
        existing_hashes = self.excel_manager.get_existing_password_hashes()
        
        print(f"\n{Colores.AZUL}⏳ Generando usuario...{Colores.RESET}")
        username = self.usuario_gen.generate(existing_users)
        print(f"{Colores.VERDE}✓ Usuario: {username}{Colores.RESET}")
        
        print(f"\n{Colores.AZUL}⏳ Generando contraseña...{Colores.RESET}")
        password, password_hash = self.password_gen.generate(existing_hashes)
        print(f"{Colores.VERDE}✓ Generada{Colores.RESET}")
        
        uso = input(f"\n{Colores.AMARILLO}Utilidad: {Colores.RESET}").strip()
        if not uso:
            uso = "Sin especificar"
        
        if self._save_user(username, password, password_hash, uso):
            print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
            print(f"{Colores.BLANCO}Usuario: {Colores.CYAN}{username}{Colores.RESET}")
            print(f"{Colores.BLANCO}Contraseña: {Colores.CYAN}{password}{Colores.RESET}")
            print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
            
            if PortapapelesUtils.copy_to_clipboard(password):
                print(f"{Colores.VERDE}✓ Copiada al portapapeles{Colores.RESET}")
    
    def _create_custom_user(self):
        """Crear usuario personalizado"""
        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}CREAR USUARIO PERSONALIZADO{Colores.RESET}".center(70))
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
        
        # Nombre de usuario
        while True:
            username = input(f"\n{Colores.AMARILLO}Nombre (mín. 5 caracteres): {Colores.RESET}").strip()
            valid, msg = Validadores.validate_username(username)
            
            if not valid:
                print(f"{Colores.ROJO}✗ {msg}{Colores.RESET}")
            else:
                print(f"{Colores.VERDE}✓ Válido{Colores.RESET}")
                break
        
        # Contraseña
        print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
        print(f"{Colores.AMARILLO}1.{Colores.RESET} Generar automáticamente")
        print(f"{Colores.AMARILLO}2.{Colores.RESET} Ingresar manualmente")
        pass_option = input(f"\n{Colores.AMARILLO}Opción: {Colores.RESET}").strip()
        
        existing_hashes = self.excel_manager.get_existing_password_hashes()
        
        if pass_option == '1':
            password, password_hash = self.password_gen.generate(existing_hashes)
            print(f"{Colores.VERDE}✓ Generada (requisitos estrictos){Colores.RESET}")
        else:
            while True:
                password = getpass.getpass(f"{Colores.AMARILLO}Contraseña: {Colores.RESET}")
                valid, details = Validadores.validate_password_manual(password, self.config.password_policy)
                
                if not valid:
                    print(f"{Colores.ROJO}✗ Requisitos incumplidos:{Colores.RESET}")
                    for req, ok in details.items():
                        status = f"{Colores.VERDE}✓{Colores.RESET}" if ok else f"{Colores.ROJO}✗{Colores.RESET}"
                        print(f"  {status} {req}")
                else:
                    print(f"{Colores.VERDE}✓ Válida{Colores.RESET}")
                    break
            
            password_hash = self.security.create_hash_password(password)
        
        # Uso y notas
        uso = input(f"\n{Colores.AMARILLO}Utilidad: {Colores.RESET}").strip()
        if not uso:
            uso = "Sin especificar"
        
        notas = input(f"{Colores.AMARILLO}Notas (opcional): {Colores.RESET}").strip()
        
        if self._save_user(username, password, password_hash, uso, notas):
            print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
            print(f"{Colores.BLANCO}Usuario: {Colores.CYAN}{username}{Colores.RESET}")
            print(f"{Colores.BLANCO}Contraseña: {Colores.CYAN}{password}{Colores.RESET}")
            print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
    
    def _save_user(
        self,
        username: str,
        password: str,
        password_hash: str,
        uso: str,
        notas: str = ""
    ) -> bool:
        """Guarda usuario en Excel y bóveda"""
        print(f"\n{Colores.AZUL}⏳ Guardando...{Colores.RESET}")
        
        fecha = FechaUtils.get_current_datetime_formatted()
        dispositivo = RedUtils.get_device_info()
        
        # Guardar en Excel
        usuario = Usuario(
            nombre=username,
            contraseña_hash=password_hash,
            fecha_creacion=fecha,
            uso=uso,
            estado="Activo",
            dispositivo=dispositivo,
            fecha_modificacion="",
            notas=notas
        )
        
        if not self.excel_manager.add_user(usuario):
            print(f"{Colores.ROJO}✗ Error en Excel{Colores.RESET}")
            return False
        
        print(f"{Colores.VERDE}   ✓ Usuario guardado en Excel{Colores.RESET}")
        
        # Guardar en bóveda
        if not self.vault_manager.save_password(username, password):
            print(f"{Colores.ROJO}✗ Error en bóveda{Colores.RESET}")
            return False
        
        # Backup
        self.backup_manager.create_backup()
        
        # Auditoría
        self.audit_logger.log_action(
            "CREAR_USUARIO",
            username,
            f"Uso: {uso}"
        )
        
        print(f"{Colores.VERDE}✓ Guardado completamente{Colores.RESET}")
        return True
    
    # ==================== GESTIONAR USUARIOS ====================
    
    def _manage_users_menu(self):
        """Menú de gestión de usuarios"""
        while True:
            print(f"\n{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}")
            print(f"{Colores.CYAN}{Colores.NEGRITA}GESTIÓN DE USUARIOS{Colores.RESET}".center(70))
            print(f"{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}")
            print(f"\n{Colores.AMARILLO}1.{Colores.RESET} Ver todos los usuarios")
            print(f"{Colores.AMARILLO}2.{Colores.RESET} Modificar estado")
            print(f"{Colores.AMARILLO}3.{Colores.RESET} {Colores.ROJO}Borrar usuario{Colores.RESET}")
            print(f"{Colores.AMARILLO}0.{Colores.RESET} Volver")
            print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
            
            option = input(f"{Colores.AMARILLO}Opción (0-3): {Colores.RESET}").strip()
            
            if option == '1':
                users = self.excel_manager.get_all_users()
                Pantalla.show_users_table(users)
            elif option == '2':
                self._modify_user_status()
            elif option == '3':
                self._delete_user()
            elif option == '0':
                break
    
    def _modify_user_status(self):
        """Modificar estado de usuario"""
        username = input(f"\n{Colores.AMARILLO}Usuario: {Colores.RESET}").strip()
        
        users = self.excel_manager.get_all_users()
        user = next((u for u in users if u.nombre == username), None)
        
        if not user:
            print(f"{Colores.ROJO}✗ No encontrado{Colores.RESET}")
            return
        
        print(f"\n{Colores.BLANCO}Estado actual: {Colores.VERDE if user.estado == 'Activo' else Colores.ROJO}{user.estado}{Colores.RESET}")
        print(f"{Colores.AMARILLO}1.{Colores.RESET} Activo")
        print(f"{Colores.AMARILLO}2.{Colores.RESET} Inactivo")
        
        option = input(f"\n{Colores.AMARILLO}Opción: {Colores.RESET}").strip()
        new_status = "Activo" if option == "1" else "Inactivo" if option == "2" else None
        
        if new_status and self.excel_manager.update_user_status(username, new_status):
            self.backup_manager.create_backup()
            self.audit_logger.log_action("CAMBIAR_ESTADO", username, f"Nuevo estado: {new_status}")
            print(f"{Colores.VERDE}✓ Modificado{Colores.RESET}")
    
    def _delete_user(self):
        """Borrar usuario"""
        print(f"\n{Colores.ROJO}{Colores.NEGRITA}⚠️  OPERACIÓN PELIGROSA{Colores.RESET}")
        username = input(f"\n{Colores.AMARILLO}Usuario: {Colores.RESET}").strip()
        
        users = self.excel_manager.get_all_users()
        if not any(u.nombre == username for u in users):
            print(f"{Colores.ROJO}✗ No encontrado{Colores.RESET}")
            return
        
        confirm = input(f"{Colores.ROJO}Escribe 'SÍ' para confirmar: {Colores.RESET}").strip().upper()
        
        if confirm == "SÍ":
            if self.excel_manager.delete_user(username):
                self.backup_manager.create_backup()
                self.audit_logger.log_action("BORRAR_USUARIO", username, "Eliminado")
                print(f"{Colores.VERDE}✓ Borrado{Colores.RESET}")
    
    # ==================== DASHBOARD Y BÚSQUEDA ====================
    
    def _show_dashboard(self):
        """Mostrar estadísticas"""
        users = self.excel_manager.get_all_users()
        Pantalla.show_dashboard(users)
    
    def _advanced_search(self):
        """Búsqueda avanzada"""
        print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
        print(f"{Colores.AMARILLO}Filtros disponibles:{Colores.RESET}")
        print(f"{Colores.AMARILLO}1.{Colores.RESET} Por nombre")
        print(f"{Colores.AMARILLO}2.{Colores.RESET} Por estado")
        print(f"{Colores.AMARILLO}0.{Colores.RESET} Cancelar")
        
        option = input(f"\n{Colores.AMARILLO}Opción: {Colores.RESET}").strip()
        
        users = self.excel_manager.get_all_users()
        
        if option == '1':
            name = input(f"{Colores.AMARILLO}Nombre: {Colores.RESET}").strip().lower()
            results = [u for u in users if name in u.nombre.lower()]
        elif option == '2':
            status = input(f"{Colores.AMARILLO}Estado (Activo/Inactivo): {Colores.RESET}").strip()
            results = [u for u in users if u.estado == status]
        else:
            return
        
        Pantalla.show_users_table(results)
    
    # ==================== BÓVEDA ====================
    
    def _show_vault(self):
        """Acceso a bóveda de contraseñas"""
        while True:
            print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}")
            print(f"{Colores.MAGENTA}{Colores.NEGRITA}BÓVEDA - ACCESO RESTRINGIDO{Colores.RESET}".center(100))
            print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}\n")
            
            print(f"{Colores.ROJO}{Colores.NEGRITA}⚠️  ESTÁS VIENDO CONTRASEÑAS EN TEXTO PLANO{Colores.RESET}\n")
            print(f"{Colores.AMARILLO}1.{Colores.RESET} Ver TODOS los usuarios y contraseñas")
            print(f"{Colores.AMARILLO}2.{Colores.RESET} Buscar usuario específico")
            print(f"{Colores.AMARILLO}3.{Colores.RESET} Copiar contraseña al portapapeles")
            print(f"{Colores.AMARILLO}0.{Colores.RESET} Volver")
            
            option = input(f"\n{Colores.AMARILLO}Opción: {Colores.RESET}").strip()
            
            if option == '1':
                # Ver todos
                vault_data = self.vault_manager.get_all_passwords()
                Pantalla.show_vault_table(vault_data)
                input(f"{Colores.AMARILLO}Presiona Enter para continuar...{Colores.RESET}")
            
            elif option == '2':
                username = input(f"{Colores.AMARILLO}Usuario: {Colores.RESET}").strip()
                password = self.vault_manager.get_password(username)
                
                if password:
                    Pantalla.show_password_details(username, password)
                else:
                    print(f"{Colores.ROJO}✗ No encontrado{Colores.RESET}")
            
            elif option == '3':
                username = input(f"{Colores.AMARILLO}Usuario: {Colores.RESET}").strip()
                password = self.vault_manager.get_password(username)
                
                if password and PortapapelesUtils.copy_to_clipboard(password):
                    print(f"{Colores.VERDE}✓ Copiada{Colores.RESET}")
                else:
                    print(f"{Colores.ROJO}✗ Error{Colores.RESET}")
            
            elif option == '0':
                break