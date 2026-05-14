/* =========================================
   COUPONSTORE — Main App Script
   Connects to FastAPI backend at /api/v1
   ========================================= */

const API = 'http://127.0.0.1:8000/api/v1';
const PAGE_SIZE = 12;

// ── State ──────────────────────────────────
let state = {
  token: localStorage.getItem('cs_token') || null,
  user: JSON.parse(localStorage.getItem('cs_user') || 'null'),
  cart: JSON.parse(localStorage.getItem('cs_cart') || '[]'),
  products: [],
  allProducts: [],
  coupons: [],
  page: 1,
  totalProducts: 0,
  appliedCoupon: null,
  discountAmount: 0,
};

// ── API helpers ────────────────────────────
async function apiFetch(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (state.token) headers['Authorization'] = `Bearer ${state.token}`;
  const res = await fetch(`${API}${path}`, { ...options, headers });
  if (res.status === 401) { logout(); return null; }
  return res;
}

async function apiGet(path) {
  const r = await apiFetch(path);
  if (!r || !r.ok) return null;
  return r.json();
}

async function apiPost(path, body) {
  const r = await apiFetch(path, { method: 'POST', body: JSON.stringify(body) });
  return r;
}

// ── Auth ───────────────────────────────────
function saveAuth(token, user) {
  state.token = token;
  state.user = user;
  localStorage.setItem('cs_token', token);
  localStorage.setItem('cs_user', JSON.stringify(user));
}

function logout() {
  state.token = null;
  state.user = null;
  localStorage.removeItem('cs_token');
  localStorage.removeItem('cs_user');
  showAuth();
}

function showAuth() {
  document.getElementById('auth-overlay').style.display = 'flex';
}

function hideAuth() {
  document.getElementById('auth-overlay').style.display = 'none';
}

// ── Toast ──────────────────────────────────
let toastTimer;
function showToast(msg, type = 'info') {
  const toast = document.getElementById('toast');
  const icon = document.getElementById('toast-icon');
  const msgEl = document.getElementById('toast-msg');
  const icons = { success: '✓', error: '✕', info: 'ℹ' };
  const colors = { success: '#4ade80', error: '#f87171', info: '#e8c547' };
  icon.textContent = icons[type];
  icon.style.color = colors[type];
  msgEl.textContent = msg;
  toast.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.add('hidden'), 3500);
}

// ── Cart ───────────────────────────────────
function saveCart() { localStorage.setItem('cs_cart', JSON.stringify(state.cart)); }

function addToCart(product, e) {
  if (e) e.stopPropagation();
  if (product.stock === 0) { showToast('Out of stock', 'error'); return; }
  const existing = state.cart.find(i => i.id === product.id);
  if (existing) {
    if (existing.qty >= product.stock) { showToast('Max stock reached', 'error'); return; }
    existing.qty++;
  } else {
    state.cart.push({ id: product.id, name: product.name, price: parseFloat(product.price), stock: product.stock, qty: 1 });
  }
  saveCart();
  renderCartCount();
  renderCart();
  showToast(`${product.name} added to cart`, 'success');
}

function removeFromCart(id) {
  state.cart = state.cart.filter(i => i.id !== id);
  saveCart();
  resetCoupon();
  renderCart();
  renderCartCount();
}

function changeQty(id, delta) {
  const item = state.cart.find(i => i.id === id);
  if (!item) return;
  item.qty = Math.max(1, Math.min(item.stock, item.qty + delta));
  saveCart();
  resetCoupon();
  renderCart();
}

function cartTotal() {
  return state.cart.reduce((s, i) => s + i.price * i.qty, 0);
}

function renderCartCount() {
  const total = state.cart.reduce((s, i) => s + i.qty, 0);
  document.getElementById('cart-count').textContent = total;
}

function renderCart() {
  const container = document.getElementById('cart-items');
  const footer = document.getElementById('cart-footer');
  if (state.cart.length === 0) {
    container.innerHTML = `<div class="cart-empty"><svg width="48" height="48" viewBox="0 0 24 24" fill="none"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4zM3 6h18M16 10a4 4 0 01-8 0" stroke="currentColor" stroke-width="1.5"/></svg><p>Your cart is empty</p></div>`;
    footer.style.display = 'none';
    return;
  }
  footer.style.display = 'flex';
  container.innerHTML = state.cart.map(item => `
    <div class="cart-item">
      <div class="cart-item-info">
        <div class="cart-item-name">${item.name}</div>
        <div class="cart-item-price">$${(item.price * item.qty).toFixed(2)}</div>
        <div class="cart-item-controls">
          <button class="qty-btn" onclick="changeQty(${item.id}, -1)">−</button>
          <span class="qty-num">${item.qty}</span>
          <button class="qty-btn" onclick="changeQty(${item.id}, 1)">+</button>
          <button class="remove-item" onclick="removeFromCart(${item.id})">Remove</button>
        </div>
      </div>
    </div>
  `).join('');
  updateTotals();
  loadRecommendations();
}

