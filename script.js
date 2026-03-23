// =========================
// ANIMAÇÃO AO ROLAR
// =========================
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

// =========================
// MENU MOBILE
// =========================
const menuBtn = document.getElementById("menuBtn");
const navMenu = document.getElementById("navMenu");

if (menuBtn && navMenu) {
  menuBtn.addEventListener("click", () => {
    navMenu.classList.toggle("active");
  });

  // Fecha menu ao clicar em um link
  const navLinks = navMenu.querySelectorAll("a");
  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      navMenu.classList.remove("active");
    });
  });
}

// =========================
// CONTADOR ANIMADO
// =========================
const counters = document.querySelectorAll(".counter");
let countersStarted = false;

function startCounters() {
  if (countersStarted) return;

  const statsSection = document.querySelector(".stats");
  if (!statsSection) return;

  const sectionTop = statsSection.getBoundingClientRect().top;
  const triggerPoint = window.innerHeight - 100;

  if (sectionTop < triggerPoint) {
    counters.forEach((counter) => {
      const target = +counter.getAttribute("data-target");
      let current = 0;
      const increment = Math.max(1, Math.ceil(target / 100));

      const updateCounter = () => {
        current += increment;

        if (current < target) {
          counter.innerText = current;
          requestAnimationFrame(updateCounter);
        } else {
          counter.innerText = target;
        }
      };

      updateCounter();
    });

    countersStarted = true;
  }
}

window.addEventListener("scroll", startCounters);
window.addEventListener("load", startCounters);

// ================================
// VERIFICA SE O USUÁRIO ESTÁ LOGADO
// ================================
const usuarioSalvo = JSON.parse(localStorage.getItem("usuario"));
const logadoIndex = localStorage.getItem("logado");

if (logadoIndex !== "true") {
  alert("Você precisa fazer login primeiro!");
  window.location.href = "login.html";
}

// ================================
// FUNÇÃO DE LOGOUT
// ================================
function logout() {
  localStorage.removeItem("logado");
  alert("Você saiu da conta.");
  window.location.href = "login.html";
}