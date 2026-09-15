from .auth_controller import auth_bp
from .admin_controller import admin_bp
from .main_controller import main_bp
from .agenda_controller import agenda_bp
from .notas_controller import notas_bp
from .foco_controller import foco_bp
from .blacklist_controller import blacklist_bp

__all__ = [
	"auth_bp",
	"admin_bp",
	"main_bp",
	"agenda_bp",
	"notas_bp",
	"foco_bp",
	"blacklist_bp",
]
