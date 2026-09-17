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
