"""
Gestor Seguro de Contraseñas USB - v7.0
Entry point of the application
"""

import sys
from pathlib import Path

# Añadir src al path para importaciones relativas
sys.path.insert(0, str(Path(__file__).parent))

# Import core modules
from config.settings import Configuracion, AppConfig
from ui.menu import MenuPrincipal
from ui.colors import Colores
from usb.detector import DetectorUSB
from usb.manager import GestorUSB
from auth.login import SistemaLogin
from core.hardware_binding import GestorHWID


def inicializar_aplicacion() -> tuple:
    """Inicializa la aplicación y retorna config y gestor USB"""
    print(f"\n{Colores.CYAN}{Colores.NEGRITA}🔐 Iniciando Gestor USB...{Colores.RESET}")

    # 1. Detectar USB
    ruta_usb = DetectorUSB.detectar_usb()

    if not ruta_usb:
        print(f"{Colores.ROJO}✗ No se detectó llave USB{Colores.RESET}")
        print(f"{Colores.AMARILLO}Conecta una llave USB y reinicia{Colores.RESET}\n")
        sys.exit(1)

    print(f"{Colores.VERDE}✓ USB detectada: {ruta_usb}{Colores.RESET}")

    # 2. Configurar carpeta de trabajo en la USB
    usb_manager = GestorUSB()
    carpeta_trabajo = usb_manager.configurar_carpeta_trabajo(ruta_usb)

    if not carpeta_trabajo:
        print(f"{Colores.ROJO}✗ Error creando carpeta de trabajo en USB{Colores.RESET}")
        sys.exit(1)

    # 3. Crear configuración con la carpeta de trabajo
    config = Configuracion(carpeta_trabajo)
    config.establecer_ruta_usb(ruta_usb)

    # 4. HWID – Verificar / Registrar dispositivo
    ruta_config = config.obtener_ruta('config')
    _verificar_hwid(ruta_config, ruta_usb)

    print(f"{Colores.VERDE}✓ Aplicación inicializada{Colores.RESET}\n")

    return config, usb_manager


def _verificar_hwid(ruta_config: str, ruta_usb: str) -> None:
    """Verifica el HWID de la USB actual. Registra si es la primera vez."""
    print(f"{Colores.AZUL}🔍 Verificando dispositivo...{Colores.RESET}")

    autorizado = GestorHWID.verificar_dispositivo(ruta_config, ruta_usb)

    if not autorizado:
        print(f"\n{Colores.ROJO}{Colores.NEGRITA}{'█'*60}{Colores.RESET}")
        print(f"{Colores.ROJO}{Colores.NEGRITA}  DISPOSITIVO NO AUTORIZADO{Colores.RESET}".center(60))
        print(f"{Colores.ROJO}{Colores.NEGRITA}{'█'*60}{Colores.RESET}")
        print(f"\n{Colores.AMARILLO}Este equipo no está registrado como dispositivo autorizado.")
        print(f"Contacta con el administrador del sistema.{Colores.RESET}\n")
        sys.exit(1)

    # Si no hay ningún dispositivo registrado aún → registrar este
    dispositivos = GestorHWID.listar_dispositivos(ruta_config)
    if not dispositivos:
        print(f"{Colores.AMARILLO}  → Primer acceso: registrando este dispositivo...{Colores.RESET}")
        ok = GestorHWID.registrar_dispositivo(ruta_config, ruta_usb)
        if ok:
            hwid_hash = GestorHWID.get_hwid_hash(ruta_usb)
            print(f"{Colores.VERDE}  ✓ Dispositivo maestro registrado{Colores.RESET}")
            print(f"{Colores.GRIS}    HWID: {hwid_hash[:32]}...{Colores.RESET}")
        else:
            print(f"{Colores.AMARILLO}  ⚠ No se pudo registrar el dispositivo{Colores.RESET}")
    else:
        print(f"{Colores.VERDE}  ✓ Dispositivo autorizado{Colores.RESET}")


def main():
    """Función principal que orquesta el flujo de la aplicación"""
    try:
        # Inicializar
        config, usb_manager = inicializar_aplicacion()

        # Autenticar
        ruta_config = config.obtener_ruta('config')
        login = SistemaLogin(ruta_config)
        if not login.autenticar():
            print(f"{Colores.ROJO}✗ Acceso denegado{Colores.RESET}\n")
            sys.exit(1)

        # Crear gestor de menús y ejecutar loop principal
        menu = MenuPrincipal(config, usb_manager)
        menu.run()

    except KeyboardInterrupt:
        print(f"\n{Colores.MAGENTA}👋 ¡Hasta luego!{Colores.RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"{Colores.ROJO}❌ Error inesperado: {e}{Colores.RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()