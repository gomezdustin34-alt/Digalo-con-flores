document.addEventListener("DOMContentLoaded", () => {
  // Navbar con sombra al hacer scroll
  const navbar = document.querySelector(".navbar");
  if (navbar) {
    const onScroll = () => navbar.classList.toggle("is-scrolled", window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // Menú móvil
  const toggle = document.querySelector(".nav-toggle");
  const mobileMenu = document.querySelector(".mobile-menu");
  const closeBtn = document.querySelector(".mobile-menu-close");
  if (toggle && mobileMenu) {
    toggle.addEventListener("click", () => mobileMenu.classList.add("is-open"));
    closeBtn?.addEventListener("click", () => mobileMenu.classList.remove("is-open"));
  }

  // Aparición progresiva al hacer scroll
  const revealEls = document.querySelectorAll(".reveal");
  const mostrarTodo = () => revealEls.forEach((el) => el.classList.add("is-visible"));

  if ("IntersectionObserver" in window && revealEls.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      // Se activan un poco antes de entrar en pantalla: la transición se
      // completa justo cuando el usuario llega al elemento.
      { threshold: 0.1, rootMargin: "0px 0px 120px 0px" }
    );
    revealEls.forEach((el) => observer.observe(el));
    // Red de seguridad: si algo impide que el observador actúe, nada queda oculto.
    setTimeout(mostrarTodo, 3000);
  } else {
    mostrarTodo();
  }

  // Confirmación antes de enviar formularios destructivos
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      if (!confirm(form.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  // Aviso de cookies: se muestra una sola vez por navegador. El acceso al
  // almacenamiento local puede fallar (modo privado, cookies bloqueadas), y en
  // ese caso simplemente se muestra el aviso sin recordar que se cerro.
  const cookieNotice = document.getElementById("cookie-notice");
  if (cookieNotice) {
    const CLAVE = "aviso_cookies";
    let yaVisto = false;
    try {
      yaVisto = localStorage.getItem(CLAVE) === "1";
    } catch (e) {
      yaVisto = false;
    }
    if (!yaVisto) {
      cookieNotice.hidden = false;
      const aceptar = document.getElementById("cookie-notice-accept");
      if (aceptar) {
        aceptar.addEventListener("click", () => {
          cookieNotice.hidden = true;
          try {
            localStorage.setItem(CLAVE, "1");
          } catch (e) {
            /* sin almacenamiento: el aviso volvera a aparecer, no pasa nada */
          }
        });
      }
    }
  }

  // Auto-cierre de flash messages
  document.querySelectorAll(".flash").forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity 0.4s ease";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 400);
    }, 4500);
  });
});
