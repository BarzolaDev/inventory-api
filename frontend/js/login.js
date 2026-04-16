const form = document.getElementById('loginForm');
    const errorMsg = document.getElementById('errorMsg');
    const submitBtn = document.getElementById('submitBtn');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      errorMsg.classList.add('hidden');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Ingresando...';

      const body = new URLSearchParams({
        username: document.getElementById('email').value,
        password: document.getElementById('password').value,
      });

      try {
        const res = await fetch(`${API_BASE}/users/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body,
        });

        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || 'Credenciales inválidas');
        }

        const { access_token } = await res.json();
        localStorage.setItem('token', access_token);
        window.location.href = 'index.html';

      } catch (err) {
        errorMsg.textContent = err.message;
        errorMsg.classList.remove('hidden');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Entrar';
      }
    });