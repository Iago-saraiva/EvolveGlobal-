// ================================
// ANIMAÇÃO AO CARREGAR / ROLAR
// ================================
const revealElements = document.querySelectorAll(".reveal");

function revealOnScroll() {
  const triggerBottom = window.innerHeight - 100;

  revealElements.forEach((element) => {
    const elementTop = element.getBoundingClientRect().top;

    if (elementTop < triggerBottom) {
      element.classList.add("active");
    }
  });
}

window.addEventListener("scroll", revealOnScroll);
window.addEventListener("load", revealOnScroll);

// ================================
// CADASTRO
// ================================
const cadastroForm = document.getElementById("cadastroForm");

if (cadastroForm) {
  cadastroForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const nome = document.getElementById("nome").value.trim();
    const email = document.getElementById("email").value.trim();
    const senha = document.getElementById("senha").value.trim();

    if (!nome || !email || !senha) {
      alert("Preencha todos os campos!");
      return;
    }

    const usuario = {
      nome: nome,
      email: email,
      senha: senha
    };

    localStorage.setItem("usuario", JSON.stringify(usuario));

    alert("Cadastro realizado com sucesso!");
    window.location.href = "login.html";
  });
}

// ================================
// LOGIN
// ================================
const loginForm = document.getElementById("loginForm");

if (loginForm) {
  loginForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const emailDigitado = document.getElementById("loginEmail").value.trim();
    const senhaDigitada = document.getElementById("loginSenha").value.trim();

    const usuarioSalvo = JSON.parse(localStorage.getItem("usuario"));

    if (!usuarioSalvo) {
      alert("Nenhum usuário cadastrado! Faça seu cadastro primeiro.");
      return;
    }

    if (
      emailDigitado === usuarioSalvo.email &&
      senhaDigitada === usuarioSalvo.senha
    ) {
      localStorage.setItem("logado", "true");
      alert(`Bem-vindo, ${usuarioSalvo.nome}!`);
      window.location.href = "index.html";
    } else {
      alert("E-mail ou senha incorretos!");
    }
  });
}

// ================================
// REDIRECIONAR SE JÁ ESTIVER LOGADO
// (opcional: evita voltar para login)
// ================================
const logado = localStorage.getItem("logado");

if (
  logado === "true" &&
  (window.location.pathname.includes("login.html") ||
    window.location.pathname.includes("cadastro.html"))
) {
  // Se quiser ativar isso, descomente:
  // window.location.href = "index.html";
}

// ================================
// FUNÇÃO GLOBAL DE LOGOUT
// ================================
function logout() {
  localStorage.removeItem("logado");
  alert("Você saiu da conta.");
  window.location.href = "login.html";
}