const token = localStorage.getItem('token');
if (!token) window.location.href = 'login.html';

document.getElementById('logoutBtn').addEventListener('click', () => {
  localStorage.removeItem('token');
  window.location.href = 'login.html';
});
