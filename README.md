# Gestor Seguro de Contraseñas USB - v7.0

Sistema modular de gestión de contraseñas


# Este es el codigo completo utilizado sin fragmentar
import random
import string
from datetime import datetime
import os
import socket
import getpass
import shutil
import hashlib
import pyperclip
import json
from cryptography.fernet import Fernet
import subprocess
import platform

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.formatting.rule import CellIsRule
    OPENPYXL_DISPONIBLE = True
except ImportError:
    OPENPYXL_DISPONIBLE = False

try:
    from cryptography.fernet import Fernet
    ENCRIPTACION_DISPONIBLE = True
except ImportError:
    ENCRIPTACION_DISPONIBLE = False

# ==================== CÓDIGOS DE COLOR ANSI ====================

class Colores:
    """Clase para definir colores en terminal"""
    RESET = '\033[0m'
    CYAN = '\033[96m'
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    GRIS = '\033[90m'
    BLANCO = '\033[97m'
    
    NEGRITA = '\033[1m'
    SUBRAYADO = '\033[4m'

# Definir caracteres para generación aleatoria
CARACTERES_ESPECIALES = "@#.$%&*!?-_+="
MINUSCULAS = string.ascii_lowercase
MAYUSCULAS = string.ascii_uppercase
NUMEROS = string.digits

# ==================== GESTIÓN DE RUTAS EN LLAVE USB ====================

class GestorUSB:
    """Maneja la detección y configuración de la llave USB"""
    
    @staticmethod
    def detectar_llave_usb():
        """Detecta automáticamente la llave USB conectada"""
        sistema = platform.system()
        
        if sistema == "Windows":
            return GestorUSB._detectar_usb_windows()
        elif sistema == "Linux":
            return GestorUSB._detectar_usb_linux()
        elif sistema == "Darwin":  # macOS
            return GestorUSB._detectar_usb_macos()
        else:
            return None
    
    @staticmethod
    def _detectar_usb_windows():
        """Detecta USB en Windows"""
        import string
        drives = []
        for letra in string.ascii_uppercase:
            unidad = f"{letra}:\\"
            if os.path.exists(unidad):
                try:
                    # Verificar que no sea unidad del sistema
                    if letra != 'C':
                        drives.append(unidad)
                except:
                    pass
        return drives[0] if drives else None
    
    @staticmethod
    def _detectar_usb_linux():
        """Detecta USB en Linux"""
        try:
            result = subprocess.run(['lsblk', '-d', '-o', 'NAME,HOTPLUG'],
                                    capture_output=True, text=True)
            for linea in result.stdout.split('\n'):
                if '1' in linea:
                    dispositivo = linea.split()[0]
                    for punto in ['/media', '/mnt']:
                        if os.path.exists(punto):
                            for carpeta in os.listdir(punto):
                                ruta = os.path.join(punto, carpeta)
                                if os.path.ismount(ruta):
                                    return ruta
        except:
            pass
        return None
    
    @staticmethod
    def _detectar_usb_macos():
        """Detecta USB en macOS"""
        try:
            volumenes = os.listdir('/Volumes')
            for vol in volumenes:
                ruta = f'/Volumes/{vol}'
                if os.path.ismount(ruta) and vol != 'Macintosh HD':
                    return ruta
        except:
            pass
        return None
    
    @staticmethod
    def configurar_carpeta_trabajo(ruta_usb):
        """Configura la carpeta de trabajo en la USB - COMPLETAMENTE OCULTA"""
        carpeta_trabajo = os.path.join(ruta_usb, ".GestorSeguro")
        
        if not os.path.exists(carpeta_trabajo):
            try:
                os.makedirs(carpeta_trabajo)
                print(f"{Colores.VERDE}✓ Carpeta de trabajo creada (oculta){Colores.RESET}")
                
                # Ocultar en Windows
                if os.name == 'nt':
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(carpeta_trabajo, 2)
                    print(f"{Colores.VERDE}✓ Carpeta oculta en Windows{Colores.RESET}")
                
            except Exception as e:
                print(f"{Colores.ROJO}✗ Error creando carpeta: {e}{Colores.RESET}")
                return None
        
        return carpeta_trabajo
    
    @staticmethod
    def obtener_ruta_archivo(carpeta_trabajo, nombre_archivo):
        """Obtiene la ruta completa del archivo en la USB"""
        return os.path.join(carpeta_trabajo, nombre_archivo)

# ==================== INSTANCIA GLOBAL DE RUTAS ====================

carpeta_trabajo = None

def inicializar_rutas_usb():
    """Inicializa las rutas de trabajo en la USB"""
    global carpeta_trabajo
    
    print(f"\n{Colores.AZUL}🔍 Detectando llave USB...{Colores.RESET}")
    ruta_usb = GestorUSB.detectar_llave_usb()
    
    if not ruta_usb:
        print(f"{Colores.ROJO}✗ No se detectó llave USB{Colores.RESET}")
        print(f"{Colores.AMARILLO}Conecta una llave USB y reinicia{Colores.RESET}\n")
        return False
    
    print(f"{Colores.VERDE}✓ USB detectada: {ruta_usb}{Colores.RESET}")
    
    carpeta_trabajo = GestorUSB.configurar_carpeta_trabajo(ruta_usb)
    
    if not carpeta_trabajo:
        return False
    
    print(f"{Colores.VERDE}✓ Carpeta de trabajo: {carpeta_trabajo}{Colores.RESET}\n")
    return True

def obtener_archivo(nombre):
    """Obtiene la ruta completa de un archivo"""
    if not carpeta_trabajo:
        raise Exception("Carpeta de trabajo no inicializada")
    return GestorUSB.obtener_ruta_archivo(carpeta_trabajo, nombre)

# ==================== RUTAS DE ARCHIVOS (CON ESTEGANOGRAFÍA) ====================

# ==================== RUTAS DE ARCHIVOS ====================

def actualizar_rutas():
    """Actualiza las variables de rutas globales"""
    global ARCHIVO_LOG, ARCHIVO_BACKUP, ARCHIVO_AUDITORIA, ARCHIVO_CONTRASEÑAS, ARCHIVO_CLAVE, ARCHIVO_CONFIG
    
    ARCHIVO_LOG = obtener_archivo("usuarios_log.xlsx")
    ARCHIVO_BACKUP = obtener_archivo(".usuarios_backup.xlsx")
    ARCHIVO_AUDITORIA = obtener_archivo(".auditoria_log.json")
    ARCHIVO_CONTRASEÑAS = obtener_archivo(".contraseñas_encriptadas.json")
    ARCHIVO_CLAVE = obtener_archivo(".clave_maestra.key")
    ARCHIVO_CONFIG = obtener_archivo(".config_sistema.json")



# ==================== FUNCIONES DE SEGURIDAD ====================

