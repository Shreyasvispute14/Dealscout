// Login page: POST credentials to /api/auth/login, then return to the insights view.
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#login-form");
  const errorBox = document.querySelector("#login-error");
  const submit = document.querySelector("#login-submit");
  const label = document.querySelector("#login-submit-label");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorBox.classList.add("hidden");
    submit.disabled = true;
    label.textContent = "Signing in…";
    try {
      await api("/auth/login", {
        method: "POST",
        body: {
          email: document.querySelector("#login-email").value,
          password: document.querySelector("#login-password").value,
        },
      });
      window.location.href = "/#insights";
    } catch (error) {
      console.warn("Login failed:", error.message);
      errorBox.classList.remove("hidden");
    } finally {
      submit.disabled = false;
      label.textContent = "Sign in";
    }
  });
});
