"""Script to verify all imports work correctly"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_all_imports():
    """Test that all modules can be imported"""
    try:
        print("Testing imports...\n")
        
        # Config
        from src.config.settings import Configuracion
        print("✓ src.config.settings")
        
        # Core
        from src.core.security import SistemaSeguridad
        print("✓ src.core.security")
        
        # USB
        from src.usb.detector import DetectorUSB
        from src.usb.manager import GestorUSB
        print("✓ src.usb.detector")
        print("✓ src.usb.manager")
        
        # Storage
        from src.storage.excel_manager import GestorExcel
        from src.storage.vault_manager import GestorBoveda
        from src.storage.audit_logger import RegistradorAuditoria
        from src.storage.backup_manager import GestorBackup
        print("✓ src.storage.excel_manager")
        print("✓ src.storage.vault_manager")
        print("✓ src.storage.audit_logger")
        print("✓ src.storage.backup_manager")
        
        # Auth
        from src.auth.login import SistemaLogin
        from src.auth.permissions import GestorPermisos
        print("✓ src.auth.login")
        print("✓ src.auth.permissions")
        
        # UI
        from src.ui.colors import Colores
        from src.ui.menu import MenuPrincipal
        from src.ui.display import Pantalla
        print("✓ src.ui.colors")
        print("✓ src.ui.menu")
        print("✓ src.ui.display")
        
        # Generators
        from src.generators.usuario_generator import GeneradorUsuario
        from src.generators.password_generator import GeneradorContraseña
        print("✓ src.generators.usuario_generator")
        print("✓ src.generators.password_generator")
        
        # Models
        from src.models.usuario import Usuario
        from src.models.contraseña import Contraseña
        from src.models.auditoria import Auditoria
        print("✓ src.models.usuario")
        print("✓ src.models.contraseña")
        print("✓ src.models.auditoria")
        
        # Utils
        from src.utils.network import RedUtils
        from src.utils.clipboard import PortapapelesUtils
        from src.utils.validators import Validadores
        from src.utils.date_utils import FechaUtils
        print("✓ src.utils.network")
        print("✓ src.utils.clipboard")
        print("✓ src.utils.validators")
        print("✓ src.utils.date_utils")
        
        print("\n✓ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n✗ Import Error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        return False


if __name__ == "__main__":
    success = test_all_imports()
    exit(0 if success else 1)