class SistemaSeguridad:
    """Maneja toda la seguridad del sistema"""
    
    @staticmethod
    def crear_clave_encriptacion():
        """Crea una clave de encriptación Fernet (AES-128) NUEVA cada vez"""
        print(f"\n{Colores.AMARILLO}⚠️  Detectando clave de encriptación...{Colores.RESET}")
        
        if os.path.exists(ARCHIVO_CLAVE):
            print(f"{Colores.AMARILLO}   Clave anterior detectada - BORRANDO...{Colores.RESET}")
            try:
                os.remove(ARCHIVO_CLAVE)
                print(f"{Colores.VERDE}   ✓ Clave anterior eliminada{Colores.RESET}")
            except:
                print(f"{Colores.ROJO}   ✗ No se pudo eliminar clave anterior{Colores.RESET}")
        
        # CREAR CLAVE NUEVA
        print(f"{Colores.AZUL}   Generando clave NUEVA...{Colores.RESET}")
        clave = Fernet.generate_key()
        
        with open(ARCHIVO_CLAVE, 'wb') as f:
            f.write(clave)
        
        # Ocultar en Windows - SOLO la clave
        if os.name == 'nt':
            import ctypes
            ctypes.windll.kernel32.SetFileAttributesW(ARCHIVO_CLAVE, 2)
        
        print(f"{Colores.VERDE}   ✓ Clave nueva generada y guardada{Colores.RESET}\n")
        return clave
    
    @staticmethod
    def obtener_clave():
        """Obtiene la clave existente"""
        if not os.path.exists(ARCHIVO_CLAVE):
            return SistemaSeguridad.crear_clave_encriptacion()
        
        try:
            with open(ARCHIVO_CLAVE, 'rb') as f:
                clave = f.read()
            
            # Validar que sea una clave Fernet válida
            try:
                Fernet(clave)
                return clave
            except:
                print(f"{Colores.ROJO}✗ Clave corrupta detectada - Generando nueva...{Colores.RESET}")
                os.remove(ARCHIVO_CLAVE)
                return SistemaSeguridad.crear_clave_encriptacion()
        except Exception as e:
            print(f"{Colores.ROJO}Error leyendo clave: {e}{Colores.RESET}")
            return SistemaSeguridad.crear_clave_encriptacion()
    
    @staticmethod
    def encriptar_contraseña(contraseña):
        """Encripta una contraseña usando Fernet (AES-128)"""
        if not ENCRIPTACION_DISPONIBLE:
            return contraseña
        
        try:
            clave = SistemaSeguridad.obtener_clave()
            cipher = Fernet(clave)
            contraseña_encriptada = cipher.encrypt(contraseña.encode())
            resultado = contraseña_encriptada.decode()
            
            print(f"{Colores.VERDE}      ✓ Contraseña encriptada{Colores.RESET}")
            return resultado
        except Exception as e:
            print(f"{Colores.ROJO}Error en encriptación: {e}{Colores.RESET}")
            return None
    
    @staticmethod
    def desencriptar_contraseña(contraseña_encriptada):
        """Desencripta una contraseña con VALIDACIÓN"""
        if not ENCRIPTACION_DISPONIBLE:
            return contraseña_encriptada
        
        try:
            clave = SistemaSeguridad.obtener_clave()
            cipher = Fernet(clave)
            contraseña = cipher.decrypt(contraseña_encriptada.encode())
            return contraseña.decode()
        except Exception as e:
            print(f"{Colores.ROJO}✗ Error desencriptando (clave incorrecta o datos corruptos){Colores.RESET}")
            return None
    
    @staticmethod
    def crear_hash_contraseña(contraseña):
        """Crea un hash SHA256 de la contraseña"""
        return hashlib.sha256(contraseña.encode()).hexdigest()
    
    @staticmethod
    def verificar_contraseña_maestra(contraseña):
        """Verifica la contraseña maestra del sistema"""
        if not os.path.exists(ARCHIVO_CONFIG):
            return False
        
        try:
            with open(ARCHIVO_CONFIG, 'r') as f:
                config = json.load(f)
            
            hash_almacenado = config.get('contraseña_maestra_hash')
            hash_ingresado = SistemaSeguridad.crear_hash_contraseña(contraseña)
            
            return hash_almacenado == hash_ingresado
        except:
            return False
    
    @staticmethod
    def configurar_contraseña_maestra():
        """Configura la contraseña maestra del sistema (PRIMERA VEZ)"""
        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}CONFIGURAR CONTRASEÑA MAESTRA DEL SISTEMA{Colores.RESET}".center(70))
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
        
        print(f"\n{Colores.AMARILLO}⚠️  IMPORTANTE:{Colores.RESET}")
        print(f"{Colores.BLANCO}Esta contraseña protege el acceso al GESTOR{Colores.RESET}")
        print(f"{Colores.BLANCO}Si la olvidas, NO podrá recuperarse{Colores.RESET}")
        
        while True:
            contraseña = getpass.getpass(f"\n{Colores.AMARILLO}Ingresa contraseña maestra (mín. 8 caracteres): {Colores.RESET}")
            
            if len(contraseña) < 8:
                print(f"{Colores.ROJO}✗ La contraseña debe tener mínimo 8 caracteres{Colores.RESET}")
                continue
            
            confirmacion = getpass.getpass(f"{Colores.AMARILLO}Confirma la contraseña: {Colores.RESET}")
            
            if contraseña != confirmacion:
                print(f"{Colores.ROJO}✗ Las contraseñas no coinciden{Colores.RESET}")
                continue
            
            # Guardar
            hash_contraseña = SistemaSeguridad.crear_hash_contraseña(contraseña)
            config = {
                'contraseña_maestra_hash': hash_contraseña,
                'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'version': '4.3 USB'
            }
            
            with open(ARCHIVO_CONFIG, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Ocultar archivo
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(ARCHIVO_CONFIG, 2)
            
            print(f"\n{Colores.VERDE}✓ Contraseña maestra configurada correctamente{Colores.RESET}")
            print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}\n")
            break

# ==================== FUNCIONES DE RED ====================

def obtener_ip_dispositivo():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "IP No disponible"

def obtener_usuario_sistema():
    try:
        return getpass.getuser()
    except Exception:
        return "Usuario desconocido"

def obtener_info_dispositivo():
    usuario = obtener_usuario_sistema()
    ip = obtener_ip_dispositivo()
    return f"@{usuario} | IP: {ip}"

def copiar_al_portapapeles(texto):
    try:
        pyperclip.copy(texto)
        return True
    except Exception:
        return False

# ==================== FUNCIONES DE VALIDACIÓN ====================

def verificar_archivo_existe():
    if not os.path.exists(ARCHIVO_LOG):
        if OPENPYXL_DISPONIBLE:
            crear_archivo_excel_formateado()
        else:
            print(f"{Colores.ROJO}⚠️  openpyxl no está instalado.{Colores.RESET}")
            print(f"{Colores.AMARILLO}Instala con: pip install openpyxl pyperclip cryptography{Colores.RESET}")
    else:
        print(f"{Colores.VERDE}✓ Archivo '{os.path.basename(ARCHIVO_LOG)}' encontrado.{Colores.RESET}\n")

def crear_archivo_excel_formateado():
    wb = Workbook()
    ws = wb.active
    ws.title = "Usuarios"
    
    headers = ["Nombre de usuario", "Contraseña Hash", "Fecha de creacion", "uso", "Estado", "Dispositivo", "Fecha Modificación", "Notas"]
    
    font_header = Font(name='Calibri', size=12, bold=True, color="FFFFFF")
    fill_header = PatternFill(start_color="2180a0", end_color="2180a0", fill_type="solid")
    alignment_header = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    border_thin = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = alignment_header
        cell.border = border_thin
    
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 65
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 25
    ws.column_dimensions['E'].width = 18
    ws.column_dimensions['F'].width = 30
    ws.column_dimensions['G'].width = 20
    ws.column_dimensions['H'].width = 30
    
    ws.row_dimensions[1].height = 25
    
    dv = DataValidation(type="list", formula1='"Activo,Inactivo"', allow_blank=False)
    dv.error = 'Por favor, selecciona "Activo" o "Inactivo"'
    ws.add_data_validation(dv)
    dv.add(f'E2:E1000')
    
    fill_verde = PatternFill(start_color="00B050", end_color="00B050", fill_type="solid")
    font_blanca = Font(name='Calibri', size=11, bold=True, color="FFFFFF")
    regla_activo = CellIsRule(operator='equal', formula=['"Activo"'], fill=fill_verde, font=font_blanca)
    ws.conditional_formatting.add(f'E2:E1000', regla_activo)
    
    fill_rojo = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
    regla_inactivo = CellIsRule(operator='equal', formula=['"Inactivo"'], fill=fill_rojo, font=font_blanca)
    ws.conditional_formatting.add(f'E2:E1000', regla_inactivo)
    
    wb.save(ARCHIVO_LOG)
    print(f"{Colores.VERDE}✓ Archivo '{os.path.basename(ARCHIVO_LOG)}' creado.{Colores.RESET}\n")

def obtener_usuarios_existentes():
    usuarios = set()
    if os.path.exists(ARCHIVO_LOG) and OPENPYXL_DISPONIBLE:
        try:
            from openpyxl import load_workbook
            wb = load_workbook(ARCHIVO_LOG)
            ws = wb.active
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row and row[0]:
                    usuarios.add(row[0])
        except Exception as e:
            print(f"{Colores.ROJO}Error: {e}{Colores.RESET}")
    return usuarios

def obtener_contrasenas_existentes():
    contrasenas = set()
    if os.path.exists(ARCHIVO_LOG) and OPENPYXL_DISPONIBLE:
        try:
            from openpyxl import load_workbook
            wb = load_workbook(ARCHIVO_LOG)
            ws = wb.active
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row and row[1]:
                    contrasenas.add(row[1])
        except Exception as e:
            print(f"{Colores.ROJO}Error: {e}{Colores.RESET}")
    return contrasenas

# ==================== GENERACIÓN DE USUARIO ====================

