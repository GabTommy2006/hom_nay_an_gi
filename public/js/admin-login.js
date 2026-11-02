/* An explicitly public UI preview, not an authentication implementation. */
(() => {
  const password = document.getElementById('admin-password');
  document.getElementById('password-toggle').addEventListener('click', event => {
    const show = password.type === 'password'; password.type = show ? 'text' : 'password';
    event.currentTarget.textContent = show ? 'Ẩn' : 'Hiện'; event.currentTarget.setAttribute('aria-pressed', String(show));
  });
  document.getElementById('admin-login-form').addEventListener('submit', event => {
    event.preventDefault(); location.assign('admin.html');
  });
})();
