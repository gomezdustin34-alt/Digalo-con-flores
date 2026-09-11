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

  document.querySelectorAll(".auto-submit-select").forEach((select) => {
    select.addEventListener("change", () => select.form?.submit());
  });
});