def generar_nombre_usuario(usuarios_existentes):
    while True:
        longitud = random.randint(5, 10)
        nombre = []
        
        for i in range(longitud):
            if i % 2 == 0:
                tipo = random.choice([MINUSCULAS, MAYUSCULAS])
            else:
                tipo = random.choice([MINUSCULAS, MAYUSCULAS, NUMEROS])
            
            nombre.append(random.choice(tipo))
        
        nombre_usuario = ''.join(nombre)
        
        if nombre_usuario not in usuarios_existentes:
            tiene_mayuscula = any(c.isupper() for c in nombre_usuario)
            tiene_minuscula = any(c.islower() for c in nombre_usuario)
            es_alfanumerico = nombre_usuario.isalnum()
            
            if tiene_mayuscula and tiene_minuscula and es_alfanumerico:
                return nombre_usuario

# ==================== GENERACIÓN DE CONTRASEÑA ====================

def generar_contraseña(contrasenas_hash, longitud=None, incluir_especiales=True):
    if longitud is None:
        longitud = random.randint(12, 28)
    
    while True:
        password = []
        pos_especial = random.randint(0, longitud - 1) if incluir_especiales else -1
        
        for i in range(longitud):
            if incluir_especiales and i == pos_especial:
                password.append(random.choice(CARACTERES_ESPECIALES))
            elif i % 3 == 0:
                password.append(random.choice(MINUSCULAS))
            elif i % 3 == 1:
                password.append(random.choice(MAYUSCULAS))
            else:
                password.append(random.choice(NUMEROS))
        
        random.shuffle(password)
        contraseña = ''.join(password)
        contraseña_hash = SistemaSeguridad.crear_hash_contraseña(contraseña)
        
        tiene_especial = any(c in CARACTERES_ESPECIALES for c in contraseña) if incluir_especiales else True
        tiene_mayuscula = any(c.isupper() for c in contraseña)
        tiene_minuscula = any(c.islower() for c in contraseña)
        tiene_numero = any(c.isdigit() for c in contraseña)
        es_unica = contraseña_hash not in contrasenas_hash
        longitud_valida = 12 <= len(contraseña) <= 28
        
        if (tiene_especial and tiene_mayuscula and tiene_minuscula and 
            tiene_numero and es_unica and longitud_valida):
            return contraseña, contraseña_hash

def verificar_contraseña(contraseña):
    tiene_especial = any(c in CARACTERES_ESPECIALES for c in contraseña)
    tiene_mayuscula = any(c.isupper() for c in contraseña)
    tiene_minuscula = any(c.islower() for c in contraseña)
    tiene_numero = any(c.isdigit() for c in contraseña)
    longitud_valida = 12 <= len(contraseña) <= 28
    
    detalles = {
        'Carácter especial (@#.$%&*!?-_+=)': tiene_especial,
        'Mayúscula': tiene_mayuscula,
        'Minúscula': tiene_minuscula,
        'Número': tiene_numero,
        'Longitud 12-28': longitud_valida
    }
    
    return all(detalles.values()), detalles

def verificar_contraseña_manual(contraseña):
    """Validación REDUCIDA para contraseñas manuales: 8+ caracteres alfanuméricos + 1 mayúscula + 1 especial"""
    tiene_especial = any(c in CARACTERES_ESPECIALES for c in contraseña)
    tiene_mayuscula = any(c.isupper() for c in contraseña)
    es_alfanumerico = all(c.isalnum() or c in CARACTERES_ESPECIALES for c in contraseña)
    longitud_valida = len(contraseña) >= 8
    
    detalles = {
        'Longitud mínima 8 caracteres': longitud_valida,
        'Alfanuméricos + caracteres especiales': es_alfanumerico,
        'Al menos una mayúscula': tiene_mayuscula,
        'Al menos un carácter especial': tiene_especial
    }
    
    return all(detalles.values()), detalles

# ==================== FECHA Y HORA ====================

def obtener_fecha_creacion():
    ahora = datetime.now()
    return ahora.strftime("%d/%m/%Y %H:%M:%S")

def parsear_fecha(fecha_str):
    try:
        return datetime.strptime(fecha_str, "%d/%m/%Y %H:%M:%S")
    except:
        return None

# ==================== GESTIÓN DE CONTRASEÑAS ENCRIPTADAS ====================

