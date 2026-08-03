
// MODO ESCURO / CLARO
 

const temaBtn = document.getElementById("temaBtn");

function atualizarIcone() {
    if (document.body.classList.contains("claro")) {
        temaBtn.textContent = "🌙";
    } else {
        temaBtn.textContent = "☀️";
    }
}

const temaSalvo = localStorage.getItem("tema");

if (temaSalvo === "light") {
    document.body.classList.add("claro");
} else {
    document.body.classList.remove("claro");
}

atualizarIcone();

temaBtn.addEventListener("click", () => {

    document.body.classList.toggle("claro");

    if (document.body.classList.contains("claro")) {
        localStorage.setItem("tema", "light");
    } else {
        localStorage.setItem("tema", "dark");
    }

    atualizarIcone();

});



// LOGIN MODAL


const openLogin = document.getElementById("loginBtn");
const closeLogin = document.getElementById("fecharBtn");
const modal = document.getElementById("loginModal");

function abrirLogin() {
    modal.classList.add("active");
}

function fecharLogin() {
    modal.classList.remove("active");
}

// Abrir

openLogin.addEventListener("click", abrirLogin);

// Fechar no X

closeLogin.addEventListener("click", fecharLogin);

// Fechar clicando fora

modal.addEventListener("click", (e) => {

    if (e.target === modal) {
        fecharLogin();
    }

});

// Fechar com ESC

document.addEventListener("keydown", (e) => {

    if (e.key === "Escape") {
        fecharLogin();
    }

});