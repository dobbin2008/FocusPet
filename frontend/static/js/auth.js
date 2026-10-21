const loginForm = document.getElementById("loginForm");
const cadastroForm = document.getElementById("cadastroForm");
const authMensagem = document.getElementById("authMensagem");
const fotoPerfilCadastro = document.getElementById("fotoPerfilCadastro");
const fotoPreviewBox = document.getElementById("fotoPreviewBox");
const fotoPreview = document.getElementById("fotoPreview");
const cadastroSenha = document.getElementById("cadastroSenha");
const senhaRequisitos = document.getElementById("senhaRequisitos");
let fotoPreviewUrl;
let captchaToken = "";
let captchaWidgetId;

if (authMensagem && new URLSearchParams(window.location.search).get("cadastro") === "ok") {
    authMensagem.textContent = "Cadastro concluído. Entre com seu email e senha.";
}

async function enviarFormularioAuth(url, dados) {
    const resposta = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados)
    });
    const resultado = await resposta.json();
    if (!resposta.ok) throw new Error(resultado.erro || "Não foi possível concluir a operação.");
    return resultado;
}

if (loginForm) {
    loginForm.addEventListener("submit", async (evento) => {
        evento.preventDefault();
        const dados = new FormData(loginForm);
        try {
            const resultado = await enviarFormularioAuth("/api/auth/login", {
                email: dados.get("email"),
                senha: dados.get("senha")
            });
            window.location.assign(resultado.destino);
        } catch (erro) {
            authMensagem.textContent = erro.message;
        }
    });
}

if (cadastroForm) {
    const cadastroSubmit = document.getElementById("cadastroSubmit");
    const captchaMensagem = document.getElementById("captchaMensagem");

    async function carregarCaptcha() {
        try {
            const resposta = await fetch("/api/auth/captcha-config");
            const configuracao = await resposta.json();
            if (!resposta.ok || !configuracao.site_key) {
                throw new Error("Verificação antirobô indisponível. Configure as chaves do CAPTCHA.");
            }

            await new Promise((resolve, reject) => {
                const script = document.createElement("script");
                script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
                script.async = true;
                script.defer = true;
                script.onload = resolve;
                script.onerror = () => reject(new Error("Não foi possível carregar a verificação antirobô."));
                document.head.appendChild(script);
            });

            captchaWidgetId = window.turnstile.render("#turnstileWidget", {
                sitekey: configuracao.site_key,
                callback: (token) => {
                    captchaToken = token;
                    cadastroSubmit.disabled = false;
                    captchaMensagem.textContent = "";
                },
                "expired-callback": () => {
                    captchaToken = "";
                    cadastroSubmit.disabled = true;
                    captchaMensagem.textContent = "A verificação expirou. Resolva-a novamente.";
                },
                "error-callback": () => {
                    captchaToken = "";
                    cadastroSubmit.disabled = true;
                    captchaMensagem.textContent = "Não foi possível concluir a verificação antirobô.";
                }
            });
        } catch (erro) {
            captchaMensagem.textContent = erro.message;
        }
    }

    carregarCaptcha();

    cadastroForm.addEventListener("submit", async (evento) => {
        evento.preventDefault();
        if (!captchaToken) {
            captchaMensagem.textContent = "Conclua a verificação antirobô antes de continuar.";
            return;
        }
        cadastroSubmit.disabled = true;
        try {
            const dados = new FormData(cadastroForm);
            dados.set("cf-turnstile-response", captchaToken);
            const resposta = await fetch("/api/auth/cadastro", {
                method: "POST",
                body: dados
            });
            const resultado = await resposta.json();
            if (!resposta.ok) throw new Error(resultado.erro || "Não foi possível criar a conta.");
            window.location.assign("/login?cadastro=ok");
        } catch (erro) {
            authMensagem.textContent = erro.message;
            captchaToken = "";
            window.turnstile.reset(captchaWidgetId);
        }
    });
}

if (fotoPerfilCadastro) {
    fotoPerfilCadastro.addEventListener("change", () => {
        if (fotoPreviewUrl) URL.revokeObjectURL(fotoPreviewUrl);
        const arquivo = fotoPerfilCadastro.files?.[0];
        if (!arquivo) {
            fotoPreviewBox.hidden = true;
            return;
        }
        fotoPreviewUrl = URL.createObjectURL(arquivo);
        fotoPreview.src = fotoPreviewUrl;
        fotoPreviewBox.hidden = false;
    });
}

if (cadastroSenha && senhaRequisitos) {
    const validarSenhaVisual = () => {
        const senha = cadastroSenha.value;
        const atendidos = {
            tamanho: Array.from(senha).length >= 12,
            maiuscula: /\p{Lu}/u.test(senha),
            minuscula: /\p{Ll}/u.test(senha),
            numero: /[\p{Nd}\p{No}]/u.test(senha),
            simbolo: Array.from(senha).some((caractere) => !/[\p{L}\p{N}\s]/u.test(caractere))
        };
        cadastroSenha.setCustomValidity(
            senha && !Object.values(atendidos).every(Boolean)
                ? "A senha deve cumprir todos os requisitos listados."
                : ""
        );
        senhaRequisitos.querySelectorAll("[data-requisito]").forEach((item) => {
            item.classList.toggle("requisito-atendido", atendidos[item.dataset.requisito]);
        });
    };
    cadastroSenha.addEventListener("input", validarSenhaVisual);
}

const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", async (evento) => {
        evento.preventDefault();
        await fetch("/api/auth/logout", { method: "POST" });
        window.location.assign("/login");
    });
}