def guardar_contraseña_encriptada(nombre_usuario, contraseña_real):
    """Guarda la contraseña encriptada - VERSIÓN v4.3 USB (Sin bloqueos de permisos)"""
    try:
        print(f"\n{Colores.AZUL}   Encriptando contraseña...{Colores.RESET}")
        contraseñas = {}
        
        # PASO 1: LEER LAS CONTRASEÑAS EXISTENTES
        if os.path.exists(ARCHIVO_CONTRASEÑAS):
            try:
                with open(ARCHIVO_CONTRASEÑAS, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    if contenido:
                        contraseñas = json.loads(contenido)
                    else:
                        contraseñas = {}
            except Exception as e:
                print(f"{Colores.AMARILLO}   ⚠️  Archivo anterior corrupto - reiniciando{Colores.RESET}")
                contraseñas = {}
        
        # PASO 2: ENCRIPTAR LA NUEVA CONTRASEÑA
        contraseña_encriptada = SistemaSeguridad.encriptar_contraseña(contraseña_real)
        
        if contraseña_encriptada is None:
            print(f"{Colores.ROJO}   ✗ Error encriptando{Colores.RESET}")
            return False
        
        # PASO 3: AÑADIR LA NUEVA CONTRASEÑA AL DICCIONARIO
        contraseñas[nombre_usuario] = {
            'contraseña': contraseña_encriptada,
            'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # PASO 4: GUARDAR TODO EL DICCIONARIO (ANTIGUAS + NUEVA)
        print(f"{Colores.AZUL}   Guardando en bóveda...{Colores.RESET}")
        with open(ARCHIVO_CONTRASEÑAS, 'w', encoding='utf-8') as f:
            json.dump(contraseñas, f, indent=2, ensure_ascii=False)
        
        # PASO 5: NO OCULTAR EL ARCHIVO JSON - Evita bloqueos en Windows
        # Solo ocultamos la clave maestra, no los datos
        
        # PASO 6: VALIDAR QUE SE GUARDÓ CORRECTAMENTE
        print(f"{Colores.AZUL}   Validando integridad...{Colores.RESET}")
        with open(ARCHIVO_CONTRASEÑAS, 'r', encoding='utf-8') as f:
            contraseñas_validacion = json.load(f)
        
        if nombre_usuario in contraseñas_validacion:
            # PROBAR DESENCRIPTACIÓN
            contraseña_test = SistemaSeguridad.desencriptar_contraseña(
                contraseñas_validacion[nombre_usuario]['contraseña']
            )
            
            if contraseña_test == contraseña_real:
                print(f"{Colores.VERDE}      ✓ Validación OK - Bóveda con {len(contraseñas_validacion)} contraseña(s){Colores.RESET}")
                return True
            else:
                print(f"{Colores.ROJO}      ✗ Validación FALLO - Datos no coinciden{Colores.RESET}")
                return False
        else:
            print(f"{Colores.ROJO}      ✗ Usuario no guardado{Colores.RESET}")
            return False
        
    except Exception as e:
        print(f"{Colores.ROJO}   ❌ Error guardando contraseña: {e}{Colores.RESET}")
        return False

def obtener_contraseña_encriptada(nombre_usuario):
    """Obtiene la contraseña desencriptada de un usuario"""
    try:
        if not os.path.exists(ARCHIVO_CONTRASEÑAS):
            return None
        
        with open(ARCHIVO_CONTRASEÑAS, 'r', encoding='utf-8') as f:
            contraseñas = json.load(f)
        
        if nombre_usuario not in contraseñas:
            return None
        
        contraseña_encriptada = contraseñas[nombre_usuario]['contraseña']
        contraseña_real = SistemaSeguridad.desencriptar_contraseña(contraseña_encriptada)
        
        return contraseña_real
    except Exception as e:
        print(f"{Colores.ROJO}Error al obtener contraseña: {e}{Colores.RESET}")
        return None

def listar_usuarios_con_acceso_contraseña():
    """Acceso a la bóveda de contraseñas con opciones de búsqueda"""
    while True:
        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}")
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}BÓVEDA DE CONTRASEÑAS - ACCESO RESTRINGIDO{Colores.RESET}".center(100))
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}\n")
        
        if not os.path.exists(ARCHIVO_CONTRASEÑAS):
            print(f"{Colores.AMARILLO}No hay contraseñas guardadas{Colores.RESET}\n")
            break
        
        try:
            with open(ARCHIVO_CONTRASEÑAS, 'r', encoding='utf-8') as f:
                contraseñas = json.load(f)
            
            if not contraseñas:
                print(f"{Colores.AMARILLO}No hay contraseñas guardadas{Colores.RESET}\n")
                break
            
            print(f"{Colores.ROJO}{Colores.NEGRITA}⚠️  ESTÁS VIENDO CONTRASEÑAS EN TEXTO PLANO ⚠️{Colores.RESET}\n")
            print(f"{Colores.AMARILLO}Opciones:{Colores.RESET}")
            print(f"{Colores.AMARILLO}1.{Colores.RESET} Ver TODAS las contraseñas ({len(contraseñas)} total)")
            print(f"{Colores.AMARILLO}2.{Colores.RESET} Buscar usuario específico")
            print(f"{Colores.AMARILLO}3.{Colores.RESET} Copiar contraseña al portapapeles")
            print(f"{Colores.AMARILLO}0.{Colores.RESET} Volver")
            
            opcion = input(f"\n{Colores.AMARILLO}Opción (0-3): {Colores.RESET}").strip()
            
            if opcion == '1':
                # VER TODAS LAS CONTRASEÑAS
                print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}")
                print(f"{Colores.MAGENTA}{Colores.NEGRITA}TODAS LAS CONTRASEÑAS{Colores.RESET}".center(100))
                print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}\n")
                
                print(f"{Colores.CYAN}{'USUARIO':<20} | {'CONTRASEÑA':<45} | {'FECHA CREACIÓN':<20}{Colores.RESET}")
                print(f"{Colores.CYAN}{'-'*90}{Colores.RESET}")
                
                contador = 0
                for usuario, datos in sorted(contraseñas.items()):
                    try:
                        contraseña_desencriptada = SistemaSeguridad.desencriptar_contraseña(datos['contraseña'])
                        if contraseña_desencriptada:
                            print(f"{usuario:<20} | {contraseña_desencriptada:<45} | {datos['fecha_creacion']:<20}")
                            contador += 1
                        else:
                            print(f"{usuario:<20} | {Colores.ROJO}[ERROR DESENCRIPTANDO]{Colores.RESET:<45} | {datos['fecha_creacion']:<20}")
                    except Exception as e:
                        print(f"{usuario:<20} | {Colores.ROJO}[ERROR: {str(e)[:30]}]{Colores.RESET:<45} | {datos['fecha_creacion']:<20}")
                
                print(f"\n{Colores.CYAN}{'-'*90}{Colores.RESET}")
                print(f"{Colores.MAGENTA}Total mostrado: {contador}/{len(contraseñas)}{Colores.RESET}\n")
                
                input(f"{Colores.AMARILLO}Presiona Enter para continuar...{Colores.RESET}")
            
            elif opcion == '2':
                # BUSCAR USUARIO ESPECÍFICO
                print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
                usuario_busqueda = input(f"{Colores.AMARILLO}Ingresa nombre del usuario: {Colores.RESET}").strip()
                
                # Búsqueda exacta primero
                if usuario_busqueda in contraseñas:
                    datos = contraseñas[usuario_busqueda]
                    contraseña_desencriptada = SistemaSeguridad.desencriptar_contraseña(datos['contraseña'])
                    
                    if contraseña_desencriptada:
                        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}")
                        print(f"{Colores.MAGENTA}{Colores.NEGRITA}CONTRASEÑA ENCONTRADA{Colores.RESET}".center(100))
                        print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}\n")
                        
                        print(f"{Colores.BLANCO}Usuario:       {Colores.CYAN}{usuario_busqueda}{Colores.RESET}")
                        print(f"{Colores.BLANCO}Contraseña:    {Colores.CYAN}{contraseña_desencriptada}{Colores.RESET}")
                        print(f"{Colores.BLANCO}Fecha:         {Colores.CYAN}{datos['fecha_creacion']}{Colores.RESET}")
                        
                        print(f"\n{Colores.AMARILLO}¿Copiar al portapapeles?{Colores.RESET}")
                        print(f"{Colores.AMARILLO}1.{Colores.RESET} Sí")
                        print(f"{Colores.AMARILLO}2.{Colores.RESET} No")
                        
                        opcion_copiar = input(f"\n{Colores.AMARILLO}Opción (1-2): {Colores.RESET}").strip()
                        
                        if opcion_copiar == '1':
                            if copiar_al_portapapeles(contraseña_desencriptada):
                                print(f"\n{Colores.VERDE}✓ Contraseña copiada{Colores.RESET}")
                        
                        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}\n")
                    else:
                        print(f"\n{Colores.ROJO}✗ Error desencriptando - Clave posiblemente incorrecta{Colores.RESET}\n")
                else:
                    # Búsqueda aproximada
                    coincidencias = [u for u in contraseñas.keys() if usuario_busqueda.lower() in u.lower()]
                    
                    if coincidencias:
                        print(f"\n{Colores.AMARILLO}Coincidencias encontradas:{Colores.RESET}\n")
                        
                        for i, usuario in enumerate(coincidencias, 1):
                            print(f"{Colores.AMARILLO}{i}.{Colores.RESET} {usuario}")
                        
                        print(f"{Colores.AMARILLO}0.{Colores.RESET} Cancelar")
                        
                        opcion_coincidencia = input(f"\n{Colores.AMARILLO}Selecciona (0-{len(coincidencias)}): {Colores.RESET}").strip()
                        
                        try:
                            indice = int(opcion_coincidencia)
                            if indice == 0:
                                pass
                            elif 1 <= indice <= len(coincidencias):
                                usuario_seleccionado = coincidencias[indice - 1]
                                datos = contraseñas[usuario_seleccionado]
                                contraseña_desencriptada = SistemaSeguridad.desencriptar_contraseña(datos['contraseña'])
                                
                                if contraseña_desencriptada:
                                    print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}")
                                    print(f"{Colores.MAGENTA}{Colores.NEGRITA}CONTRASEÑA ENCONTRADA{Colores.RESET}".center(100))
                                    print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}\n")
                                    
                                    print(f"{Colores.BLANCO}Usuario:       {Colores.CYAN}{usuario_seleccionado}{Colores.RESET}")
                                    print(f"{Colores.BLANCO}Contraseña:    {Colores.CYAN}{contraseña_desencriptada}{Colores.RESET}")
                                    print(f"{Colores.BLANCO}Fecha:         {Colores.CYAN}{datos['fecha_creacion']}{Colores.RESET}")
                                    
                                    print(f"\n{Colores.AMARILLO}¿Copiar al portapapeles?{Colores.RESET}")
                                    print(f"{Colores.AMARILLO}1.{Colores.RESET} Sí")
                                    print(f"{Colores.AMARILLO}2.{Colores.RESET} No")
                                    
                                    opcion_copiar = input(f"\n{Colores.AMARILLO}Opción (1-2): {Colores.RESET}").strip()
                                    
                                    if opcion_copiar == '1':
                                        if copiar_al_portapapeles(contraseña_desencriptada):
                                            print(f"\n{Colores.VERDE}✓ Contraseña copiada{Colores.RESET}")
                                    
                                    print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}\n")
                        except:
                            pass
                    else:
                        print(f"\n{Colores.ROJO}✗ No se encontraron usuarios{Colores.RESET}")
            
            elif opcion == '3':
                # COPIAR DIRECTAMENTE
                print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
                usuario_copiar = input(f"{Colores.AMARILLO}Usuario: {Colores.RESET}").strip()
                
                if usuario_copiar in contraseñas:
                    datos = contraseñas[usuario_copiar]
                    contraseña_desencriptada = SistemaSeguridad.desencriptar_contraseña(datos['contraseña'])
                    
                    if contraseña_desencriptada and copiar_al_portapapeles(contraseña_desencriptada):
                        print(f"\n{Colores.VERDE}✓ Contraseña de '{usuario_copiar}' copiada{Colores.RESET}\n")
                    else:
                        print(f"\n{Colores.ROJO}✗ Error desencriptando{Colores.RESET}\n")
                else:
                    print(f"\n{Colores.ROJO}✗ Usuario no encontrado{Colores.RESET}\n")
            
            elif opcion == '0':
                break
        
        except Exception as e:
            print(f"{Colores.ROJO}Error: {e}{Colores.RESET}\n")
            break

