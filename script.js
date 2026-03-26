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

// Controle do bot que se move com o scroll
class MovingBot {
  constructor() {
    this.bot = document.querySelector('.bot');
    this.lastScrollTop = 0;
    this.scrollTimeout = null;
    this.isMoving = false;
    
    this.init();
  }
  
  init() {
    if (!this.bot) return;
    
    // Esconder bot inicialmente
    this.bot.classList.add('hide');
    
    // Aguardar um pouco antes de mostrar
    setTimeout(() => {
      this.bot.classList.remove('hide');
      this.bot.classList.add('show');
    }, 1000);
    
    // Adicionar eventos de scroll
    window.addEventListener('scroll', () => this.handleScroll());
    window.addEventListener('wheel', () => this.handleWheel());
    
    // Adicionar evento de hover para pausar movimento
    this.bot.addEventListener('mouseenter', () => this.pauseMovement());
    this.bot.addEventListener('mouseleave', () => this.resumeMovement());
  }
  
  handleScroll() {
    if (!this.bot) return;
    
    const currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollDirection = currentScrollTop > this.lastScrollTop ? 'down' : 'up';
    
    // Adicionar classe de movimento baseado na direção
    if (scrollDirection === 'down') {
      this.moveBotDown();
    } else {
      this.moveBotUp();
    }
    
    this.lastScrollTop = currentScrollTop;
    
    // Limpar timeout anterior
    if (this.scrollTimeout) {
      clearTimeout(this.scrollTimeout);
    }
    
    // Voltar à posição original após parar de scrollar
    this.scrollTimeout = setTimeout(() => {
      this.resetBotPosition();
    }, 150);
  }
  
  handleWheel() {
    if (!this.bot) return;
    
    // Pequeno movimento extra baseado no wheel
    const delta = event.deltaY;
    if (delta > 0) {
      this.moveBotDown();
    } else {
      this.moveBotUp();
    }
  }
  
  moveBotDown() {
    if (this.isMoving && this.paused) return;
    
    const currentBottom = parseInt(window.getComputedStyle(this.bot).bottom);
    const maxBottom = window.innerHeight - 100; // Limite máximo
    
    let newBottom = currentBottom - 10;
    newBottom = Math.max(20, Math.min(newBottom, maxBottom));
    
    this.bot.style.transition = 'bottom 0.2s ease-out';
    this.bot.style.bottom = newBottom + 'px';
  }
  
  moveBotUp() {
    if (this.isMoving && this.paused) return;
    
    const currentBottom = parseInt(window.getComputedStyle(this.bot).bottom);
    const minBottom = 20;
    
    let newBottom = currentBottom + 10;
    newBottom = Math.min(maxBottom, Math.max(newBottom, minBottom));
    
    this.bot.style.transition = 'bottom 0.2s ease-out';
    this.bot.style.bottom = newBottom + 'px';
  }
  
  resetBotPosition() {
    if (!this.bot || this.paused) return;
    
    this.bot.style.transition = 'bottom 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
    this.bot.style.bottom = '30px';
    
    // Remover a transição especial após completar
    setTimeout(() => {
      if (this.bot) {
        this.bot.style.transition = '';
      }
    }, 500);
  }
  
  pauseMovement() {
    this.paused = true;
  }
  
  resumeMovement() {
    this.paused = false;
  }
}

// Versão alternativa mais simples - movimento suave
function simpleMovingBot() {
  const bot = document.querySelector('.bot');
  if (!bot) return;
  
  let lastScrollY = window.scrollY;
  let ticking = false;
  
  function updateBotPosition() {
    const currentScrollY = window.scrollY;
    const scrollDelta = currentScrollY - lastScrollY;
    
    // Limitar o movimento máximo
    const moveLimit = 50;
    let moveAmount = Math.min(Math.abs(scrollDelta), moveLimit);
    
    if (scrollDelta > 0) {
      // Scroll para baixo - bot sobe um pouco
      bot.style.transform = `translateY(-${moveAmount * 0.3}px)`;
    } else if (scrollDelta < 0) {
      // Scroll para cima - bot desce um pouco
      bot.style.transform = `translateY(${moveAmount * 0.3}px)`;
    }
    
    lastScrollY = currentScrollY;
    ticking = false;
    
    // Resetar posição após parar
    clearTimeout(window.resetTimeout);
    window.resetTimeout = setTimeout(() => {
      bot.style.transform = 'translateY(0)';
    }, 200);
  }
  
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(updateBotPosition);
      ticking = true;
    }
  });
}



// chatbot
simpleMovingBot();

// add efect pulse
function addPulseEffect() {
  const bot = document.querySelector('.bot a');
  if (!bot) return;
  
  setInterval(() => {
    bot.style.animation = 'none';
    bot.offsetHeight;
    bot.style.animation = 'pulse 0.5s ease';
    
    setTimeout(() => {
      if (bot) bot.style.animation = '';
    }, 500);
  }, 50000); // Pulsa a cada 30 segundos
}

// Adicionar animação de pulso ao CSS
const style = document.createElement('style');
style.textContent = `
  @keyframes pulse {
    0% {
      transform: scale(1);
      box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
    }
    50% {
      transform: scale(1.1);
      box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);
    }
    100% {
      transform: scale(1);
      box-shadow: 0 0 0 0 rgba(102, 126, 234, 0);
    }
  }
`;
document.head.appendChild(style);

// Iniciar efeito de pulso
setTimeout(() => {
  addPulseEffect();
}, 2000);