const year = document.getElementById('year');
if (year) year.textContent = new Date().getFullYear();
document.getElementById('quote')?.addEventListener('submit', event => {
  event.preventDefault();
  const service = document.getElementById('service').value;
  const details = document.getElementById('details').value.trim();
  const message = `Hola, E & V. Quiero solicitar una cotización para ${service.toLowerCase()}.${details ? '\n\n' + details : ''}`;
  window.open('https://wa.me/18299704893?text=' + encodeURIComponent(message), '_blank', 'noopener,noreferrer');
});

const menuToggle = document.querySelector('.menu-toggle');
const mainNav = document.getElementById('main-nav');
function closeMenu() {
  mainNav?.classList.remove('is-open');
  menuToggle?.setAttribute('aria-expanded', 'false');
}
menuToggle?.addEventListener('click', () => {
  const open = menuToggle.getAttribute('aria-expanded') !== 'true';
  menuToggle.setAttribute('aria-expanded', String(open));
  mainNav.classList.toggle('is-open', open);
});
mainNav?.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menuToggle?.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menuToggle.focus();
  }
});

const inquiryForm = document.getElementById('shop-inquiry');
if (inquiryForm) {
  const selection = new Map();
  const cards = [...document.querySelectorAll('.product-card')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  const cart = document.getElementById('cart-items');
  const fields = document.getElementById('cart-fields');
  const feedback = document.getElementById('shop-feedback');
  let feedbackTimer;

  function announce(message) {
    clearTimeout(feedbackTimer);
    feedback.textContent = message;
    feedbackTimer = setTimeout(() => { feedback.textContent = ''; }, 4500);
  }

  function setFilter(category, updateUrl = true) {
    if (!filters.some(button => button.dataset.filter === category)) category = 'todos';
    filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === category)));
    cards.forEach(card => { card.hidden = category !== 'todos' && card.dataset.category !== category; });
    const visible = cards.filter(card => !card.hidden).length;
    document.getElementById('product-count').textContent = `${visible} categorías de productos`;
    if (updateUrl) {
      const url = new URL(location.href);
      if (category === 'todos') url.searchParams.delete('categoria');
      else url.searchParams.set('categoria', category);
      history.replaceState(null, '', url);
    }
  }
  filters.forEach(button => button.addEventListener('click', () => setFilter(button.dataset.filter)));
  setFilter(new URLSearchParams(location.search).get('categoria') || 'todos', false);

  function makeButton(text, label, handler) {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = text;
    button.setAttribute('aria-label', label);
    button.addEventListener('click', handler);
    return button;
  }

  function renderCart(focusName, focusAction) {
    cart.replaceChildren();
    let total = 0;
    selection.forEach((quantity, name) => {
      total += quantity;
      const row = document.createElement('div');
      row.className = 'cart-row';
      const title = document.createElement('h3');
      title.textContent = name;
      const controls = document.createElement('div');
      controls.className = 'cart-controls';
      const output = document.createElement('output');
      output.textContent = quantity;
      output.setAttribute('aria-label', `Cantidad de ${name}`);
      const less = makeButton('−', `Reducir cantidad de ${name}`, () => {
        if (quantity > 1) selection.set(name, quantity - 1);
        renderCart(name, 'less');
      });
      less.disabled = quantity === 1;
      const more = makeButton('+', `Aumentar cantidad de ${name}`, () => {
        if (quantity < 99) selection.set(name, quantity + 1);
        renderCart(name, 'more');
      });
      more.disabled = quantity === 99;
      const remove = makeButton('Quitar', `Quitar ${name}`, () => {
        selection.delete(name);
        renderCart();
        announce(`${name}: eliminado de tu consulta.`);
        const firstButton = cart.querySelector('button:not(:disabled)');
        (firstButton || document.querySelector('.product-add')).focus();
      });
      remove.className = 'remove-item';
      controls.append(less, output, more, remove);
      row.append(title, controls);
      cart.append(row);
      if (focusName === name) {
        const target = focusAction === 'less' ? less : more;
        (target.disabled ? (focusAction === 'less' ? more : less) : target).focus();
      }
    });
    document.querySelectorAll('[data-cart-count]').forEach(el => { el.textContent = total; });
    fields.hidden = !selection.size;
    if (!selection.size) {
      const empty = document.createElement('p');
      empty.className = 'cart-empty';
      empty.textContent = 'Tu consulta está vacía. Añade una categoría de producto para comenzar.';
      cart.append(empty);
    }
  }
  document.querySelectorAll('.product-add').forEach(button => button.addEventListener('click', () => {
    const name = button.dataset.product;
    const quantity = selection.get(name) || 0;
    if (quantity >= 99) { announce('Puedes consultar hasta 99 unidades por categoría. Añade más detalles en tu mensaje.'); return; }
    selection.set(name, quantity + 1);
    renderCart();
    announce(`${name}: añadido a tu consulta.`);
  }));
  inquiryForm.addEventListener('submit', event => {
    event.preventDefault();
    if (!selection.size) return;
    const items = [...selection].map(([name, quantity]) => `• ${name}: ${quantity} unidad(es) aproximada(s)`).join('\n');
    const notes = document.getElementById('shop-notes').value.trim();
    const installation = document.getElementById('include-installation').checked;
    const message = `Hola, E & V. Quiero consultar precios y disponibilidad de:\n\n${items}${notes ? '\n\nDetalles: ' + notes : ''}${installation ? '\n\nTambién quiero consultar la instalación.' : ''}\n\nQuedo pendiente de las referencias disponibles y su cotización.`;
    window.open('https://wa.me/18299704893?text=' + encodeURIComponent(message), '_blank', 'noopener,noreferrer');
  });
}
