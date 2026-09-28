document.getElementById('year').textContent = new Date().getFullYear();
document.querySelectorAll('[data-service]').forEach(link => link.addEventListener('click', () => { document.getElementById('service').value = link.dataset.service; }));
document.getElementById('quote').addEventListener('submit', event => {
  event.preventDefault();
  const service = document.getElementById('service').value;
  const details = document.getElementById('details').value.trim();
  const message = `Hola, E & V. Quiero solicitar una cotización para ${service.toLowerCase()}.${details ? '\n\n' + details : ''}`;
  window.open('https://wa.me/18299704893?text=' + encodeURIComponent(message), '_blank', 'noopener,noreferrer');
});
