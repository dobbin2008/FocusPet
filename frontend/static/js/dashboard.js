const petNome = document.getElementById("petNome");
const petImagem = document.getElementById("petImagem");
const xpTexto = document.getElementById("xpTexto");
const xpBarra = document.getElementById("xpBarra");
const petNivel = document.getElementById("petNivel");
const petXp = document.getElementById("petXp");
const estudanteXp = document.getElementById("estudanteXp");
const estudanteNome = document.getElementById("estudanteNome");
const estudanteEmail = document.getElementById("estudanteEmail");
const estudanteIniciais = document.getElementById("estudanteIniciais");
const estudanteFoto = document.getElementById("estudanteFoto");
const petDisponiveis = document.getElementById("petDisponiveis");
const petMensagem = document.getElementById("petMensagem");
const homeMain = document.querySelector(".home-main");
const inventarioToggle = document.getElementById("inventarioToggle");
const inventarioFechar = document.getElementById("inventarioFechar");
const petInventario = document.getElementById("petInventario");
const ganharXpTesteBtn = document.getElementById("ganharXpTesteBtn");
const resetarXpPetBtn = document.getElementById("resetarXpPetBtn");
const developerTools = document.getElementById("developerTools");
const simularEstudoForm = document.getElementById("simularEstudoForm");
const simularHoras = document.getElementById("simularHoras");
const developerMensagem = document.getElementById("developerMensagem");

async function carregarDashboard() {
    const respostaIniciais = await fetch("/api/pets/iniciais", { method: "POST" });
    if (!respostaIniciais.ok) throw new Error("Não foi possível preparar os pets da conta.");
    const [respostaDashboard, respostaPets, respostaSessao] = await Promise.all([
        fetch("/api/dashboard"),
        fetch("/api/pets"),
        fetch("/api/auth/session")
    ]);
    const dados = await respostaDashboard.json();
    const pets = await respostaPets.json();
    const sessao = await respostaSessao.json();
    if (!respostaDashboard.ok || !respostaPets.ok || !respostaSessao.ok) {
        throw new Error(dados.erro || "Não foi possível carregar o dashboard.");
    }
    if (developerTools) developerTools.hidden = !sessao.is_developer;

    const xpNivel = dados.pet?.xp_progresso_nivel || 0;
    petNome.textContent = dados.pet?.nome || "Nenhum pet equipado";
    petImagem.src = dados.pet?.imagem_url || "/static/img/weedle%20base%20grup0.png";
    xpTexto.textContent = dados.pet
        ? dados.pet.proximo_nivel
            ? `${xpNivel} / 100 XP para o nível ${dados.pet.proximo_nivel}`
            : "Nível máximo alcançado"
        : "Equipe um pet para começar a evolução.";
    xpBarra.style.width = `${xpNivel}%`;
    petNivel.textContent = dados.pet?.nivel ?? "—";
    petXp.textContent = dados.pet?.xp_atual ?? "—";
    estudanteXp.textContent = dados.estudante.xp_total;
    estudanteNome.textContent = dados.estudante.nome;
    estudanteEmail.textContent = dados.estudante.email;
    estudanteIniciais.textContent = dados.estudante.iniciais;
    estudanteFoto.hidden = !dados.estudante.foto_url;
    estudanteIniciais.hidden = Boolean(dados.estudante.foto_url);
    if (dados.estudante.foto_url) {
        estudanteFoto.src = dados.estudante.foto_url;
        estudanteFoto.onerror = () => {
            estudanteFoto.hidden = true;
            estudanteIniciais.hidden = false;
        };
    } else {
        estudanteFoto.removeAttribute("src");
    }

    petDisponiveis.replaceChildren();
    if (!pets.pets.length) {
        const vazio = document.createElement("p");
        vazio.textContent = "Nenhum pet disponível para esta conta.";
        petDisponiveis.appendChild(vazio);
    }
    pets.pets.forEach((pet) => {
        const card = document.createElement("article");
        card.className = "pet-opcao";
        const imagem = document.createElement("img");
        imagem.src = pet.imagem_url;
        imagem.alt = `${pet.nome}, nível ${pet.nivel}`;
        imagem.className = "pet-miniatura";
        const detalhes = document.createElement("div");
        detalhes.className = "pet-detalhes";
        const nome = document.createElement("h3");
        nome.textContent = pet.nome;
        const nivel = document.createElement("p");
        nivel.textContent = `Nível ${pet.nivel} · ${pet.xp_atual} XP total`;
        const progresso = document.createElement("p");
        progresso.textContent = pet.proximo_nivel
            ? `${pet.xp_progresso_nivel} / 100 XP para nível ${pet.proximo_nivel}`
            : "Nível máximo";
        const barra = document.createElement("progress");
        barra.max = 100;
        barra.value = pet.xp_progresso_nivel;
        barra.setAttribute("aria-label", `Progresso de ${pet.nome} para o próximo nível`);
        detalhes.append(nome, nivel, progresso, barra);
        const equipar = document.createElement("button");
        const estaEquipado = dados.pet?.id === pet.id;
        card.classList.toggle("pet-opcao-equipado", estaEquipado);
        equipar.type = "button";
        equipar.textContent = estaEquipado ? "Em uso" : "Equipar";
        equipar.disabled = estaEquipado;
        equipar.addEventListener("click", () => equiparPet(pet.id));
        card.append(imagem, detalhes, equipar);
        petDisponiveis.appendChild(card);
    });

}