function updateTotals() {
  const sub = cartTotal();
  const disc = state.discountAmount;
  const total = Math.max(0, sub - disc);
  document.getElementById('subtotal-display').textContent = `$${sub.toFixed(2)}`;
  document.getElementById('total-display').textContent = `$${total.toFixed(2)}`;
  const discRow = document.getElementById('discount-row');
  if (disc > 0) {
    discRow.classList.remove('hidden');
    document.getElementById('discount-display').textContent = `-$${disc.toFixed(2)}`;
  } else {
    discRow.classList.add('hidden');
  }
}

function resetCoupon() {
  state.appliedCoupon = null;
  state.discountAmount = 0;
  document.getElementById('checkout-coupon-code').value = '';
  document.getElementById('coupon-feedback').className = 'coupon-feedback hidden';
  updateTotals();
}

// ── Recommendations ────────────────────────
async function loadRecommendations() {
  const sub = cartTotal();
  if (sub === 0) return;
  const strip = document.getElementById('recommend-strip');
  const list = document.getElementById('recommend-list');
  try {
    const data = await apiGet(`/coupons/recommend?order_value=${sub.toFixed(2)}&limit=3`);
    if (!data || data.length === 0) { strip.classList.add('hidden'); return; }
    strip.classList.remove('hidden');
    list.innerHTML = data.map(c => {
      const label = c.discount_type === 'PERCENT'
        ? `Save ${c.discount_value}%${c.max_discount_amount ? ` (max $${c.max_discount_amount})` : ''}`
        : `Save $${c.discount_value}`;
      return `<div class="recommend-chip" onclick="applyRecommendedCode('${c.code}')">
        <span class="chip-code">${c.code}</span>
        <span class="chip-val">${label}</span>
      </div>`;
    }).join('');
  } catch (_) { strip.classList.add('hidden'); }
}

function applyRecommendedCode(code) {
  document.getElementById('checkout-coupon-code').value = code;
  applyCoupon();
}

// ── Apply Coupon ───────────────────────────
async function applyCoupon() {
  const code = document.getElementById('checkout-coupon-code').value.trim().toUpperCase();
  const fb = document.getElementById('coupon-feedback');
  if (!code) return;
  const sub = cartTotal();
  if (sub === 0) { showToast('Add items to cart first', 'error'); return; }
  fb.className = 'coupon-feedback';
  fb.textContent = 'Validating...';
  try {
    const r = await apiFetch('/coupons/validate', {
      method: 'POST',
      body: JSON.stringify({ code, order_value: sub })
    });
    const data = await r.json();
    if (r.ok && data.is_valid) {
      state.appliedCoupon = data;
      state.discountAmount = data.discount_amount;
      fb.className = 'coupon-feedback success';
      fb.textContent = `✓ Code applied! You save $${data.discount_amount.toFixed(2)}`;
      updateTotals();
    } else {
      state.discountAmount = 0;
      fb.className = 'coupon-feedback error';
      fb.textContent = data.detail || data.error_message || 'Invalid coupon code';
      updateTotals();
    }
  } catch (e) {
    fb.className = 'coupon-feedback error';
    fb.textContent = 'Could not validate coupon. Check connection.';
  }
}

// ── Private code preview ───────────────────
async function checkPrivateCode() {
  const code = document.getElementById('private-code-input').value.trim().toUpperCase();
  const result = document.getElementById('private-result');
  if (!code) return;
  result.className = 'private-result';
  result.textContent = 'Checking...';
  result.classList.remove('hidden');
  const sub = cartTotal() || 100; // preview with $100 if cart empty
  try {
    const r = await apiFetch('/coupons/validate', {
      method: 'POST',
      body: JSON.stringify({ code, order_value: sub })
    });
    const data = await r.json();
    if (r.ok && data.is_valid) {
      result.className = 'private-result success';
      const discLabel = data.discount_type === 'PERCENT'
        ? `${data.discount_value}% off`
        : `$${data.discount_value} off`;
      result.innerHTML = `<div class="result-title">✓ Valid code: ${code}</div>
        <div class="result-detail">${discLabel} — saves $${data.discount_amount.toFixed(2)} on a $${sub.toFixed(2)} order. Add to cart and apply at checkout.</div>`;
    } else {
      result.className = 'private-result error';
      result.innerHTML = `<div class="result-title">✕ Invalid code</div>
        <div class="result-detail">${data.detail || data.error_message || 'This code does not exist or has expired.'}</div>`;
    }
  } catch (_) {
    result.className = 'private-result error';
    result.textContent = 'Could not validate. Check your connection.';
  }
}