# ==================== FUNCIONES DE AUDITORÍA Y BACKUP ====================

def registrar_auditoria(accion, usuario, detalles=""):
    try:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        usuario_sistema = obtener_usuario_sistema()
        dispositivo = obtener_ip_dispositivo()
        
        entrada_auditoria = {
            "timestamp": ahora,
            "accion": accion,
            "usuario_afectado": usuario,
            "usuario_sistema": usuario_sistema,
            "dispositivo": dispositivo,
            "detalles": detalles
        }
        
        auditoria = []
        if os.path.exists(ARCHIVO_AUDITORIA):
            with open(ARCHIVO_AUDITORIA, 'r', encoding='utf-8') as f:
                try:
                    auditoria = json.load(f)
                except:
                    auditoria = []
        
        auditoria.append(entrada_auditoria)
        
        with open(ARCHIVO_AUDITORIA, 'w', encoding='utf-8') as f:
            json.dump(auditoria, f, indent=2, ensure_ascii=False)
        
        if os.name == 'nt':
            import ctypes
            ctypes.windll.kernel32.SetFileAttributesW(ARCHIVO_AUDITORIA, 2)
    except Exception as e:
        pass

def crear_backup():
    try:
        if os.path.exists(ARCHIVO_LOG):
            shutil.copy2(ARCHIVO_LOG, ARCHIVO_BACKUP)
            
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(ARCHIVO_BACKUP, 2)
    except Exception as e:
        pass

# ==================== GUARDADO EN EXCEL ====================

def guardar_usuario(nombre, contraseña_original, contraseña_hash, uso, info_dispositivo, notas=""):
    fecha = obtener_fecha_creacion()
    
    if not OPENPYXL_DISPONIBLE:
        print(f"{Colores.ROJO}✗ openpyxl no disponible.{Colores.RESET}")
        return False, None
    
    try:
        from openpyxl import load_workbook
        from openpyxl.styles import Alignment, Border, Side
        
        wb = load_workbook(ARCHIVO_LOG)
        ws = wb.active
        siguiente_fila = ws.max_row + 1
        
        estado = "Activo"
        datos = [nombre, contraseña_hash, fecha, uso, estado, info_dispositivo, "", notas]
        
        alignment_data = Alignment(horizontal="left", vertical="center", wrap_text=True)
        alignment_estado = Alignment(horizontal="center", vertical="center", wrap_text=True)
        border_thin = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        for col_num, dato in enumerate(datos, 1):
            cell = ws.cell(row=siguiente_fila, column=col_num)
            cell.value = dato
            cell.border = border_thin
            
            if col_num == 5:
                cell.alignment = alignment_estado
            else:
                cell.alignment = alignment_data
        
        ws.row_dimensions[siguiente_fila].height = 20
        
        dv = DataValidation(type="list", formula1='"Activo,Inactivo"', allow_blank=False)
        ws.add_data_validation(dv)
        dv.add(f'E{siguiente_fila}')
        
        wb.save(ARCHIVO_LOG)
        
        print(f"{Colores.VERDE}   ✓ Usuario guardado en Excel{Colores.RESET}")
        
        # GUARDAR CONTRASEÑA ENCRIPTADA
        resultado = guardar_contraseña_encriptada(nombre, contraseña_original)
        
        if resultado:
            crear_backup()
            registrar_auditoria("CREAR_USUARIO", nombre, f"Usuario creado. Uso: {uso}")
            return True, contraseña_original
        else:
            print(f"{Colores.ROJO}   ✗ Error en bóveda - Usuario NO se guardó completamente{Colores.RESET}")
            return False, None
            
    except Exception as e:
        print(f"{Colores.ROJO}Error: {e}{Colores.RESET}")
        return False, None

# ==================== GESTIÓN DE USUARIOS ====================

def leer_todos_usuarios():
    usuarios = []
    if os.path.exists(ARCHIVO_LOG) and OPENPYXL_DISPONIBLE:
        try:
            from openpyxl import load_workbook
            wb = load_workbook(ARCHIVO_LOG)
            ws = wb.active
            
            for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                if row and row[0]:
                    usuarios.append({
                        'nombre': row[0],
                        'contraseña_hash': row[1],
                        'fecha': row[2],
                        'uso': row[3],
                        'estado': row[4],
                        'dispositivo': row[5],
                        'fecha_mod': row[6],
                        'notas': row[7] if len(row) > 7 else "",
                        'fila': row_num
                    })
        except Exception as e:
            pass
    return usuarios

def cambiar_estado_usuario(nombre_usuario, nuevo_estado):
    if not OPENPYXL_DISPONIBLE:
        return False
    
    try:
        from openpyxl import load_workbook
        wb = load_workbook(ARCHIVO_LOG)
        ws = wb.active
        
        encontrado = False
        for row in ws.iter_rows(min_row=2):
            if row[0].value == nombre_usuario:
                row[4].value = nuevo_estado
                row[6].value = obtener_fecha_creacion()
                encontrado = True
                break
        
        if encontrado:
            wb.save(ARCHIVO_LOG)
            crear_backup()
            registrar_auditoria("CAMBIAR_ESTADO", nombre_usuario, f"Estado: {nuevo_estado}")
            return True
        return False
    except Exception as e:
        pass
    return False

def buscar_usuarios_por_fecha(fecha_inicio, fecha_fin):
    usuarios_encontrados = []
    try:
        fecha_inicio_obj = datetime.strptime(fecha_inicio, "%d/%m/%Y")
        fecha_fin_obj = datetime.strptime(fecha_fin, "%d/%m/%Y").replace(hour=23, minute=59, second=59)
        
        from openpyxl import load_workbook
        wb = load_workbook(ARCHIVO_LOG)
        ws = wb.active
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and row[0]:
                fecha_usuario = parsear_fecha(row[2])
                if fecha_usuario and fecha_inicio_obj <= fecha_usuario <= fecha_fin_obj:
                    usuarios_encontrados.append(row)
    except Exception as e:
        pass
    
    return usuarios_encontrados

def buscar_usuarios_por_uso(uso_busqueda):
    usuarios_encontrados = []
    try:
        from openpyxl import load_workbook
        wb = load_workbook(ARCHIVO_LOG)
        ws = wb.active
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and row[0] and uso_busqueda.lower() in str(row[3]).lower():
                usuarios_encontrados.append(row)
    except Exception as e:
        pass
    
    return usuarios_encontrados

def buscar_usuarios_por_estado(estado):
    usuarios_encontrados = []
    try:
        from openpyxl import load_workbook
        wb = load_workbook(ARCHIVO_LOG)
        ws = wb.active
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row and row[0] and row[4] == estado:
                usuarios_encontrados.append(row)
    except Exception as e:
        pass
    
    return usuarios_encontrados

def borrar_usuario(nombre_usuario):
    if not OPENPYXL_DISPONIBLE:
        return False
    
    try:
        from openpyxl import load_workbook
        wb = load_workbook(ARCHIVO_LOG)
        ws = wb.active
        
        encontrado = False
        fila_a_borrar = None
        
        for row_num, row in enumerate(ws.iter_rows(min_row=2), start=2):
            if row[0].value == nombre_usuario:
                fila_a_borrar = row_num
                encontrado = True
                break
        
        if encontrado:
            ws.delete_rows(fila_a_borrar, 1)
            wb.save(ARCHIVO_LOG)
            crear_backup()
            registrar_auditoria("BORRAR_USUARIO", nombre_usuario, "Eliminado")
            return True
        return False
    except Exception as e:
        pass
    return False

def reset_todos_usuarios():
    if not OPENPYXL_DISPONIBLE:
        return False
    
    try:
        from openpyxl import load_workbook
        wb = load_workbook(ARCHIVO_LOG)
        ws = wb.active
        
        if ws.max_row > 1:
            ws.delete_rows(2, ws.max_row - 1)
        wb.save(ARCHIVO_LOG)
        crear_backup()
        registrar_auditoria("RESET_TOTAL", "SISTEMA", "Reset total")
        return True
    except Exception as e:
        pass
    return False

# ==================== ESTADÍSTICAS Y DASHBOARD ====================

