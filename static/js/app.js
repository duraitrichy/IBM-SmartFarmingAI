/**
 * app.js — SmartFarmingAI global JavaScript
 * Dark mode toggle, active nav highlighting, utils
 */

(function () {
  "use strict";

  // ── Dark Mode ─────────────────────────────────────────────────
  const DARK_KEY = "sfa_dark";
  const html = document.documentElement;
  const toggleBtn = document.getElementById("darkToggle");

  function applyDark(on) {
    html.setAttribute("data-bs-theme", on ? "dark" : "light");
    if (toggleBtn) {
      toggleBtn.innerHTML = on
        ? '<i class="bi bi-sun"></i>'
        : '<i class="bi bi-moon-stars"></i>';
    }
    localStorage.setItem(DARK_KEY, on ? "1" : "0");
  }

  // Restore preference
  applyDark(localStorage.getItem(DARK_KEY) === "1");

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      applyDark(html.getAttribute("data-bs-theme") !== "dark");
    });
  }

  // ── Active nav link ───────────────────────────────────────────
  const path = window.location.pathname;
  document.querySelectorAll(".navbar-nav .nav-link").forEach((link) => {
    if (link.getAttribute("href") === path) {
      link.classList.add("active");
    }
  });

  // ── Auto-dismiss alerts after 5s ──────────────────────────────
  document.querySelectorAll(".alert.alert-dismissible").forEach((el) => {
    setTimeout(() => {
      try {
        bootstrap.Alert.getOrCreateInstance(el).close();
      } catch (_) {}
    }, 5000);
  });

  // ── Tooltips ──────────────────────────────────────────────────
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
    new bootstrap.Tooltip(el);
  });

  // ── Format numbers with commas ────────────────────────────────
  window.formatNum = function (n) {
    if (n == null) return "—";
    return Number(n).toLocaleString("en-IN");
  };

  // ── Show toast notification ───────────────────────────────────
  window.showToast = function (message, type = "success") {
    const existing = document.getElementById("sfa-toast-container");
    if (!existing) {
      const div = document.createElement("div");
      div.id = "sfa-toast-container";
      div.className = "position-fixed bottom-0 end-0 p-3";
      div.style.zIndex = 9999;
      document.body.appendChild(div);
    }
    const id = "toast-" + Date.now();
    const el = document.createElement("div");
    el.id = id;
    el.className = `toast align-items-center text-bg-${type} border-0`;
    el.setAttribute("role", "alert");
    el.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>`;
    document.getElementById("sfa-toast-container").appendChild(el);
    const t = new bootstrap.Toast(el, { delay: 3500 });
    t.show();
    el.addEventListener("hidden.bs.toast", () => el.remove());
  };

  // ── Confirm delete ────────────────────────────────────────────
  document.querySelectorAll("[data-confirm]").forEach((el) => {
    el.addEventListener("click", (e) => {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });

})();