// ── Products ───────────────────────────────
function productEmoji(name) {
  const n = name.toLowerCase();
  if (n.includes('phone') || n.includes('mobile')) return '📱';
  if (n.includes('laptop') || n.includes('computer')) return '💻';
  if (n.includes('head') || n.includes('ear')) return '🎧';
  if (n.includes('watch')) return '⌚';
  if (n.includes('camera')) return '📷';
  if (n.includes('shoe') || n.includes('sneaker')) return '👟';
  if (n.includes('bag') || n.includes('pack')) return '🎒';
  if (n.includes('book')) return '📚';
  if (n.includes('game')) return '🎮';
  if (n.includes('shirt') || n.includes('cloth')) return '👕';
  return '🛍️';
}

function sortProducts(products, sort) {
  const arr = [...products];
  if (sort === 'price-asc') arr.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
  else if (sort === 'price-desc') arr.sort((a, b) => parseFloat(b.price) - parseFloat(a.price));
  else if (sort === 'name-asc') arr.sort((a, b) => a.name.localeCompare(b.name));
  return arr;
}

async function loadProducts(page = 1) {
  const grid = document.getElementById('products-grid');
  grid.innerHTML = `<div class="skeleton-grid">${'<div class="skeleton-card"></div>'.repeat(6)}</div>`;
  const skip = (page - 1) * PAGE_SIZE;
  const data = await apiGet(`/products/?skip=${skip}&limit=${PAGE_SIZE}`);
  if (!data) { grid.innerHTML = '<div class="empty-state"><h3>Failed to load products</h3><p>Check your backend connection</p></div>'; return; }
  state.allProducts = data.items;
  state.totalProducts = data.total;
  state.page = page;
  renderProducts();
  renderPagination(data.total);
}

function renderProducts() {
  const sort = document.getElementById('sort-select').value;
  const sorted = sortProducts(state.allProducts, sort);
  const grid = document.getElementById('products-grid');
  if (sorted.length === 0) {
    grid.innerHTML = '<div class="empty-state"><h3>No products found</h3><p>Check back later for new items.</p></div>';
    return;
  }
  grid.innerHTML = sorted.map(p => `
    <div class="product-card" onclick="openProductModal(${p.id})">
      <div class="product-thumb">
        <span>${productEmoji(p.name)}</span>
        <div class="product-badge ${p.stock > 0 ? 'badge-in' : 'badge-out'}">${p.stock > 0 ? 'In Stock' : 'Out of Stock'}</div>
      </div>
      <div class="product-body">
        <div class="product-name">${p.name}</div>
        <div class="product-desc">${p.description || 'No description available.'}</div>
        <div class="product-footer">
          <div>
            <div class="product-price">$${parseFloat(p.price).toFixed(2)}</div>
            <div class="product-stock">${p.stock} left</div>
          </div>
          <button class="add-to-cart" onclick="addToCart(${JSON.stringify(p).replace(/"/g, '&quot;')}, event)" title="Add to cart"
            ${p.stock === 0 ? 'disabled style="opacity:0.4;cursor:not-allowed"' : ''}>+</button>
        </div>
      </div>
    </div>
  `).join('');
}

function renderPagination(total) {
  const pages = Math.ceil(total / PAGE_SIZE);
  const pg = document.getElementById('pagination');
  if (pages <= 1) { pg.innerHTML = ''; return; }
  let html = '';
  for (let i = 1; i <= pages; i++) {
    html += `<button class="page-btn ${i === state.page ? 'active' : ''}" onclick="loadProducts(${i})">${i}</button>`;
  }
  pg.innerHTML = html;
}

