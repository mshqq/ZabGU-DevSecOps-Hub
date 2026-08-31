document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('login-form');
  const errorBlock = document.getElementById('login-error');

  form.addEventListener('submit', async function (event) {
    event.preventDefault();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!email || !password) {
      showError('Пожалуйста, заполните все поля');
      return;
    }

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        window.location.href = '/';
      } else {
        const errorMsg =
          data.error || 'Ошибка входа. Проверьте email и пароль.';
        showError(errorMsg);
      }
    } catch (error) {
      showError('Не удалось соединиться с сервером. Проверьте интернет.');
      console.error('Fetch error:', error);
    }
  });

  function showError(message) {
    errorBlock.textContent = message;
    errorBlock.classList.remove('hidden');
  }
});
