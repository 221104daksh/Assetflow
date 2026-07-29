(function () {
  "use strict";

  // ---------- Dark mode ----------
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("af-theme", theme);
  }

  window.AF_toggleDarkMode = function () {
    const current = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);

    fetch("/auth/toggle-dark-mode", {
      method: "POST",
      headers: { "X-CSRFToken": window.AF_CSRF_TOKEN || "" },
    }).catch(() => {});
  };

  // ---------- Sidebar (mobile) ----------
  window.AF_toggleSidebar = function () {
    const sidebar = document.querySelector(".af-sidebar");
    if (sidebar) sidebar.classList.toggle("af-sidebar-open");
  };

  // ---------- Confirm dialogs ----------
  document.addEventListener("click", function (e) {
    const trigger = e.target.closest("[data-af-confirm]");
    if (!trigger) return;
    const message = trigger.getAttribute("data-af-confirm") || "Are you sure?";
    if (!window.confirm(message)) {
      e.preventDefault();
      e.stopPropagation();
    }
  });

  // ---------- Toasts (Bootstrap) ----------
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".af-toast").forEach(function (el) {
      if (window.bootstrap && window.bootstrap.Toast) {
        new window.bootstrap.Toast(el, { delay: 4500 }).show();
      }
    });

    // Auto-highlight active nav link
    document.querySelectorAll(".af-nav-link").forEach(function (link) {
      if (link.dataset.active === "true") link.classList.add("active");
    });
  });
})();