// ── Product Modal ──────────────────────────
async function openProductModal(id) {
  const product = state.allProducts.find(p => p.id === id);
  if (!product) return;
  const modal = document.getElementById('product-modal');
  const body = document.getElementById('modal-body');
  const price = parseFloat(product.price);
  body.innerHTML = `
    <div class="modal-thumb"><span style="font-size:72px">${productEmoji(product.name)}</span></div>
    <div class="modal-name">${product.name}</div>
    <div class="modal-price">$${price.toFixed(2)}</div>
    <div class="modal-desc">${product.description || 'No description available.'}</div>
    <div class="modal-meta">
      <div class="modal-meta-item"><label>Stock</label><span>${product.stock} units</span></div>
      <div class="modal-meta-item"><label>Status</label><span style="color:${product.stock > 0 ? 'var(--success)' : 'var(--error)'}">${product.stock > 0 ? 'Available' : 'Out of Stock'}</span></div>
      <div class="modal-meta-item"><label>Added</label><span>${new Date(product.create_at).toLocaleDateString()}</span></div>
    </div>
    <button class="btn-primary full-width" onclick="addToCart(${JSON.stringify(product).replace(/"/g, '&quot;')}, null); closeModal();" ${product.stock === 0 ? 'disabled style="opacity:0.5"' : ''}>
      <span>${product.stock > 0 ? 'Add to Cart' : 'Out of Stock'}</span>
    </button>
  `;
  modal.classList.remove('hidden');
}

function closeModal() { document.getElementById('product-modal').classList.add('hidden'); }

// ── Coupons ────────────────────────────────
async function loadCoupons() {
  const grid = document.getElementById('coupons-grid');
  grid.innerHTML = `<div class="skeleton-grid">${'<div class="skeleton-card"></div>'.repeat(3)}</div>`;
  const data = await apiGet('/coupons/?limit=50');
  if (!data) { grid.innerHTML = '<div class="empty-state"><h3>Failed to load coupons</h3></div>'; return; }
  // Show only PUBLIC active coupons to users
  state.coupons = data.filter(c => c.visibility === 'PUBLIC' && c.is_active);
  renderCoupons();
}

function renderCoupons() {
  const grid = document.getElementById('coupons-grid');
  if (state.coupons.length === 0) {
    grid.innerHTML = '<div class="empty-state"><h3>No active public coupons</h3><p>Check back later or use a private code.</p></div>';
    return;
  }
  grid.innerHTML = state.coupons.map(c => {
    const isPercent = c.discount_type === 'PERCENT';
    const valDisplay = isPercent
      ? `${c.discount_value}<sub>%OFF</sub>`
      : `<sup>$</sup>${c.discount_value}<sub>OFF</sub>`;
    const typeClass = isPercent ? 'type-percent' : 'type-fixed';
    const typeLabel = isPercent ? 'Percentage' : 'Fixed Amount';
    const minOrder = c.min_order_value ? `$${c.min_order_value}` : 'None';
    const maxDisc = c.max_discount_amount ? `$${c.max_discount_amount}` : 'Unlimited';
    return `
      <div class="coupon-card">
        <div class="coupon-top">
          <div class="coupon-value">${valDisplay}</div>
          <div class="coupon-type-badge ${typeClass}">${typeLabel}</div>
        </div>
        <div class="coupon-code-wrap">
          <span class="coupon-code">${c.code}</span>
          <button class="copy-btn" onclick="copyCode('${c.code}', this)">
            <svg viewBox="0 0 24 24" fill="none"><rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" stroke="currentColor" stroke-width="1.5"/></svg>
            Copy
          </button>
        </div>
        <div class="coupon-meta">
          <div class="meta-row"><span class="meta-label">Min. Order</span><span class="meta-val">${minOrder}</span></div>
          ${isPercent ? `<div class="meta-row"><span class="meta-label">Max Discount</span><span class="meta-val">${maxDisc}</span></div>` : ''}
        </div>
        <div class="coupon-actions">
          <button class="apply-from-coupon" onclick="applyFromCouponCard('${c.code}')">Apply in Cart</button>
        </div>
      </div>
    `;
  }).join('');
}

