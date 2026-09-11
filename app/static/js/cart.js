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