def generar_dashboard():
    usuarios = leer_todos_usuarios()
    
    if not usuarios:
        print(f"\n{Colores.AMARILLO}No hay datos{Colores.RESET}")
        return
    
    total_usuarios = len(usuarios)
    activos = sum(1 for u in usuarios if u['estado'] == 'Activo')
    inactivos = sum(1 for u in usuarios if u['estado'] == 'Inactivo')
    
    dispositivos_unicos = set()
    usos_unicos = set()
    
    for u in usuarios:
        dispositivos_unicos.add(u['dispositivo'])
        if u['uso']:
            usos_unicos.add(u['uso'])
    
    print(f"\n{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}")
    print(f"{Colores.CYAN}{Colores.NEGRITA}     DASHBOARD - ESTADÍSTICAS{Colores.RESET}")
    print(f"{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}\n")
    
    print(f"{Colores.BLANCO}📊 {Colores.NEGRITA}RESUMEN:{Colores.RESET}")
    print(f"   {Colores.VERDE}✓ Total: {Colores.CYAN}{total_usuarios}{Colores.RESET}")
    print(f"   {Colores.VERDE}✓ Activos: {Colores.CYAN}{activos}{Colores.RESET}")
    print(f"   {Colores.VERDE}✓ Inactivos: {Colores.CYAN}{inactivos}{Colores.RESET}")
    
    porcentaje_activos = (activos / total_usuarios * 100) if total_usuarios > 0 else 0
    print(f"   {Colores.BLANCO}📈 Tasa: {Colores.VERDE}{porcentaje_activos:.1f}%{Colores.RESET}\n")
    
    print(f"{Colores.BLANCO}🖥️  {Colores.NEGRITA}DISPOSITIVOS:{Colores.RESET}")
    print(f"   {Colores.VERDE}✓ Únicos: {Colores.CYAN}{len(dispositivos_unicos)}{Colores.RESET}\n")
    
    print(f"{Colores.BLANCO}🏷️  {Colores.NEGRITA}USOS:{Colores.RESET}")
    print(f"   {Colores.VERDE}✓ Únicos: {Colores.CYAN}{len(usos_unicos)}{Colores.RESET}\n")
    
    print(f"{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}\n")

def busqueda_avanzada():
    print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
    print(f"{Colores.AMARILLO}{Colores.NEGRITA}BÚSQUEDA AVANZADA{Colores.RESET}")
    print(f"{Colores.CYAN}{'-'*70}{Colores.RESET}")
    
    usuarios = leer_todos_usuarios()
    resultados = usuarios[:]
    
    criterios_aplicados = []
    
    print(f"\n{Colores.BLANCO}Filtros:{Colores.RESET}")
    print(f"{Colores.AMARILLO}1.{Colores.RESET} Por nombre")
    print(f"{Colores.AMARILLO}2.{Colores.RESET} Por estado")
    print(f"{Colores.AMARILLO}3.{Colores.RESET} Por uso")
    print(f"{Colores.AMARILLO}4.{Colores.RESET} Por dispositivo")
    print(f"{Colores.AMARILLO}5.{Colores.RESET} Por fechas")
    print(f"{Colores.AMARILLO}6.{Colores.RESET} Ver resultados")
    print(f"{Colores.AMARILLO}0.{Colores.RESET} Cancelar")
    
    while True:
        opcion = input(f"\n{Colores.AMARILLO}Filtro (0-6): {Colores.RESET}").strip()
        
        if opcion == '1':
            nombre = input(f"{Colores.AMARILLO}Nombre: {Colores.RESET}").strip().lower()
            resultados = [u for u in resultados if nombre in u['nombre'].lower()]
            criterios_aplicados.append(f"Nombre: '{nombre}'")
            print(f"{Colores.VERDE}✓ Aplicado{Colores.RESET}")
        
        elif opcion == '2':
            estado = input(f"{Colores.AMARILLO}Estado (Activo/Inactivo): {Colores.RESET}").strip()
            if estado in ['Activo', 'Inactivo']:
                resultados = [u for u in resultados if u['estado'] == estado]
                criterios_aplicados.append(f"Estado: {estado}")
                print(f"{Colores.VERDE}✓ Aplicado{Colores.RESET}")
        
        elif opcion == '3':
            uso = input(f"{Colores.AMARILLO}Uso: {Colores.RESET}").strip().lower()
            resultados = [u for u in resultados if uso in str(u['uso']).lower()]
            criterios_aplicados.append(f"Uso: '{uso}'")
            print(f"{Colores.VERDE}✓ Aplicado{Colores.RESET}")
        
        elif opcion == '4':
            dispositivo = input(f"{Colores.AMARILLO}Dispositivo: {Colores.RESET}").strip().lower()
            resultados = [u for u in resultados if dispositivo in str(u['dispositivo']).lower()]
            criterios_aplicados.append(f"Dispositivo: '{dispositivo}'")
            print(f"{Colores.VERDE}✓ Aplicado{Colores.RESET}")
        
        elif opcion == '5':
            fecha_inicio = input(f"{Colores.AMARILLO}Inicio (DD/MM/YYYY): {Colores.RESET}").strip()
            fecha_fin = input(f"{Colores.AMARILLO}Fin (DD/MM/YYYY): {Colores.RESET}").strip()
            try:
                fecha_inicio_obj = datetime.strptime(fecha_inicio, "%d/%m/%Y")
                fecha_fin_obj = datetime.strptime(fecha_fin, "%d/%m/%Y").replace(hour=23, minute=59, second=59)
                resultados = [u for u in resultados if fecha_inicio_obj <= parsear_fecha(u['fecha']) <= fecha_fin_obj]
                criterios_aplicados.append(f"Fechas: {fecha_inicio} - {fecha_fin}")
                print(f"{Colores.VERDE}✓ Aplicado{Colores.RESET}")
            except:
                print(f"{Colores.ROJO}✗ Formato inválido{Colores.RESET}")
        
        elif opcion == '6':
            print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}")
            print(f"{Colores.MAGENTA}{Colores.NEGRITA}RESULTADOS{Colores.RESET}".center(100))
            print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}\n")
            
            if criterios_aplicados:
                print(f"{Colores.CYAN}Criterios:{Colores.RESET}")
                for criterio in criterios_aplicados:
                    print(f"  • {criterio}\n")
            
            if not resultados:
                print(f"{Colores.AMARILLO}Sin resultados{Colores.RESET}")
            else:
                print(f"{Colores.CYAN}{'USUARIO':<15} | {'FECHA':<20} | {'ESTADO':<12} | {'USO':<20}{Colores.RESET}")
                print(f"{Colores.CYAN}{'-'*75}{Colores.RESET}")
                
                for usuario in resultados:
                    estado_color = f"{Colores.VERDE}{usuario['estado']}{Colores.RESET}" if usuario['estado'] == 'Activo' else f"{Colores.ROJO}{usuario['estado']}{Colores.RESET}"
                    print(f"{usuario['nombre']:<15} | {str(usuario['fecha']):<20} | {estado_color:<32} | {str(usuario['uso']):<20}")
                
                print(f"\n{Colores.VERDE}Total: {len(resultados)}{Colores.RESET}")
            
            print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*100}{Colores.RESET}\n")
            break
        
        elif opcion == '0':
            break

# ==================== AUTENTICACIÓN ====================

def login_sistema():
    """Autentica al usuario antes de acceder al programa"""
    print(f"\n{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}")
    print(f"{Colores.CYAN}{Colores.NEGRITA}     SISTEMA DE AUTENTICACIÓN{Colores.RESET}")
    print(f"{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}\n")
    
    # Primera vez: configurar contraseña maestra
    if not os.path.exists(ARCHIVO_CONFIG):
        print(f"{Colores.AMARILLO}Primera vez ejecutando...{Colores.RESET}")
        SistemaSeguridad.configurar_contraseña_maestra()
    
    # Login normal
    intentos = 3
    while intentos > 0:
        contraseña = getpass.getpass(f"{Colores.AMARILLO}Contraseña maestra: {Colores.RESET}")
        
        if SistemaSeguridad.verificar_contraseña_maestra(contraseña):
            print(f"{Colores.VERDE}✓ Autenticado{Colores.RESET}\n")
            return True
        else:
            intentos -= 1
            if intentos > 0:
                print(f"{Colores.ROJO}✗ Incorrecta. Intentos: {intentos}{Colores.RESET}")
            else:
                print(f"{Colores.ROJO}✗ Acceso denegado{Colores.RESET}")
                return False
    
    return False

# ==================== MENÚS ====================

