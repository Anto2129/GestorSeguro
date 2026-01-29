@echo off
REM Script para crear estructura v7.0
REM Uso: Doble click en este archivo

echo Creando estructura de proyecto v7.0...

REM Crear carpetas
mkdir src\core
mkdir src\usb
mkdir src\storage
mkdir src\auth
mkdir src\ui
mkdir src\generators
mkdir src\models
mkdir src\utils
mkdir src\config
mkdir tests
mkdir docs
mkdir examples

REM Crear archivos __init__.py (vacíos)
type nul > src\__init__.py
type nul > src\core\__init__.py
type nul > src\usb\__init__.py
type nul > src\storage\__init__.py
type nul > src\auth\__init__.py
type nul > src\ui\__init__.py
type nul > src\generators\__init__.py
type nul > src\models\__init__.py
type nul > src\utils\__init__.py
type nul > src\config\__init__.py
type nul > tests\__init__.py

REM Crear módulos Python (vacíos)
type nul > src\main.py

REM core/
type nul > src\core\security.py
type nul > src\core\hardware_binding.py
type nul > src\core\steganography.py
type nul > src\core\disk_protection.py

REM usb/
type nul > src\usb\detector.py
type nul > src\usb\manager.py

REM storage/
type nul > src\storage\excel_manager.py
type nul > src\storage\vault_manager.py
type nul > src\storage\audit_logger.py
type nul > src\storage\backup_manager.py

REM auth/
type nul > src\auth\login.py
type nul > src\auth\permissions.py

REM ui/
type nul > src\ui\colors.py
type nul > src\ui\menu.py
type nul > src\ui\display.py

REM generators/
type nul > src\generators\usuario_generator.py
type nul > src\generators\password_generator.py

REM models/
type nul > src\models\usuario.py
type nul > src\models\auditoria.py
type nul > src\models\contraseña.py

REM utils/
type nul > src\utils\network.py
type nul > src\utils\clipboard.py
type nul > src\utils\validators.py
type nul > src\utils\date_utils.py

REM config/
type nul > src\config\settings.py

REM tests/
type nul > tests\test_security.py
type nul > tests\test_hardware_binding.py
type nul > tests\test_steganography.py
type nul > tests\test_generators.py
type nul > tests\test_storage.py
type nul > tests\test_usb.py
type nul > tests\conftest.py

REM docs/
type nul > docs\INSTALLATION.md
type nul > docs\USER_GUIDE.md
type nul > docs\DEVELOPER_GUIDE.md
type nul > docs\API.md

REM examples/
type nul > examples\ejemplo_basico.py
type nul > examples\ejemplo_avanzado.py

REM Crear archivos importantes
(
echo cryptography==41.0.0
echo openpyxl==3.10.10
echo pyperclip==1.8.2
echo Pillow==10.0.0
echo argon2-cffi==23.1.0
echo pytest==7.4.0
echo pytest-cov==4.1.0
) > requirements.txt

(
echo # Gestor Seguro de Contraseñas USB - v7.0
echo.
echo Sistema modular de gestión de contraseñas
) > README.md

REM Crear .gitignore
(
echo # Python
echo __pycache__/
echo *.py[cod]
echo .venv/
echo.
echo # IDE
echo .vscode/
echo .idea/
echo.
echo # Datos sensibles
echo .contraseñas_encriptadas.json
echo .config_sistema.json
) > .gitignore

echo.
echo ════════════════════════════════════════
echo ESTRUCTURA CREADA EXITOSAMENTE
echo ════════════════════════════════════════
echo.
pause
