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

  // Auto-cierre de flash messages
  document.querySelectorAll(".flash").forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity 0.4s ease";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 400);
    }, 4500);
  });
});

// Comportamientos que antes vivian en atributos onclick/onchange del HTML.
// Se movieron aqui para que la pagina pueda declarar una CSP estricta: con
// ella, el navegador ignora cualquier script incrustado en los atributos.
document.addEventListener("DOMContentLoaded", () => {
  // Galería del producto: la miniatura cambia la imagen grande
  const principal = document.getElementById("main-product-image");
  document.querySelectorAll(".galeria-mini").forEach((mini) => {
    mini.addEventListener("click", () => {
      if (principal) principal.src = mini.src;
      mini.parentNode.querySelectorAll("img").forEach((i) => i.classList.remove("active"));
      mini.classList.add("active");
    });
  });

  // Botón redondo de las tarjetas: envía el formulario de su propia tarjeta
  document.querySelectorAll(".add-cart-round").forEach((boton) => {
    boton.addEventListener("click", () => {
      boton.closest(".product-card")?.querySelector(".add-to-cart-form")?.requestSubmit();
    });
  });

  // Selectores que recargan la página al cambiar (ordenar el catálogo)
  document.querySelectorAll(".auto-submit-select").forEach((select) => {
    select.addEventListener("change", () => select.form?.submit());
  });
});

function mostrarAviso(texto) {
  document.querySelector(".toast")?.remove();
  const aviso = document.createElement("div");
  aviso.className = "toast";
  aviso.setAttribute("role", "status");
  aviso.innerHTML =
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">' +
    '<circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v4h1"/></svg>';
  aviso.appendChild(document.createTextNode(texto));
  document.body.appendChild(aviso);
  setTimeout(() => aviso.remove(), 5000);
}

function getCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]')?.content || "";
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".add-to-cart-form").forEach((form) => {
    // "Comprar ahora" debe viajar como envio normal: el servidor agrega al
    // carrito y redirige al checkout. Si lo interceptaramos por AJAX, el
    // navegador se quedaria en la pagina del producto.
    const botonComprar = form.querySelector(".btn-comprar");
    if (botonComprar) {
      botonComprar.addEventListener("click", () => {
        form.dataset.comprar = "1";
      });
    }

    form.addEventListener("submit", async (e) => {
      if (form.dataset.comprar === "1") {
        delete form.dataset.comprar;
        return;
      }
      e.preventDefault();
      const button = form.querySelector("button[type=submit]:not(.btn-comprar)");
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
      if (btn.dataset.enviando === "1") return;
      btn.dataset.enviando = "1";

      try {
        const response = await fetch(`/mi-cuenta/favoritos/${productId}/alternar`, {
          method: "POST",
          headers: { "X-Requested-With": "XMLHttpRequest", "X-CSRFToken": getCsrfToken() },
        });

        // Sin sesion: se avisa y despues se lleva al login, de donde volvera
        // a esta misma pagina.
        if (response.status === 401 || response.redirected) {
          const volverA = window.location.pathname + window.location.search;
          mostrarAviso("Inicia sesión para guardar tus favoritos.");
          setTimeout(() => {
            window.location.href = "/cuenta/iniciar-sesion?next=" + encodeURIComponent(volverA);
          }, 1600);
          return;
        }

        const data = await response.json();
        btn.classList.toggle("is-active", data.is_favorite);
      } catch (err) {
        /* silencioso */
      } finally {
        delete btn.dataset.enviando;
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