def mostrar_menu_principal():
    print(f"\n{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}")
    print(f"{Colores.CYAN}{Colores.NEGRITA}     GESTOR DE USUARIOS Y CONTRASEÑAS USB{Colores.RESET}")
    print(f"{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}")
    print(f"\n{Colores.AMARILLO}1.{Colores.RESET} Crear usuario automático")
    print(f"{Colores.AMARILLO}2.{Colores.RESET} Crear usuario personalizado")
    print(f"{Colores.AMARILLO}3.{Colores.RESET} Ver y gestionar usuarios")
    print(f"{Colores.AMARILLO}4.{Colores.RESET} Dashboard - Estadísticas")
    print(f"{Colores.AMARILLO}5.{Colores.RESET} Búsqueda Avanzada")
    print(f"{Colores.AMARILLO}6.{Colores.RESET} {Colores.ROJO}BÓVEDA DE CONTRASEÑAS{Colores.RESET}")
    print(f"{Colores.AMARILLO}7.{Colores.RESET} Salir")
    print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")

def mostrar_submenu_gestion():
    print(f"\n{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}")
    print(f"{Colores.CYAN}{Colores.NEGRITA}     GESTIÓN DE USUARIOS{Colores.RESET}")
    print(f"{Colores.CYAN}{Colores.NEGRITA}{'='*70}{Colores.RESET}")
    print(f"\n{Colores.AMARILLO}1.{Colores.RESET} Ver todos los usuarios")
    print(f"{Colores.AMARILLO}2.{Colores.RESET} Modificar estado")
    print(f"{Colores.AMARILLO}3.{Colores.RESET} Buscar por fecha")
    print(f"{Colores.AMARILLO}4.{Colores.RESET} Buscar por uso")
    print(f"{Colores.AMARILLO}5.{Colores.RESET} Listar por estado")
    print(f"{Colores.AMARILLO}6.{Colores.RESET} {Colores.ROJO}Borrar usuario{Colores.RESET}")
    print(f"{Colores.AMARILLO}7.{Colores.RESET} {Colores.ROJO}RESET TOTAL{Colores.RESET}")
    print(f"{Colores.AMARILLO}0.{Colores.RESET} Volver")
    print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")

# ==================== CREAR USUARIOS ====================

def crear_usuario_automatico():
    print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
    print(f"{Colores.MAGENTA}{Colores.NEGRITA}CREAR USUARIO AUTOMÁTICO{Colores.RESET}".center(70))
    print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
    
    usuarios_existentes = obtener_usuarios_existentes()
    contrasenas_hash = obtener_contrasenas_existentes()
    
    print(f"\n{Colores.AZUL}⏳ Generando usuario...{Colores.RESET}")
    nombre_usuario = generar_nombre_usuario(usuarios_existentes)
    print(f"{Colores.VERDE}✓ Usuario: {nombre_usuario}{Colores.RESET}")
    
    print(f"\n{Colores.AZUL}⏳ Generando contraseña...{Colores.RESET}")
    contraseña, contraseña_hash = generar_contraseña(contrasenas_hash)
    print(f"{Colores.VERDE}✓ Generada{Colores.RESET}")
    
    fecha = obtener_fecha_creacion()
    info_dispositivo = obtener_info_dispositivo()
    
    print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
    uso = input(f"{Colores.AMARILLO}Utilidad: {Colores.RESET}> ").strip()
    
    if not uso:
        uso = "Sin especificar"
    
    print(f"\n{Colores.AZUL}⏳ Guardando...{Colores.RESET}")
    resultado, contraseña_devuelta = guardar_usuario(nombre_usuario, contraseña, contraseña_hash, uso, info_dispositivo)
    
    if resultado:
        print(f"{Colores.VERDE}✓ Guardado completamente{Colores.RESET}")
        
        if copiar_al_portapapeles(contraseña):
            print(f"{Colores.VERDE}✓ Copiada al portapapeles{Colores.RESET}")
        
        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
        print(f"{Colores.BLANCO}Usuario: {Colores.CYAN}{nombre_usuario}{Colores.RESET}")
        print(f"{Colores.BLANCO}Contraseña: {Colores.CYAN}{contraseña}{Colores.RESET}")
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
    else:
        print(f"{Colores.ROJO}✗ Error - No se guardó{Colores.RESET}")

def crear_usuario_personalizado():
    print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
    print(f"{Colores.MAGENTA}{Colores.NEGRITA}CREAR USUARIO PERSONALIZADO{Colores.RESET}".center(70))
    print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
    
    contrasenas_hash = obtener_contrasenas_existentes()
    
    print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
    while True:
        nombre_usuario = input(f"{Colores.AMARILLO}Nombre (mín. 5 caracteres): {Colores.RESET}").strip()
        
        if len(nombre_usuario) < 5:
            print(f"{Colores.ROJO}✗ Mínimo 5 caracteres{Colores.RESET}")
        else:
            print(f"{Colores.VERDE}✓ Válido{Colores.RESET}")
            break
    
    print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
    print(f"{Colores.AMARILLO}1.{Colores.RESET} Generar contraseña automática")
    print(f"{Colores.AMARILLO}2.{Colores.RESET} Ingresar contraseña manualmente")
    opcion_pass = input(f"\n{Colores.AMARILLO}Opción: {Colores.RESET}").strip()
    
    if opcion_pass == '1':
        # CONTRASEÑA AUTOMÁTICA - requisitos estrictos
        contraseña, contraseña_hash = generar_contraseña(contrasenas_hash)
        print(f"{Colores.VERDE}✓ Generada con requisitos estrictos (12-28 caracteres){Colores.RESET}")
    else:
        # CONTRASEÑA MANUAL - requisitos reducidos
        print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
        print(f"{Colores.AMARILLO}Requisitos:{Colores.RESET}")
        print(f"  • Mínimo 8 caracteres")
        print(f"  • Alfanuméricos + caracteres especiales (@#.$%&*!?-_+=)")
        print(f"  • Al menos una mayúscula")
        print(f"  • Al menos un carácter especial\n")
        
        while True:
            contraseña = getpass.getpass(f"{Colores.AMARILLO}Contraseña: {Colores.RESET}")
            valida, detalles = verificar_contraseña_manual(contraseña)
            
            if not valida:
                print(f"{Colores.ROJO}✗ No cumple requisitos:{Colores.RESET}")
                for requisito, cumple in detalles.items():
                    estado = f"{Colores.VERDE}✓{Colores.RESET}" if cumple else f"{Colores.ROJO}✗{Colores.RESET}"
                    print(f"  {estado} {requisito}")
                print()
            else:
                print(f"{Colores.VERDE}✓ Contraseña válida{Colores.RESET}")
                break
        
        contraseña_hash = SistemaSeguridad.crear_hash_contraseña(contraseña)
    
    print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
    uso = input(f"{Colores.AMARILLO}Utilidad: {Colores.RESET}").strip()
    if not uso:
        uso = "Sin especificar"
    
    notas = input(f"{Colores.AMARILLO}Notas (opcional): {Colores.RESET}").strip()
    
    info_dispositivo = obtener_info_dispositivo()
    
    print(f"\n{Colores.AZUL}⏳ Guardando...{Colores.RESET}")
    resultado, _ = guardar_usuario(nombre_usuario, contraseña, contraseña_hash, uso, info_dispositivo, notas)
    
    if resultado:
        print(f"{Colores.VERDE}✓ Guardado completamente{Colores.RESET}")
        
        if copiar_al_portapapeles(contraseña):
            print(f"{Colores.VERDE}✓ Copiada{Colores.RESET}")
        
        print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
        print(f"{Colores.BLANCO}Usuario: {Colores.CYAN}{nombre_usuario}{Colores.RESET}")
        print(f"{Colores.BLANCO}Contraseña: {Colores.CYAN}{contraseña}{Colores.RESET}")
        print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*70}{Colores.RESET}")
    else:
        print(f"{Colores.ROJO}✗ Error - No se guardó{Colores.RESET}")

