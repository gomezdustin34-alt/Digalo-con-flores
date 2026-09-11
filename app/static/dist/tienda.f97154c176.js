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

function getCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]')?.content || "";
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".add-to-cart-form").forEach((form) => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const button = form.querySelector("button[type=submit]");
      const originalText = button ? button.textContent : "";
      if (button) {
        button.disabled = true;
        button.textContent = "Agregando...";
      }

      try {
        const response = await fetch(form.action, {
          method: "POST",
          headers: { "X-Requested-With": "XMLHttpRequest" },
          body: new FormData(form),
        });
        const data = await response.json();
        if (data.ok) {
          document.querySelectorAll(".cart-count-badge").forEach((el) => {
            el.textContent = data.count;
            el.classList.remove("bump");
            void el.offsetWidth;
            el.classList.add("bump");
          });
          if (button) button.textContent = "¡Agregado!";
        }
      } catch (err) {
        if (button) button.textContent = "Error, intenta de nuevo";
      } finally {
        setTimeout(() => {
          if (button) {
            button.disabled = false;
            button.textContent = originalText;
          }
        }, 1400);
      }
    });
  });

  document.querySelectorAll(".fav-toggle").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const productId = btn.dataset.productId;
      try {
        const response = await fetch(`/mi-cuenta/favoritos/${productId}/alternar`, {
          method: "POST",
          headers: { "X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCsrfToken() },
        });
        if (response.status === 401) {
          window.location.href = "/cuenta/iniciar-sesion";
          return;
        }
        const data = await response.json();
        btn.classList.toggle("is-active", data.is_favorite);
      } catch (err) {
        /* silencioso */
      }
    });
  });

  document.querySelectorAll(".qty-stepper").forEach((stepper) => {
    const input = stepper.querySelector("input");
    stepper.querySelector(".qty-minus")?.addEventListener("click", () => {
      input.value = Math.max(1, parseInt(input.value || "1", 10) - 1);
    });
    stepper.querySelector(".qty-plus")?.addEventListener("click", () => {
      input.value = parseInt(input.value || "1", 10) + 1;
    });
  });
});
