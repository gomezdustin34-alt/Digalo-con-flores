document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector(".admin-sidebar");
  document.querySelector(".sidebar-toggle")?.addEventListener("click", () => {
    sidebar?.classList.toggle("is-open");
  });

  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      if (!confirm(form.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  // Botones (no formularios) que piden confirmar antes de enviar. Sirve para
  // acciones como "eliminar esta imagen", que viven dentro de un formulario
  // mayor y usan su propio formaction.
  document.querySelectorAll("button[data-confirm]").forEach((boton) => {
    boton.addEventListener("click", (e) => {
      if (!confirm(boton.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  document.querySelectorAll(".auto-submit-select").forEach((select) => {
    select.addEventListener("change", () => select.form?.submit());
  });
});

// ---- Aviso sonoro de notificaciones nuevas ----
// Cada medio minuto se pregunta cuantas hay sin leer. Si subieron desde la
// ultima consulta, se actualiza el punto rojo y suena una campanita corta.
document.addEventListener("DOMContentLoaded", () => {
  const campana = document.querySelector('.admin-topbar-right a[aria-label="Notificaciones"]');
  if (!campana) return;

  const CLAVE = "notificaciones_vistas";
  let anterior = parseInt(campana.querySelector(".icon-badge")?.textContent || "0", 10);
  try {
    const guardado = sessionStorage.getItem(CLAVE);
    if (guardado !== null) anterior = Math.max(anterior, parseInt(guardado, 10) || 0);
  } catch (e) {
    /* sin almacenamiento: se sigue igual, solo que no recuerda entre paginas */
  }

  function sonar() {
    // Se sintetiza el sonido en el navegador: no hace falta descargar ningun
    // archivo y no hay nada que se pueda quedar sin cargar.
    try {
      const Audio = window.AudioContext || window.webkitAudioContext;
      if (!Audio) return;
      const ctx = new Audio();
      [880, 1320].forEach((frecuencia, i) => {
        const osc = ctx.createOscillator();
        const vol = ctx.createGain();
        osc.type = "sine";
        osc.frequency.value = frecuencia;
        const inicio = ctx.currentTime + i * 0.16;
        vol.gain.setValueAtTime(0.0001, inicio);
        vol.gain.exponentialRampToValueAtTime(0.22, inicio + 0.02);
        vol.gain.exponentialRampToValueAtTime(0.0001, inicio + 0.3);
        osc.connect(vol).connect(ctx.destination);
        osc.start(inicio);
        osc.stop(inicio + 0.32);
      });
      setTimeout(() => ctx.close(), 1200);
    } catch (e) {
      /* el navegador puede bloquear el audio hasta que haya un clic; no pasa nada */
    }
  }

  function pintar(cuantas) {
    let punto = campana.querySelector(".icon-badge");
    if (cuantas > 0) {
      if (!punto) {
        punto = document.createElement("span");
        punto.className = "icon-badge";
        campana.appendChild(punto);
      }
      punto.textContent = cuantas;
    } else if (punto) {
      punto.remove();
    }
  }

  async function revisar() {
    try {
      const r = await fetch("/admin/notificaciones/contador", {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!r.ok) return;
      const { sin_leer: cuantas } = await r.json();
      if (cuantas > anterior) {
        sonar();
        campana.classList.add("suena");
        setTimeout(() => campana.classList.remove("suena"), 1200);
      }
      pintar(cuantas);
      anterior = cuantas;
      try {
        sessionStorage.setItem(CLAVE, String(cuantas));
      } catch (e) {
        /* sin almacenamiento */
      }
    } catch (e) {
      /* la red fallo: se reintenta en la siguiente vuelta */
    }
  }

  setInterval(revisar, 30000);
});

// ---- Selección múltiple en las listas del panel ----
// La casilla del encabezado marca todas las de la página; la barra de acciones
// aparece sola en cuanto hay algo marcado y dice cuántos son.
document.addEventListener("DOMContentLoaded", () => {
  const barra = document.getElementById("barra-lote");
  const casillas = Array.from(document.querySelectorAll(".marca-pedido"));
  if (!casillas.length) return;

  // Hay dos "seleccionar todos": el de la cabecera de la tabla y el rotulado
  // de arriba. Van sincronizados, marque el que marque.
  const maestras = ["marcar-todos", "marcar-todos-visible"]
    .map((id) => document.getElementById(id))
    .filter(Boolean);
  const bloqueGlobal = document.getElementById("marcar-global");
  const todasLasPaginas = document.getElementById("marcar-todas-paginas");

  function refrescar() {
    const marcadas = casillas.filter((c) => c.checked);
    const todasMarcadas = marcadas.length === casillas.length && casillas.length > 0;

    if (barra) {
      barra.hidden = marcadas.length === 0;
      const contador = barra.querySelector("[data-seleccionados]");
      if (contador) {
        contador.textContent = todasLasPaginas?.checked
          ? todasLasPaginas.dataset.total || marcadas.length
          : marcadas.length;
      }
    }
    maestras.forEach((m) => {
      m.checked = todasMarcadas;
      m.indeterminate = marcadas.length > 0 && !todasMarcadas;
    });

    // La opcion de abarcar todas las paginas solo tiene sentido cuando ya
    // marcaste todo lo de esta.
    if (bloqueGlobal) {
      bloqueGlobal.hidden = !todasMarcadas;
      if (!todasMarcadas && todasLasPaginas) todasLasPaginas.checked = false;
    }
  }

  maestras.forEach((m) =>
    m.addEventListener("change", () => {
      casillas.forEach((c) => {
        c.checked = m.checked;
      });
      refrescar();
    })
  );
  casillas.forEach((c) => c.addEventListener("change", refrescar));
  todasLasPaginas?.addEventListener("change", refrescar);
  refrescar();

  // Confirmación antes de un borrado en lote, diciendo cuántos son.
  document.querySelectorAll("[data-confirm-lote]").forEach((boton) => {
    boton.addEventListener("click", (e) => {
      const global = document.getElementById("marcar-todas-paginas");
      const cuantos = global?.checked
        ? parseInt(global.dataset.total || "0", 10) || casillas.filter((c) => c.checked).length
        : casillas.filter((c) => c.checked).length;
      if (!cuantos) {
        e.preventDefault();
        return;
      }
      const mensaje = boton.dataset.confirmLote.replace(
        "los pedidos seleccionados",
        cuantos === 1 ? "el pedido seleccionado" : `los ${cuantos} pedidos seleccionados`
      );
      if (!confirm(mensaje)) e.preventDefault();
    });
  });
});
