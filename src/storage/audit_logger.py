"""Registro de auditoría"""
import json
from pathlib import Path
from datetime import datetime
from config.settings import AppConfig
from models.auditoria import Auditoria
from utils.network import RedUtils
from typing import List


class RegistradorAuditoria:
    """Registra todas las acciones en auditoría"""
    
    def __init__(self, config: AppConfig):
        self.config = config
    
    def log_action(
        self,
        action: str,
        affected_user: str,
        details: str = ""
    ):
        """Registra una acción"""
        try:
            timestamp = datetime.now().isoformat()
            username = RedUtils.get_system_username()
            ip = RedUtils.get_device_ip()
            
            record = Auditoria(
                timestamp=timestamp,
                accion=action,
                usuario_afectado=affected_user,
                usuario_sistema=username,
                dispositivo=ip,
                detalles=details
            )
            
            # Cargar auditoría existente
            audit_log = self._load_audit_log()
            audit_log.append(record.to_dict())
            
            # Guardar
            self.config.archivo_auditoria.write_text(
                json.dumps(audit_log, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        
        except Exception as e:
            pass  # No interrumpir operación por error de auditoría
    
    def get_all_records(self) -> List[Auditoria]:
        """Obtiene todos los registros de auditoría"""
        records = []
        log = self._load_audit_log()
        
        for record_data in log:
            records.append(Auditoria.from_dict(record_data))
        
        return records
    
    def get_records_by_action(self, action: str) -> List[Auditoria]:
        """Obtiene registros por acción"""
        return [r for r in self.get_all_records() if r.accion == action]
    
    def _load_audit_log(self) -> list:
        """Carga log de auditoría"""
        if not self.config.archivo_auditoria.exists():
            return []
        
        try:
            content = self.config.archivo_auditoria.read_text(encoding='utf-8')
            if content.strip():
                return json.loads(content)
        except Exception:
            pass
        
        return []