def ver_todos_usuarios():
    if not os.path.exists(ARCHIVO_LOG):
        print(f"\n{Colores.ROJO}✗ Archivo no existe{Colores.RESET}")
        return
    
    usuarios = leer_todos_usuarios()
    
    print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*120}{Colores.RESET}")
    print(f"{Colores.MAGENTA}{Colores.NEGRITA}LOG DE USUARIOS{Colores.RESET}".center(120))
    print(f"{Colores.MAGENTA}{Colores.NEGRITA}{'█'*120}{Colores.RESET}\n")
    
    if not usuarios:
        print(f"{Colores.AMARILLO}Sin registros{Colores.RESET}")
    else:
        print(f"{Colores.CYAN}{'USUARIO':<15} | {'FECHA':<20} | {'ESTADO':<12} | {'USO':<20} | {'DISPOSITIVO':<30}{Colores.RESET}")
        print(f"{Colores.CYAN}{'-'*110}{Colores.RESET}")
        
        for usuario in usuarios:
            estado_color = f"{Colores.VERDE}{usuario['estado']}{Colores.RESET}" if usuario['estado'] == 'Activo' else f"{Colores.ROJO}{usuario['estado']}{Colores.RESET}"
            print(f"{usuario['nombre']:<15} | {str(usuario['fecha']):<20} | {estado_color:<32} | {str(usuario['uso']):<20} | {str(usuario['dispositivo']):<30}")
        
        print(f"\n{Colores.CYAN}{'-'*110}{Colores.RESET}")
        print(f"{Colores.VERDE}Total: {len(usuarios)}{Colores.RESET}")
    
    print(f"\n{Colores.MAGENTA}{Colores.NEGRITA}{'█'*120}{Colores.RESET}")

def modificar_estado_usuario():
    print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
    nombre = input(f"{Colores.AMARILLO}Usuario: {Colores.RESET}").strip()
    
    usuarios = leer_todos_usuarios()
    usuario_existe = any(u['nombre'] == nombre for u in usuarios)
    
    if not usuario_existe:
        print(f"{Colores.ROJO}✗ No encontrado{Colores.RESET}")
        return
    
    usuario_actual = next(u for u in usuarios if u['nombre'] == nombre)
    print(f"\n{Colores.BLANCO}Estado: {Colores.VERDE if usuario_actual['estado'] == 'Activo' else Colores.ROJO}{usuario_actual['estado']}{Colores.RESET}")
    
    print(f"\n{Colores.AMARILLO}1.{Colores.RESET} Activo")
    print(f"{Colores.AMARILLO}2.{Colores.RESET} Inactivo")
    opcion = input(f"\n{Colores.AMARILLO}Opción: {Colores.RESET}").strip()
    
    nuevo_estado = "Activo" if opcion == "1" else "Inactivo" if opcion == "2" else None
    
    if nuevo_estado and cambiar_estado_usuario(nombre, nuevo_estado):
        print(f"{Colores.VERDE}✓ Modificado{Colores.RESET}")
    else:
        print(f"{Colores.ROJO}✗ Error{Colores.RESET}")

def buscar_por_fecha():
    print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
    fecha_inicio = input(f"{Colores.AMARILLO}Inicio (DD/MM/YYYY): {Colores.RESET}").strip()
    fecha_fin = input(f"{Colores.AMARILLO}Fin (DD/MM/YYYY): {Colores.RESET}").strip()
    
    usuarios = buscar_usuarios_por_fecha(fecha_inicio, fecha_fin)
    
    if not usuarios:
        print(f"{Colores.AMARILLO}Sin resultados{Colores.RESET}")
    else:
        print(f"\n{Colores.VERDE}Encontrados: {len(usuarios)}{Colores.RESET}")

def buscar_por_uso():
    print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
    uso_busqueda = input(f"{Colores.AMARILLO}Motivo: {Colores.RESET}").strip()
    
    usuarios = buscar_usuarios_por_uso(uso_busqueda)
    
    if not usuarios:
        print(f"{Colores.AMARILLO}Sin resultados{Colores.RESET}")
    else:
        print(f"\n{Colores.VERDE}Encontrados: {len(usuarios)}{Colores.RESET}")

def listar_por_estado():
    print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
    print(f"{Colores.AMARILLO}1.{Colores.RESET} Activos")
    print(f"{Colores.AMARILLO}2.{Colores.RESET} Inactivos")
    opcion = input(f"\n{Colores.AMARILLO}Opción: {Colores.RESET}").strip()
    
    estado = "Activo" if opcion == "1" else "Inactivo" if opcion == "2" else None
    
    if not estado:
        print(f"{Colores.ROJO}✗ Inválido{Colores.RESET}")
        return
    
    usuarios = buscar_usuarios_por_estado(estado)
    
    if not usuarios:
        print(f"{Colores.AMARILLO}Sin usuarios{Colores.RESET}")
    else:
        print(f"\n{Colores.VERDE}Total: {len(usuarios)}{Colores.RESET}")

def borrar_usuario_especifico():
    print(f"\n{Colores.ROJO}{Colores.NEGRITA}⚠️  OPERACIÓN PELIGROSA{Colores.RESET}")
    print(f"\n{Colores.CYAN}{'-'*70}{Colores.RESET}")
    nombre = input(f"{Colores.AMARILLO}Usuario a BORRAR: {Colores.RESET}").strip()
    
    usuarios = leer_todos_usuarios()
    usuario_existe = any(u['nombre'] == nombre for u in usuarios)
    
    if not usuario_existe:
        print(f"{Colores.ROJO}✗ No encontrado{Colores.RESET}")
        return
    
    confirmacion = input(f"{Colores.ROJO}Escribe 'SÍ': {Colores.RESET}").strip().upper()
    
    if confirmacion == "SÍ":
        confirmacion2 = input(f"{Colores.ROJO}Escribe 'BORRAR': {Colores.RESET}").strip().upper()
        
        if confirmacion2 == "BORRAR":
            if borrar_usuario(nombre):
                print(f"{Colores.VERDE}✓ Borrado{Colores.RESET}")

def reset_emergencia():
    print(f"\n{Colores.ROJO}{Colores.NEGRITA}⚠️  RESET TOTAL{Colores.RESET}")
    
    confirmacion = input(f"\n{Colores.ROJO}Escribe 'RESET TOTAL': {Colores.RESET}").strip().upper()
    
    if confirmacion == "RESET TOTAL":
        confirmacion2 = input(f"{Colores.ROJO}Escribe 'BORRAR TODO': {Colores.RESET}").strip().upper()
        
        if confirmacion2 == "BORRAR TODO":
            if reset_todos_usuarios():
                print(f"\n{Colores.VERDE}✓ Completado{Colores.RESET}")

def menu_gestion():
    while True:
        mostrar_submenu_gestion()
        opcion = input(f"{Colores.AMARILLO}Opción (0-7): {Colores.RESET}").strip()
        
        if opcion == '1':
            ver_todos_usuarios()
        elif opcion == '2':
            modificar_estado_usuario()
        elif opcion == '3':
            buscar_por_fecha()
        elif opcion == '4':
            buscar_por_uso()
        elif opcion == '5':
            listar_por_estado()
        elif opcion == '6':
            borrar_usuario_especifico()
        elif opcion == '7':
            reset_emergencia()
        elif opcion == '0':
            break

# ==================== MAIN ====================

def main():
    print(f"\n{Colores.CYAN}{Colores.NEGRITA}🔐 Iniciando Gestor USB...{Colores.RESET}")
    
    # Inicializar rutas en USB
    if not inicializar_rutas_usb():
        return
    
    # Actualizar rutas globales
    actualizar_rutas()
    
    if not OPENPYXL_DISPONIBLE or not ENCRIPTACION_DISPONIBLE:
        print(f"\n{Colores.ROJO}✗ Librerías faltantes{Colores.RESET}")
        print(f"{Colores.AMARILLO}Instala:{Colores.RESET}")
        print(f"{Colores.BLANCO}   pip install openpyxl pyperclip cryptography{Colores.RESET}\n")
        return
    
    try:
        import pyperclip
    except ImportError:
        print(f"{Colores.ROJO}✗ pyperclip no instalado{Colores.RESET}\n")
        return
    
    # LOGIN
    if not login_sistema():
        return
    
    verificar_archivo_existe()
    
    while True:
        mostrar_menu_principal()
        opcion = input(f"{Colores.AMARILLO}Opción (1-7): {Colores.RESET}").strip()
        
        if opcion == '1':
            crear_usuario_automatico()
        elif opcion == '2':
            crear_usuario_personalizado()
        elif opcion == '3':
            menu_gestion()
        elif opcion == '4':
            generar_dashboard()
        elif opcion == '5':
            busqueda_avanzada()
        elif opcion == '6':
            listar_usuarios_con_acceso_contraseña()
        elif opcion == '7':
            print(f"\n{Colores.MAGENTA}👋 ¡Hasta luego!{Colores.RESET}\n")
            break

if __name__ == "__main__":
    main()
