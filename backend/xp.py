ATIVIDADE_XP_MAXIMO = 50
FOCO_XP_MAXIMO = 100
MINUTOS_PARA_XP_MAXIMO = 4 * 60
XP_POR_DISTRACAO = 20


def calcular_xp_bonus_meta(meta_minutos):
    minutos = max(0, min(240, int(meta_minutos or 0)))
    if minutos == 0:
        return 0
    if minutos <= 60:
        return max(1, (minutos * 10 + 30) // 60)
    return 10 + ((minutos - 60) * 10 + 90) // 180


def calcular_xp_atividade(duracao_minutos):
    minutos = max(0, int(duracao_minutos or 0))
    return min(
        ATIVIDADE_XP_MAXIMO,
        minutos * ATIVIDADE_XP_MAXIMO // MINUTOS_PARA_XP_MAXIMO,
    )


def calcular_xp_foco(duracao_minutos, distracoes):
    minutos = max(0, int(duracao_minutos or 0))
    quantidade_distracoes = max(0, int(distracoes or 0))
    xp_por_tempo = min(
        FOCO_XP_MAXIMO,
        minutos * FOCO_XP_MAXIMO // MINUTOS_PARA_XP_MAXIMO,
    )
    return max(0, xp_por_tempo - quantidade_distracoes * XP_POR_DISTRACAO)
