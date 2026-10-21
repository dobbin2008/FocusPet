from backend.controllers.agenda_controller import agenda_bp
from backend.controllers.auth_controller import auth_bp
from backend.controllers.blacklist_controller import blacklist_bp
from backend.controllers.dashboard_controller import dashboard_bp
from backend.controllers.developer_controller import developer_bp
from backend.controllers.foco_controller import foco_bp
from backend.controllers.historico_foco_controller import historico_foco_bp
from backend.controllers.main_controller import main_bp
from backend.controllers.materias_controller import materias_bp
from backend.controllers.metas_controller import metas_bp
from backend.controllers.notas_controller import notas_bp
from backend.controllers.pet_controller import pet_bp
from backend.controllers.perfil_controller import perfil_bp
from backend.controllers.summary_controller import summary_bp

__all__ = [
    "agenda_bp",
    "auth_bp",
    "blacklist_bp",
    "dashboard_bp",
    "developer_bp",
    "foco_bp",
    "historico_foco_bp",
    "main_bp",
    "materias_bp",
    "metas_bp",
    "notas_bp",
    "pet_bp",
    "perfil_bp",
    "summary_bp",
]