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

  // Login submit
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      clearError();

      const email = document.getElementById('loginEmail').value.trim().toLowerCase();
      const password = document.getElementById('loginPassword').value;

      const user = users.find(u => u.email === email);
      if (!user || user.password !== password) {
        showError('Incorrect email or password.');
        return;
      }

      setCurrentUser(user);
      loginForm.reset();
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