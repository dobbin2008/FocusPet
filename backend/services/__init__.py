from backend.services.agenda_service import (
    ConcluirAtividadeService,
    CriarAtividadeService,
    ListarAtividadesService,
)
from backend.services.auth_service import (
    AutenticarEstudanteService,
    CadastrarEstudanteService,
)
from backend.services.blacklist_service import (
    AdicionarSiteBlacklistService,
    ListarBlacklistService,
    ListarUrlsBloqueadasService,
    RemoverSiteBlacklistService,
)
from backend.services.captcha_service import ValidarTurnstileService
from backend.services.dashboard_service import ObterDashboardService
from backend.services.developer_service import SimularEstudoService
from backend.services.foco_service import (
    ConsultarSessaoFocoService,
    EncerrarModoFocoService,
    IniciarModoFocoService,
    ObterSessaoFocoAtivaService,
    RegistrarDistracaoService,
    ValidarTokenSessaoService,
)
from backend.services.metas_service import (
    CalcularBonusMetaService,
    ConfigurarMetasEstudoService,
    ObterMetasEstudoService,
)
from backend.services.notas_service import (
    AtualizarNotaService,
    ExcluirNotaService,
    ObterNotaService,
)
from backend.services.pet_service import (
    CriarPetsIniciaisService,
    ConcederXpTestePetService,
    EquiparPetService,
    ListarPetsDisponiveisService,
)
from backend.services.summary_service import GerarResumoSemanalService

__all__ = [name for name in globals() if name.endswith("Service")]