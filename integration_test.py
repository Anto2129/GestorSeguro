"""
Script de integración: verifica todo el sistema con el USB real conectado.
Uso: .venv\\Scripts\\python.exe integration_test.py
"""
import sys
from pathlib import Path

# Añadir src/ al path para los imports internos
sys.path.insert(0, str(Path(__file__).parent / "src"))

def separador(titulo):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print('='*60)

def ok(msg): print(f"  ✓ {msg}")
def fail(msg): print(f"  ✗ {msg}")

errores = []

# ──────────────────────────────────────────────
# 1. Detección USB
# ──────────────────────────────────────────────
separador("1. Detección USB")
try:
    from usb.detector import DetectorUSB
    ruta_usb = DetectorUSB.detectar_usb()
    if ruta_usb:
        ok(f"USB detectada: {ruta_usb}")
    else:
        fail("No se detectó USB")
        errores.append("USB no detectada")
except Exception as e:
    fail(f"Error al detectar USB: {e}")
    errores.append(str(e))
    ruta_usb = None

# ──────────────────────────────────────────────
# 2. Carpeta de trabajo
# ──────────────────────────────────────────────
separador("2. Carpeta de trabajo en USB")
carpeta_trabajo = None
if ruta_usb:
    try:
        from usb.manager import GestorUSB
        carpeta_trabajo = GestorUSB.configurar_carpeta_trabajo(ruta_usb)
        if carpeta_trabajo:
            ok(f"Carpeta: {carpeta_trabajo}")
        else:
            fail("No se pudo crear carpeta de trabajo")
            errores.append("Carpeta de trabajo no creada")
    except Exception as e:
        fail(f"Error: {e}")
        errores.append(str(e))

# ──────────────────────────────────────────────
# 3. Configuración
# ──────────────────────────────────────────────
separador("3. Configuración del sistema")
config = None
if carpeta_trabajo:
    try:
        from config.settings import Configuracion
        config = Configuracion(carpeta_trabajo)
        ok(f"Configuración inicializada")
        ok(f"archivo_log     → {config.archivo_log}")
        ok(f"archivo_clave   → {config.archivo_clave}")
        ok(f"archivo_config  → {config.archivo_config}")
    except Exception as e:
        fail(f"Error: {e}")
        errores.append(str(e))

# ──────────────────────────────────────────────
# 4. Seguridad – clave de encriptación
# ──────────────────────────────────────────────
separador("4. Sistema de seguridad (encriptación)")
security = None
if config:
    try:
        from core.security import SistemaSeguridad
        security = SistemaSeguridad(config.archivo_clave)
        # Generar/obtener clave
        clave = security.obtener_clave_encriptacion()
        ok(f"Clave de encriptación lista ({len(clave)} bytes)")
        # Test encrypt/decrypt
        texto = "ContraseñaTest123@"
        enc = security.encriptar_contraseña(texto)
        dec = security.desencriptar_contraseña(enc)
        assert dec == texto, "Desencriptado no coincide"
        ok("Encrypt → Decrypt: OK")
        # Test hash
        h = SistemaSeguridad.crear_hash_contraseña(texto)
        ok(f"Hash SHA-256: {h[:16]}…")
    except Exception as e:
        fail(f"Error: {e}")
        errores.append(str(e))

# ──────────────────────────────────────────────
# 5. Bóveda de contraseñas
# ──────────────────────────────────────────────
separador("5. Bóveda de contraseñas")
if config and security:
    try:
        from storage.vault_manager import GestorBoveda
        boveda = GestorBoveda(config, security)
        ok("GestorBoveda creado")
        # Guardar contraseña de prueba
        guardado = boveda.save_password("__integration_test__", "TestPass1@")
        if guardado:
            ok("Contraseña de test guardada en bóveda")
        else:
            fail("Error guardando en bóveda")
            errores.append("Bóveda: save_password falló")
        # Recuperar
        recuperada = boveda.get_password("__integration_test__")
        if recuperada == "TestPass1@":
            ok("Contraseña recuperada correctamente")
        else:
            fail(f"Contraseña incorrecta: {recuperada}")
            errores.append("Bóveda: get_password devolvió valor incorrecto")
    except Exception as e:
        fail(f"Error: {e}")
        errores.append(str(e))

# ──────────────────────────────────────────────
# 6. Generadores
# ──────────────────────────────────────────────
separador("6. Generadores de usuario y contraseña")
try:
    from generators.usuario_generator import GeneradorUsuario
    from generators.password_generator import GeneradorContraseña
    from config.settings import PasswordPolicy

    gen_user = GeneradorUsuario()
    usuario = gen_user.generate(set())
    ok(f"Usuario generado: {usuario} ({len(usuario)} chars)")

    gen_pass = GeneradorContraseña(PasswordPolicy())
    password, phash = gen_pass.generate(set())
    ok(f"Contraseña generada: {password} ({len(password)} chars)")
    ok(f"Hash: {phash[:16]}…")
except Exception as e:
    fail(f"Error: {e}")
    errores.append(str(e))

# ──────────────────────────────────────────────
# 7. Excel manager (estructura)
# ──────────────────────────────────────────────
separador("7. Gestor Excel")
if config:
    try:
        from storage.excel_manager import GestorExcel
        excel = GestorExcel(config)
        ok("GestorExcel creado y archivo verificado/creado")
        usuarios = excel.get_all_users()
        ok(f"Usuarios en Excel: {len(usuarios)}")
    except Exception as e:
        fail(f"Error: {e}")
        errores.append(str(e))

# ──────────────────────────────────────────────
# 8. Backup
# ──────────────────────────────────────────────
separador("8. Gestor de Backup")
if config:
    try:
        from storage.backup_manager import GestorBackup
        backup = GestorBackup(config)
        resultado = backup.create_backup()
        ok(f"Backup ejecutado: {'OK' if resultado else 'Sin archivo origen aún'}")
    except Exception as e:
        fail(f"Error: {e}")
        errores.append(str(e))

# ──────────────────────────────────────────────
# 9. Validadores
# ──────────────────────────────────────────────
separador("9. Validadores")
try:
    from utils.validators import Validadores
    from config.settings import PasswordPolicy

    policy = PasswordPolicy()
    ok_user, msg = Validadores.validate_username("TestUser")
    ok(f"validate_username('TestUser') → {ok_user}")
    ok_pass, details = Validadores.validate_password_manual("Password1@", policy)
    ok(f"validate_password_manual → {ok_pass}")
except Exception as e:
    fail(f"Error: {e}")
    errores.append(str(e))

# ──────────────────────────────────────────────
# Resumen final
# ──────────────────────────────────────────────
separador("RESUMEN FINAL")
if errores:
    fail(f"{len(errores)} error(s) encontrado(s):")
    for e in errores:
        print(f"    → {e}")
    sys.exit(1)
else:
    print(f"\n  ✓ ¡Todos los módulos funcionan correctamente con la USB real!")
    print(f"  ✓ USB: {ruta_usb}")
    print(f"  ✓ Carpeta: {carpeta_trabajo}")
    print()
    sys.exit(0)
