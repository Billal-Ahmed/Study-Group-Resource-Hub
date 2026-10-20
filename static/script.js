/* Client-side validation and UI behaviour */

"use strict";

// ── Bootstrap form validation ─────────────────────────────────────────────

(function () {
  const forms = document.querySelectorAll(
    "#register-form, #login-form, #create-group-form, #resource-form, #deadline-form"
  );

  forms.forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
      }
      form.classList.add("was-validated");
    });
  });
})();


// ── Password confirmation check (register page only) ──────────────────────

(function () {
  const pw  = document.getElementById("password");
  const cfm = document.getElementById("confirmation");
  if (!pw || !cfm) return;

  function validateMatch() {
    if (cfm.value && pw.value !== cfm.value) {
      cfm.setCustomValidity("Passwords do not match.");
    } else {
      cfm.setCustomValidity("");
    }
  }

  pw.addEventListener("input", validateMatch);
  cfm.addEventListener("input", validateMatch);
})();


// ── Resource-type placeholder hint ────────────────────────────────────────

(function () {
  const sel   = document.getElementById("resource-type-sel");
  const input = document.getElementById("link-or-note-input");
  if (!sel || !input) return;

  sel.addEventListener("change", function () {
    if (sel.value === "link") {
      input.placeholder = "Paste a URL (https://…)";
    } else {
      input.placeholder = "Write your note here…";
    }
  });
})();


// ── Confirmation modal for destructive actions ────────────────────────────

(function () {
  const modal   = document.getElementById("confirmModal");
  if (!modal) return;

  const bsModal     = new bootstrap.Modal(modal);
  const label       = document.getElementById("confirmModalLabel");
  const actionBtn   = document.getElementById("confirm-action-btn");

  let pendingForm = null;

  // Any submit button with data-confirm triggers the modal instead of submitting
  document.querySelectorAll("[data-confirm]").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      pendingForm = btn.closest("form");
      label.textContent = btn.dataset.confirm;
      bsModal.show();
    });
  });

  actionBtn.addEventListener("click", function () {
    bsModal.hide();
    if (pendingForm) {
      pendingForm.submit();
      pendingForm = null;
    }
  });

  modal.addEventListener("hidden.bs.modal", function () {
    pendingForm = null;
  });
})();