if (petNome && xpTexto && xpBarra && petDisponiveis) {
    carregarDashboard().catch(() => {
        petNome.textContent = "Dashboard indisponível";
        xpTexto.textContent = "Não foi possível carregar os dados.";
    });
}

async function equiparPet(petId) {
    petMensagem.textContent = "";
    const resposta = await fetch("/api/pets/equipar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pet_id: petId })
    });
    const resultado = await resposta.json();
    if (!resposta.ok) {
        petMensagem.textContent = resultado.erro || "Não foi possível equipar o pet.";
        return;
    }
    fecharInventario();
    await carregarDashboard();
}

function abrirInventario() {
    petInventario.hidden = false;
    homeMain.classList.add("inventario-aberto");
    inventarioToggle.setAttribute("aria-expanded", "true");
    inventarioToggle.setAttribute("aria-label", "Fechar inventário de pets");
}

function fecharInventario() {
    petInventario.hidden = true;
    homeMain.classList.remove("inventario-aberto");
    inventarioToggle.setAttribute("aria-expanded", "false");
    inventarioToggle.setAttribute("aria-label", "Abrir inventário de pets");
}

inventarioToggle.addEventListener("click", () => {
    if (petInventario.hidden) abrirInventario();
    else fecharInventario();
});
inventarioFechar.addEventListener("click", fecharInventario);
document.addEventListener("keydown", (evento) => {
    if (evento.key === "Escape" && !petInventario.hidden) fecharInventario();
});

if (ganharXpTesteBtn) {
    ganharXpTesteBtn.addEventListener("click", async () => {
        developerMensagem.textContent = "";
        ganharXpTesteBtn.disabled = true;
        try {
            const resposta = await fetch("/api/pets/teste/ganhar-xp", { method: "POST" });
            const resultado = await resposta.json();
            if (!resposta.ok) throw new Error(resultado.erro || "Não foi possível conceder XP.");
            await carregarDashboard();
            developerMensagem.textContent = `${resultado.pet.nome} ganhou 100 XP de teste.`;
        } catch (erro) {
            developerMensagem.textContent = erro.message;
        } finally {
            ganharXpTesteBtn.disabled = false;
        }
    });
}

if (resetarXpPetBtn) {
    resetarXpPetBtn.addEventListener("click", async () => {
        if (!window.confirm("Zerar o XP do pet equipado? O XP dos outros pets não será alterado.")) return;
        developerMensagem.textContent = "";
        resetarXpPetBtn.disabled = true;
        try {
            const resposta = await fetch("/api/desenvolvedor/resetar-xp-pet", {
                method: "POST"
            });
            const resultado = await resposta.json();
            if (!resposta.ok) throw new Error(resultado.erro || "Não foi possível resetar o XP.");
            await carregarDashboard();
            developerMensagem.textContent =
                `${resultado.pet.nome} voltou à forma base. ${resultado.xp_resetado} XP resetado; o XP dos outros pets foi mantido.`;
        } catch (erro) {
            developerMensagem.textContent = erro.message;
        } finally {
            resetarXpPetBtn.disabled = false;
        }
    });
}

if (simularEstudoForm) {
    simularEstudoForm.addEventListener("submit", async (evento) => {
        evento.preventDefault();
        developerMensagem.textContent = "";
        const botao = simularEstudoForm.querySelector('[type="submit"]');
        botao.disabled = true;
        try {
            const resposta = await fetch("/api/desenvolvedor/simular-estudo", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ horas: simularHoras.value })
            });
            const resultado = await resposta.json();
            if (!resposta.ok) throw new Error(resultado.erro || "Não foi possível simular o estudo.");
            await carregarDashboard();
            developerMensagem.textContent =
                `${resultado.horas_estudadas} h registradas como estudo concluído; +${resultado.xp_ganho} XP.`;
        } catch (erro) {
            developerMensagem.textContent = erro.message;
        } finally {
            botao.disabled = false;
        }
    });
}