// Simple auth: localStorage-backed user list + current user
let users = JSON.parse(localStorage.getItem('lemmaticaUsers') || '[]');
let currentUser = null;

const storedEmail = localStorage.getItem('lemmaticaCurrentUserEmail');
if (storedEmail) {
currentUser = users.find(u => u.email === storedEmail) || null;
}

// Account DOM
  const accountLoggedOut   = document.getElementById('accountLoggedOut');
  const accountRegister    = document.getElementById('accountRegister');
  const accountInfo        = document.getElementById('accountInfo');
  const loginForm          = document.getElementById('loginForm');
  const registerForm       = document.getElementById('registerForm');
  const logoutBtn          = document.getElementById('logoutBtn');
  const switchToRegister   = document.getElementById('switchToRegister');
  const switchToLogin      = document.getElementById('switchToLogin');
  const authError          = document.getElementById('authError');
  const infoEmailEl        = document.getElementById('infoEmail');
  const infoUsernameEl     = document.getElementById('infoUsername');
  const infoJoinedEl       = document.getElementById('infoJoined');

  /* =========================================================
    B2) ACCOUNT / AUTH HELPERS
    ========================================================= */

  function saveUsers() {
    localStorage.setItem('lemmaticaUsers', JSON.stringify(users));
  }

  function showError(msg) {
    if (!authError) return;
    authError.textContent = msg;
    authError.classList.remove('d-none');
  }

  function clearError() {
    if (!authError) return;
    authError.textContent = '';
    authError.classList.add('d-none');
  }

  function setCurrentUser(user) {
    currentUser = user;
    if (user) {
      localStorage.setItem('lemmaticaCurrentUserEmail', user.email);
    } else {
      localStorage.removeItem('lemmaticaCurrentUserEmail');
    }
    syncAccountUI();
  }

  // <<< This is the function you asked to update >>>
  function syncAccountUI() {
    clearError();
    const loggedIn = !!currentUser;
    const accountNav = document.getElementById('nav-account-link');

    if (loggedIn) {
      // Show account info card
      accountLoggedOut.classList.add('d-none');
      accountRegister.classList.add('d-none');
      accountInfo.classList.remove('d-none');

      // Fill details
      infoEmailEl.textContent = currentUser.email;
      infoUsernameEl.textContent = currentUser.username;
      infoJoinedEl.textContent = new Date(currentUser.joinedAt).toLocaleDateString();

      // Navbar label: "Signed in as X"
      if (accountNav) {
        accountNav.textContent = `Signed in as ${currentUser.username}`;
      }
    } else {
      // Show login form by default
      accountLoggedOut.classList.remove('d-none');
      accountRegister.classList.add('d-none');
      accountInfo.classList.add('d-none');

      // Navbar label back to "Account"
      if (accountNav) {
        accountNav.textContent = 'Account';
      }
    }
  }

/* =========================================================
  LOGIN (backend POST)
  ========================================================= */


if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (authError) authError.classList.add("d-none");

        const email = document.getElementById("loginEmail").value.trim();
        const password = document.getElementById("loginPassword").value.trim();

        try {
            const res = await fetch("/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
                credentials: "same-origin"
            });

            const data = await res.json();

            if (res.ok) {
                // Success → redirect to backend-specified location
                window.location.href = data.redirect || "/";
            } else {
                if (authError) {
                    authError.textContent = data.error || "Login failed";
                    authError.classList.remove("d-none");
                } else {
                    alert(data.error || "Login failed");
                }
            }
        } catch (err) {
            if (authError) {
                authError.textContent = "Network error, please try again.";
                authError.classList.remove("d-none");
            } else {
                alert("Network error, please try again.");
            }
            console.error(err);
        }
    });
}


  // Register submit
  if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
      e.preventDefault();
      clearError();

      const email = document.getElementById('regEmail').value.trim().toLowerCase();
      const username = document.getElementById('regUsername').value.trim();
      const password = document.getElementById('regPassword').value;
      const confirm  = document.getElementById('regConfirm').value;

      if (!email || !username || !password) {
        showError('Please fill in all fields.');
        return;
      }
      if (password !== confirm) {
        showError('Passwords do not match.');
        return;
      }
      if (users.some(u => u.email === email)) {
        showError('An account with that email already exists.');
        return;
      }

      const user = {
        email,
        username,
        password,
        joinedAt: Date.now()
      };
      users.push(user);
      saveUsers();
      registerForm.reset();
      setCurrentUser(user);
    });
  }

  // Switch between login and register
  switchToRegister?.addEventListener('click', (e) => {
    e.preventDefault();
    clearError();
    accountLoggedOut.classList.add('d-none');
    accountRegister.classList.remove('d-none');
  });

  switchToLogin?.addEventListener('click', (e) => {
    e.preventDefault();
    clearError();
    accountRegister.classList.add('d-none');
    accountLoggedOut.classList.remove('d-none');
  });

  // Logout
  logoutBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    setCurrentUser(null);
  });

    syncAccountUI(); // reflect login state on load