function copyCode(code, btn) {
  navigator.clipboard.writeText(code).then(() => {
    const orig = btn.innerHTML;
    btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg> Copied!`;
    btn.style.color = 'var(--success)';
    setTimeout(() => { btn.innerHTML = orig; btn.style.color = ''; }, 2000);
  });
}

function applyFromCouponCard(code) {
  openCart();
  setTimeout(() => {
    document.getElementById('checkout-coupon-code').value = code;
    applyCoupon();
  }, 300);
}

// ── Cart Drawer ────────────────────────────
function openCart() {
  document.getElementById('cart-drawer').classList.remove('hidden');
  document.getElementById('cart-overlay').classList.remove('hidden');
  renderCart();
}

function closeCart() {
  document.getElementById('cart-drawer').classList.add('hidden');
  document.getElementById('cart-overlay').classList.add('hidden');
}

// ── User Menu ──────────────────────────────
function renderUser() {
  const label = document.getElementById('user-label');
  const info = document.getElementById('dropdown-info');
  if (state.user) {
    label.textContent = state.user.username;
    info.innerHTML = `<strong>${state.user.username}</strong>${state.user.email}`;
  }
}

function toggleUserMenu() {
  document.getElementById('user-dropdown').classList.toggle('open');
}

// ── Auth forms ─────────────────────────────
async function handleLogin(e) {
  e.preventDefault();
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  const errEl = document.getElementById('login-error');
  errEl.classList.add('hidden');
  const body = new URLSearchParams({ username, password });
  try {
    const r = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString()
    });
    const data = await r.json();
    if (r.ok) {
      state.token = data.access_token;
      localStorage.setItem('cs_token', data.access_token);
      // Fetch user info
      const me = await apiGet('/auth/me');
      if (me) {
        saveAuth(data.access_token, me);
        renderUser();
        hideAuth();
        await Promise.all([loadProducts(), loadCoupons()]);
        renderCartCount();
        showToast(`Welcome back, ${me.username}!`, 'success');
      }
    } else {
      errEl.textContent = data.detail || 'Invalid username or password';
      errEl.classList.remove('hidden');
    }
  } catch (_) {
    errEl.textContent = 'Connection error. Is the backend running?';
    errEl.classList.remove('hidden');
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const username = document.getElementById('reg-username').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;
  const errEl = document.getElementById('register-error');
  errEl.classList.add('hidden');
  try {
    const r = await fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    const data = await r.json();
    if (r.ok) {
      showToast('Account created! Please sign in.', 'success');
      // Switch to login tab
      document.querySelectorAll('.auth-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === 'login'));
      document.getElementById('login-form').classList.add('active');
      document.getElementById('register-form').classList.remove('active');
      document.getElementById('login-username').value = username;
    } else {
      errEl.textContent = data.detail || 'Registration failed';
      errEl.classList.remove('hidden');
    }
  } catch (_) {
    errEl.textContent = 'Connection error. Is the backend running?';
    errEl.classList.remove('hidden');
  }
}

// ── Init ───────────────────────────────────
async function init() {
  renderCartCount();
  // Event listeners
  document.getElementById('login-form').addEventListener('submit', handleLogin);
  document.getElementById('register-form').addEventListener('submit', handleRegister);
  document.getElementById('logout-btn').addEventListener('click', () => { closeUserDropdown(); logout(); });
  document.getElementById('cart-btn').addEventListener('click', openCart);
  document.getElementById('close-cart').addEventListener('click', closeCart);
  document.getElementById('cart-overlay').addEventListener('click', closeCart);
  document.getElementById('apply-coupon-btn').addEventListener('click', applyCoupon);
  document.getElementById('checkout-coupon-code').addEventListener('keydown', e => { if (e.key === 'Enter') applyCoupon(); });
  document.getElementById('check-private-btn').addEventListener('click', checkPrivateCode);
  document.getElementById('private-code-input').addEventListener('keydown', e => { if (e.key === 'Enter') checkPrivateCode(); });
  document.getElementById('modal-close').addEventListener('click', closeModal);
  document.getElementById('product-modal').addEventListener('click', e => { if (e.target === e.currentTarget) closeModal(); });
  document.getElementById('sort-select').addEventListener('change', renderProducts);
  document.getElementById('user-btn').addEventListener('click', e => { e.stopPropagation(); toggleUserMenu(); });
  document.addEventListener('click', () => document.getElementById('user-dropdown').classList.remove('open'));
  document.getElementById('checkout-btn').addEventListener('click', () => {
    if (state.cart.length === 0) { showToast('Your cart is empty', 'error'); return; }
    showToast('Checkout coming soon! This is a demo.', 'info');
  });

  // Auth tab switching
  document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
      document.getElementById(`${tab.dataset.tab}-form`).classList.add('active');
    });
  });

  if (state.token) {
    // Verify token still valid
    const me = await apiGet('/auth/me');
    if (me) {
      state.user = me;
      renderUser();
      hideAuth();
      await Promise.all([loadProducts(), loadCoupons()]);
    } else {
      showAuth();
    }
  } else {
    showAuth();
  }
}

function closeUserDropdown() {
  document.getElementById('user-dropdown').classList.remove('open');
}

document.addEventListener('DOMContentLoaded', init);
