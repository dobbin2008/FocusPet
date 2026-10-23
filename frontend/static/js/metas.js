const metasForm = document.getElementById("metasForm");
const metasMensagem = document.getElementById("metasMensagem");
const salvarMetasBtn = document.getElementById("salvarMetasBtn");
const metaDiariaInput = document.getElementById("metaDiaria");
const metaSemanalInput = document.getElementById("metaSemanal");
const metaDiariaUnidade = document.getElementById("metaDiariaUnidade");
const metaSemanalUnidade = document.getElementById("metaSemanalUnidade");
const metaSemanalAjuda = document.getElementById("metaSemanalAjuda");
let unidadeDiariaAnterior = "minutos";

function formatarTempo(minutos) {
    const horas = Math.floor(minutos / 60);
    const restantes = minutos % 60;
    if (horas && restantes) return `${horas} h ${restantes} min`;
    if (horas) return `${horas} h`;
    return `${restantes} min`;
}

function renderizarProgresso(tipo, dados) {
    const diario = tipo === "diaria";
    const texto = document.getElementById(diario ? "metaDiariaTexto" : "metaSemanalTexto");
    const barra = document.getElementById(diario ? "metaDiariaBarra" : "metaSemanalBarra");
    const status = document.getElementById(diario ? "metaDiariaStatus" : "metaSemanalStatus");
    const bonus = document.getElementById(diario ? "metaDiariaBonus" : "metaSemanalBonus");

    const metaDias = dados.meta_dias || 0;
    const valorMeta = metaDias || dados.meta_minutos;
    if (!valorMeta) {
        texto.textContent = "Meta desativada.";
        barra.value = 0;
        status.textContent = "Opcional";
        bonus.textContent = "Configure uma meta para acompanhar seu progresso.";
        return;
    }
    texto.textContent = metaDias
        ? `${dados.dias_estudados} de ${metaDias} ${metaDias === 1 ? "dia" : "dias"} estudados`
        : `${formatarTempo(dados.minutos_estudados)} de ${formatarTempo(dados.meta_minutos)}`;
    barra.value = dados.percentual;
    status.textContent = dados.atingida ? "Meta alcançada!" : `${dados.percentual}%`;
    bonus.textContent = dados.bonus_concedido
        ? `Bônus de +${dados.bonus_xp} XP recebido neste período.`
        : dados.atingida
            ? `Bônus de +${dados.bonus_xp} XP será adicionado ao encerrar a sessão que atingiu a meta.`
            : `Bônus de até +${dados.bonus_xp} XP ao atingir a meta.`;
}

function exibirMetas(dados, unidadeDiaria = null) {
    const metaDiariaEmHoras = unidadeDiaria === "horas"
        || (!unidadeDiaria && dados.meta_diaria_minutos > 0
            && dados.meta_diaria_minutos % 60 === 0);
    metaDiariaUnidade.value = metaDiariaEmHoras ? "horas" : "minutos";
    metaDiariaInput.value = metaDiariaEmHoras
        ? dados.meta_diaria_minutos / 60
        : dados.meta_diaria_minutos;
    if (dados.meta_semanal_dias) {
        metaSemanalUnidade.value = "dias";
        metaSemanalInput.value = dados.meta_semanal_dias;
    } else {
        metaSemanalUnidade.value = "horas";
        metaSemanalInput.value = dados.meta_semanal_minutos / 60;
    }
    unidadeDiariaAnterior = metaDiariaUnidade.value;
    atualizarLimites();
    renderizarProgresso("diaria", dados.diaria);
    renderizarProgresso("semanal", dados.semanal);
}

function atualizarLimites() {
    const diariaEmHoras = metaDiariaUnidade.value === "horas";
    metaDiariaInput.max = diariaEmHoras ? "24" : "1440";
    metaDiariaInput.step = diariaEmHoras ? "0.25" : "1";

    const semanalEmDias = metaSemanalUnidade.value === "dias";
    metaSemanalInput.max = semanalEmDias ? "7" : "168";
    metaSemanalInput.step = semanalEmDias ? "1" : "0.25";
    metaSemanalAjuda.textContent = semanalEmDias
        ? "Conte dias diferentes com ao menos uma sessão de foco concluída. A meta máxima é 7 dias; o bônus é de 10 XP por dia, limitado a 20 XP."
        : "Use 0 para desativar. A meta semanal máxima é 168 horas.";
}

async function carregarMetas() {
    const resposta = await fetch("/api/metas");
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro || "Não foi possível carregar suas metas.");
    exibirMetas(dados);
}

metaDiariaUnidade.addEventListener("change", () => {
    const valor = Number(metaDiariaInput.value || 0);
    metaDiariaInput.value = unidadeDiariaAnterior === "minutos"
        ? valor / 60
        : valor * 60;
    unidadeDiariaAnterior = metaDiariaUnidade.value;
    atualizarLimites();
});
metaSemanalUnidade.addEventListener("change", () => {
    metaSemanalInput.value = 0;
    atualizarLimites();
});

metasForm.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    salvarMetasBtn.disabled = true;
    metasMensagem.textContent = "";
    try {
        const resposta = await fetch("/api/metas", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                meta_diaria_minutos: Math.round(
                    Number(metaDiariaInput.value) *
                        (metaDiariaUnidade.value === "horas" ? 60 : 1)
                ),
                meta_semanal_minutos: metaSemanalUnidade.value === "horas"
                    ? Math.round(Number(metaSemanalInput.value) * 60)
                    : 0,
                meta_semanal_dias: metaSemanalUnidade.value === "dias"
                    ? Number(metaSemanalInput.value)
                    : 0
            })
        });
        const dados = await resposta.json();
        if (!resposta.ok) throw new Error(dados.erro || "Não foi possível salvar as metas.");
        exibirMetas(dados, metaDiariaUnidade.value);
        metasMensagem.textContent = "Metas salvas.";
    } catch (erro) {
        metasMensagem.textContent = erro.message;
    } finally {
        salvarMetasBtn.disabled = false;
    }
});

carregarMetas().catch((erro) => {
    metasMensagem.textContent = erro.message;
});
