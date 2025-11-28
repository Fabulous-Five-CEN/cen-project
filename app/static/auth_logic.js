const accountLoggedOut = document.getElementById("accountLoggedOut");
const accountRegister = document.getElementById("accountRegister");
const accountInfo = document.getElementById("accountInfo");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const logoutBtn = document.getElementById("logoutBtn");
const switchToRegister = document.getElementById("switchToRegister");
const switchToLogin = document.getElementById("switchToLogin");
const authError = document.getElementById("authError");
const infoEmailEl = document.getElementById("infoEmail");
const infoUsernameEl = document.getElementById("infoUsername");
const infoJoinedEl = document.getElementById("infoJoined");

let currentUser = window.currentUser || null;
const urlParams = new URLSearchParams(window.location.search);
const nextParam = urlParams.get("next");

function showError(msg) {
  if (!authError) return;
  authError.textContent = msg;
  authError.classList.remove("d-none");
}

function clearError() {
  if (!authError) return;
  authError.textContent = "";
  authError.classList.add("d-none");
}

function formatDate(value) {
  if (!value) return "";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? "" : parsed.toLocaleDateString();
}

function syncAccountUI() {
  clearError();
  const loggedIn = !!currentUser;
  const accountNav = document.getElementById("nav-account-link");

  if (loggedIn) {
    accountLoggedOut?.classList.add("d-none");
    accountRegister?.classList.add("d-none");
    accountInfo?.classList.remove("d-none");

    if (infoEmailEl) infoEmailEl.textContent = currentUser.email || "";
    if (infoUsernameEl) infoUsernameEl.textContent = currentUser.display_name || "";
    if (infoJoinedEl) infoJoinedEl.textContent = formatDate(currentUser.created_at);

    if (accountNav) {
      const label = currentUser.display_name || currentUser.email || "Account";
      accountNav.textContent = `Signed in as ${label}`;
    }
  } else {
    accountLoggedOut?.classList.remove("d-none");
    accountRegister?.classList.add("d-none");
    accountInfo?.classList.add("d-none");

    if (accountNav) {
      accountNav.textContent = "Account";
    }
  }
}

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError();

    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();

    try {
      const res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({ email, password, next: nextParam }),
      });

      const data = await res.json();
      if (!res.ok) {
        showError(data.error || "Login failed.");
        return;
      }

      currentUser = data.user || null;
      window.location.href = data.redirect || "/";
    } catch (err) {
      console.error(err);
      showError("Network error, please try again.");
    }
  });
}

if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError();

    const email = document.getElementById("regEmail").value.trim().toLowerCase();
    const displayName = document.getElementById("regUsername").value.trim();
    const password = document.getElementById("regPassword").value;
    const confirm = document.getElementById("regConfirm").value;

    if (!email || !displayName || !password) {
      showError("Please fill in all fields.");
      return;
    }
    if (password !== confirm) {
      showError("Passwords do not match.");
      return;
    }

    try {
      const res = await fetch("/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({
          email,
          display_name: displayName,
          password,
          next: nextParam,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        showError(data.error || "Registration failed.");
        return;
      }

      currentUser = data.user || null;
      window.location.href = data.redirect || "/";
    } catch (err) {
      console.error(err);
      showError("Network error, please try again.");
    }
  });
}

switchToRegister?.addEventListener("click", (e) => {
  e.preventDefault();
  clearError();
  accountLoggedOut?.classList.add("d-none");
  accountRegister?.classList.remove("d-none");
});

switchToLogin?.addEventListener("click", (e) => {
  e.preventDefault();
  clearError();
  accountRegister?.classList.add("d-none");
  accountLoggedOut?.classList.remove("d-none");
});

logoutBtn?.addEventListener("click", async (e) => {
  e.preventDefault();
  clearError();

  try {
    const res = await fetch("/auth/logout", {
      method: "POST",
      credentials: "same-origin",
    });
    if (res.ok) {
      const data = await res.json();
      currentUser = null;
      syncAccountUI();
      window.location.href = data.redirect || "/auth/login";
      return;
    }
    showError("Logout failed. Please try again.");
  } catch (err) {
    console.error(err);
    showError("Network error, please try again.");
  }
});

syncAccountUI();
