const perfilForm = document.getElementById("perfilForm");
const perfilNome = document.getElementById("perfilNome");
const perfilEmail = document.getElementById("perfilEmail");
const perfilSenhaAtual = document.getElementById("perfilSenhaAtual");
const perfilNovaSenha = document.getElementById("perfilNovaSenha");
const perfilConfirmarSenha = document.getElementById("perfilConfirmarSenha");
const perfilFoto = document.getElementById("perfilFoto");
const removerFoto = document.getElementById("removerFoto");
const perfilFotoAtual = document.getElementById("perfilFotoAtual");
const perfilIniciais = document.getElementById("perfilIniciais");
const perfilMensagem = document.getElementById("perfilMensagem");

function atualizarFotoPerfil(url, nome) {
    perfilIniciais.textContent = nome.trim().split(/\s+/).slice(0, 2).map((parte) => parte[0]).join("").toUpperCase() || "—";
    perfilFotoAtual.hidden = !url;
    perfilIniciais.hidden = Boolean(url);
    if (url) perfilFotoAtual.src = `${url}?t=${Date.now()}`;
    else perfilFotoAtual.removeAttribute("src");
}

async function carregarPerfil() {
    const resposta = await fetch("/api/perfil");
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro || "Não foi possível carregar o perfil.");
    perfilNome.value = dados.nome;
    perfilEmail.value = dados.email;
    atualizarFotoPerfil(dados.foto_url, dados.nome);
}

perfilForm.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    perfilMensagem.textContent = "";
    const botao = perfilForm.querySelector('[type="submit"]');
    botao.disabled = true;
    const dados = new FormData();
    dados.set("nome", perfilNome.value);
    dados.set("email", perfilEmail.value);
    dados.set("remover_foto", String(removerFoto.checked));
    dados.set("senha_atual", perfilSenhaAtual.value);
    dados.set("nova_senha", perfilNovaSenha.value);
    dados.set("confirmar_senha", perfilConfirmarSenha.value);
    const arquivo = perfilFoto.files[0];
    if (arquivo) dados.set("foto_perfil", arquivo);
    try {
        const resposta = await fetch("/api/perfil", { method: "PATCH", body: dados });
        const resultado = await resposta.json();
        if (!resposta.ok) throw new Error(resultado.erro || "Não foi possível salvar o perfil.");
        perfilNome.value = resultado.nome;
        perfilEmail.value = resultado.email;
        atualizarFotoPerfil(resultado.foto_url, resultado.nome);
        perfilFoto.value = "";
        removerFoto.checked = false;
        perfilSenhaAtual.value = "";
        perfilNovaSenha.value = "";
        perfilConfirmarSenha.value = "";
        perfilMensagem.textContent = "Perfil atualizado.";
    } catch (erro) {
        perfilMensagem.textContent = erro.message;
    } finally {
        botao.disabled = false;
    }
});

carregarPerfil().catch((erro) => {
    perfilMensagem.textContent = erro.message;
});
