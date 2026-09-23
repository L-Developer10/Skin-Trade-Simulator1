/**
 * Skin Trader Simulator - Cliente JavaScript
 * Integração Full-Stack com Flask (:5000) e Live Server (:5500)
 */

// ==============================================================================
// 0. CONFIGURAÇÃO CENTRAL DA URL DO BACKEND
// ==============================================================================
const API_URL = "http://127.0.0.1:5000";

// ==============================================================================
// 1. ARMAS COM SVGs VETORIAIS EMBUTIDOS
// ==============================================================================
const WEAPON_SVGS = {
  pistol: `<svg viewBox="0 0 100 60" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M15 25H60L55 12H18L15 25Z" fill="currentColor" opacity="0.8"/>
    <path d="M60 20H88L85 28H60V20Z" fill="currentColor"/>
    <path d="M22 25L32 52H45L38 25H22Z" fill="currentColor" opacity="0.9"/>
    <rect x="36" y="27" width="10" height="12" rx="2" fill="#222"/>
  </svg>`,
  rifle: `<svg viewBox="0 0 120 50" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M10 22H35L42 32H20L10 22Z" fill="currentColor" opacity="0.8"/>
    <path d="M35 18H95L108 22H115V26H95L90 32H75L72 26H50L45 42H35L42 26H35V18Z" fill="currentColor"/>
    <rect x="95" y="19" width="18" height="4" fill="currentColor" opacity="0.9"/>
  </svg>`,
  sniper: `<svg viewBox="0 0 130 45" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M5 22H25L30 32H15L5 22Z" fill="currentColor" opacity="0.7"/>
    <rect x="40" y="8" width="40" height="7" rx="2" fill="currentColor"/>
    <path d="M25 18H118V24H85L80 32H70L73 24H25V18Z" fill="currentColor" opacity="0.9"/>
    <rect x="118" y="20" width="10" height="4" fill="currentColor"/>
  </svg>`,
  smg: `<svg viewBox="0 0 100 55" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M15 20H75V28H65L58 46H46L50 28H28L20 42H12L15 20Z" fill="currentColor"/>
    <rect x="75" y="22" width="18" height="4" fill="currentColor" opacity="0.8"/>
  </svg>`,
  shotgun: `<svg viewBox="0 0 110 45" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M8 20H30L38 32H22L8 20Z" fill="currentColor" opacity="0.75"/>
    <rect x="30" y="18" width="65" height="9" rx="1" fill="currentColor"/>
    <rect x="50" y="28" width="22" height="6" rx="2" fill="currentColor" opacity="0.9"/>
    <rect x="95" y="20" width="12" height="5" fill="currentColor"/>
  </svg>`,
  knife: `<svg viewBox="0 0 100 65" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 48L24 55C30 52 35 45 32 38L22 34C18 36 14 42 12 48Z" fill="#333"/>
    <path d="M24 35C35 32 55 24 75 10C82 18 85 28 72 38C58 45 40 46 28 42L24 35Z" fill="currentColor"/>
    <circle cx="20" cy="46" r="5" fill="#111"/>
  </svg>`
};

// ==============================================================================
// 2. CONFIGURAÇÃO DAS CAIXAS
// ==============================================================================
const BOXES = {
  comum: { id: "comum", name: "Caixa Comum", price: 100.00 },
  rara: { id: "rara", name: "Caixa Rara", price: 1000.00 },
  lendaria: { id: "lendaria", name: "Caixa Lendária", price: 10000.00 }
};

// ==============================================================================
// 3. SISTEMA DE ÁUDIO SINTETIZADO (WEB AUDIO API)
// ==============================================================================
class SoundFX {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  playTone(freq, type = 'sine', duration = 0.08, vol = 0.15) {
    if (!this.enabled) return;
    try {
      this.init();
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
      gain.gain.setValueAtTime(vol, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + duration);
    } catch (e) {
      console.warn('Audio error', e);
    }
  }

  tick() {
    this.playTone(750, 'triangle', 0.03, 0.12);
  }

  coin() {
    this.playTone(880, 'sine', 0.09, 0.2);
    setTimeout(() => this.playTone(1320, 'sine', 0.15, 0.25), 60);
  }

  buzz() {
    this.playTone(130, 'sawtooth', 0.2, 0.2);
  }

  win() {
    const notes = [523.25, 659.25, 783.99, 1046.50];
    notes.forEach((freq, idx) => {
      setTimeout(() => this.playTone(freq, 'triangle', 0.18, 0.25), idx * 70);
    });
  }

  jackpot() {
    const melody = [523.25, 659.25, 783.99, 1046.50, 1318.51, 1567.98];
    melody.forEach((freq, idx) => {
      setTimeout(() => this.playTone(freq, 'square', 0.22, 0.2), idx * 80);
    });
  }
}

const sfx = new SoundFX();

// ==============================================================================
// 4. ESTADO GLOBAL DO CLIENTE
// ==============================================================================
const state = {
  user: null,
  balance: 0.00,
  inventory: [],
  currentTab: 'tab-case',
  isSpinningCase: false,
  isSpinningSlots: false,
  clickerActive: false,
  clickerDiff: 'easy',
  openQuantity: 1,
  clickerStats: { hits: 0, totalEarned: 0 },
  pendingUnboxItem: null,
  pendingMultiItems: [],
  activeMarketTimers: {}
};

function formatMoney(amount) {
  return (amount || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function updateBalanceUI(newBalance, delta = 0) {
  state.balance = Math.max(0, Math.round(newBalance * 100) / 100);
  const el = document.getElementById('balance-display');
  if (el) {
    el.textContent = formatMoney(state.balance);
    if (delta > 0) {
      el.classList.remove('pulse-green', 'pulse-red');
      void el.offsetWidth;
      el.classList.add('pulse-green');
    } else if (delta < 0) {
      el.classList.remove('pulse-green', 'pulse-red');
      void el.offsetWidth;
      el.classList.add('pulse-red');
    }
  }
  updateBoxButtonsUI();
}

function updateBoxButtonsUI() {
  const qty = state.openQuantity;
  Object.keys(BOXES).forEach(boxId => {
    const box = BOXES[boxId];
    const totalCost = box.price * qty;

    const priceEl = document.getElementById(`price-${boxId}`);
    if (priceEl) priceEl.textContent = formatMoney(totalCost);

    const btn = document.getElementById(`btn-${boxId}`);
    if (btn) {
      btn.textContent = `ABRIR ${qty}x (${formatMoney(totalCost)})`;
      btn.disabled = !state.user || state.balance < totalCost || state.isSpinningCase;
    }
  });
}

function showToast(msg, icon = 'ℹ️') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span>${icon}</span> <span>${msg}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 300);
  }, 4500);
}

// ==============================================================================
// 5. AUTENTICAÇÃO E PERFIL DO USUÁRIO VIA FLASK & MONGODB
// ==============================================================================

async function checkAuthSession() {
  try {
    const res = await fetch(`${API_URL}/api/me`, {
      method: 'GET',
      credentials: 'include'
    });
    
    if (res.ok) {
      const data = await res.json();
      if (data.authenticated && data.user) {
        onUserAuthenticated(data.user);
        return;
      }
    }
  } catch (err) {
    console.warn("Servidor Flask (:5000) não respondeu no /api/me:", err);
  }
  onUserLoggedOut();
}

function onUserAuthenticated(user) {
  state.user = user;
  state.inventory = user.inventario || [];
  updateBalanceUI(user.dinheiro || 0.0);

  // Exibe informações no Header
  const chip = document.getElementById('user-profile-chip');
  const guestActions = document.getElementById('guest-auth-actions');
  const avatarEl = document.getElementById('user-avatar');
  const nameEl = document.getElementById('user-name');
  const authModal = document.getElementById('auth-modal');

  if (chip) chip.style.display = 'flex';
  if (guestActions) guestActions.style.display = 'none';
  if (avatarEl) {
    avatarEl.src = user.avatar || `https://avatars.githubusercontent.com/${encodeURIComponent(user.username || 'user')}`;
    avatarEl.onerror = () => { avatarEl.src = 'https://avatars.githubusercontent.com/u/0'; };
  }
  if (nameEl) nameEl.textContent = user.nome || user.username || 'Jogador';
  if (authModal) authModal.classList.remove('show');

  atualizarInventario();
  showToast(`Conectado como ${user.nome || user.username}! Saldo e inventário carregados do MongoDB.`, '👤');
}

function onUserLoggedOut() {
  state.user = null;
  state.inventory = [];
  updateBalanceUI(0.0);

  const chip = document.getElementById('user-profile-chip');
  const guestActions = document.getElementById('guest-auth-actions');
  const authModal = document.getElementById('auth-modal');

  if (chip) chip.style.display = 'none';
  if (guestActions) guestActions.style.display = 'block';
  if (authModal) authModal.classList.add('show');

  atualizarInventario();
}

async function handleLogout() {
  try {
    await fetch(`${API_URL}/auth/logout`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Accept': 'application/json' }
    });
  } catch (e) {
    console.warn("Erro ao deslogar no backend:", e);
  }
  onUserLoggedOut();
  showToast('Você saiu da sua conta.', '👋');
}

// ==============================================================================
// 6. MULTI-CAIXAS: ABERTURA AUTORITATIVA NO BACKEND FLASK
// ==============================================================================
const CARD_WIDTH = 140;
const TOTAL_CAROUSEL_ITEMS = 65;
const WINNING_INDEX = 52;

function buildSkinCardHTML(skin) {
  const svg = WEAPON_SVGS[skin.type] || WEAPON_SVGS.rifle;
  return `
    <div class="roulette-card ${skin.rarity}" data-skin-id="${skin.id || skin.skinId}">
      <div class="card-weapon-icon" style="color: ${skin.color}">
        ${svg}
      </div>
      <div class="card-weapon-name">${skin.weapon}</div>
      <div class="card-skin-name">${skin.skin}</div>
    </div>
  `;
}

function setOpenQuantity(qty) {
  qty = Math.min(5, Math.max(1, parseInt(qty) || 1));
  state.openQuantity = qty;

  document.querySelectorAll('.qty-btn').forEach(btn => {
    btn.classList.toggle('active', parseInt(btn.dataset.qty) === qty);
  });

  updateBoxButtonsUI();
}

window.abrirCaixa = async function(boxId) {
  if (!state.user) {
    document.getElementById('auth-modal').classList.add('show');
    showToast('Você precisa entrar na sua conta para abrir caixas!', '⚠️');
    return;
  }

  if (state.isSpinningCase) return;

  const qty = state.openQuantity;
  const box = BOXES[boxId];
  if (!box) return;

  const totalCost = box.price * qty;
  if (state.balance < totalCost) {
    showToast(`Saldo insuficiente! ${qty}x ${box.name} custa ${formatMoney(totalCost)}.`, '⚠️');
    sfx.buzz();
    return;
  }

  sfx.init();
  state.isSpinningCase = true;
  updateBoxButtonsUI();

  try {
    // Solicita a abertura autoritativa ao backend Flask
    const res = await fetch(`${API_URL}/api/caixas/abrir`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ boxId: boxId, quantity: qty })
    });

    const data = await res.json();
    if (!res.ok || data.error) {
      showToast(data.error || 'Erro ao abrir caixa no servidor.', '❌');
      sfx.buzz();
      state.isSpinningCase = false;
      updateBoxButtonsUI();
      return;
    }

    const winningItems = data.items;
    updateBalanceUI(data.novoSaldo, -totalCost);

    // Adiciona as skins ao inventário local sincronizado
    state.inventory.unshift(...winningItems);
    atualizarInventario();

    // Rola para a esteira e executa animação correspondente
    const stageEl = document.getElementById('roulette-stage');
    if (stageEl) {
      stageEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    animarCaixasSimultaneas(box, winningItems, () => {
      if (qty === 1) {
        state.pendingUnboxItem = winningItems[0];
        mostrarResultado(winningItems[0]);
      } else {
        state.pendingMultiItems = winningItems;
        mostrarResultadoMultiplo(winningItems, totalCost);
      }
    });

  } catch (err) {
    console.error("Erro na requisição ao backend Flask:", err);
    showToast('Erro de comunicação com o servidor Flask (:5000). Verifique se ele está rodando com python app.py.', '❌');
    state.isSpinningCase = false;
    updateBoxButtonsUI();
  }
};

function animarCaixasSimultaneas(box, winningItems, callback) {
  const container = document.getElementById('multi-roulette-container');
  container.innerHTML = '';

  const qty = winningItems.length;
  const isSingle = qty === 1;

  const tracks = [];
  const targetXs = [];

  for (let idx = 0; idx < qty; idx++) {
    const item = winningItems[idx];
    const viewport = document.createElement('div');
    viewport.className = `roulette-viewport ${isSingle ? 'single-viewport' : ''}`;
    
    viewport.innerHTML = `
      <div class="roulette-track-label">Caixa #${idx + 1}</div>
      <div class="roulette-marker top"></div>
      <div class="roulette-marker bottom"></div>
      <div class="roulette-track" id="roulette-track-${idx}"></div>
    `;
    container.appendChild(viewport);

    const track = viewport.querySelector(`#roulette-track-${idx}`);
    tracks.push(track);

    const fragment = document.createDocumentFragment();
    for (let i = 0; i < TOTAL_CAROUSEL_ITEMS; i++) {
      let currentSkin;
      if (i === WINNING_INDEX) {
        currentSkin = item;
      } else {
        currentSkin = item; // preenche visualmente
      }
      const temp = document.createElement('div');
      temp.innerHTML = buildSkinCardHTML(currentSkin);
      fragment.appendChild(temp.firstElementChild);
    }
    track.appendChild(fragment);

    const viewportWidth = viewport.clientWidth || 800;
    const randomOffset = Math.floor(Math.random() * 60) - 30;
    const targetX = (WINNING_INDEX * CARD_WIDTH) + (CARD_WIDTH / 2) - (viewportWidth / 2) + randomOffset;
    targetXs.push(targetX);
  }

  const spinDuration = 5500;
  const startTime = Date.now();
  let nextTickTime = 35;

  function scheduleTicks() {
    const elapsed = Date.now() - startTime;
    if (elapsed < spinDuration && state.isSpinningCase) {
      sfx.tick();
      const progress = elapsed / spinDuration;
      nextTickTime = 30 + Math.pow(progress, 3) * 450;
      setTimeout(scheduleTicks, nextTickTime);
    }
  }

  requestAnimationFrame(() => {
    tracks.forEach((track, idx) => {
      track.style.transition = `transform ${spinDuration}ms cubic-bezier(0.12, 0.8, 0.33, 1)`;
      track.style.transform = `translateX(-${targetXs[idx]}px)`;
    });
    setTimeout(scheduleTicks, 50);
  });

  setTimeout(() => {
    state.isSpinningCase = false;
    updateBoxButtonsUI();

    const hasLegendary = winningItems.some(i => i.rarity === 'legendary');
    if (hasLegendary) {
      sfx.jackpot();
    } else {
      sfx.win();
    }

    if (typeof callback === 'function') {
      callback();
    }
  }, spinDuration + 150);
}

// Modal 1 item
function mostrarResultado(item) {
  const modal = document.getElementById('unbox-modal');
  const rarityBadge = document.getElementById('modal-rarity');
  const wearBadge = document.getElementById('modal-wear');
  const svgWrap = document.getElementById('modal-svg');
  const nameEl = document.getElementById('modal-skin-name');
  const priceEl = document.getElementById('modal-skin-price');
  const subpriceEl = document.getElementById('modal-skin-subprice');
  const botPriceEl = document.getElementById('modal-bot-price');
  const glow = document.getElementById('modal-glow');

  const botSellValue = Math.round(item.price * 0.45 * 100) / 100;

  rarityBadge.textContent = item.rarity.toUpperCase();
  rarityBadge.style.background = item.color;
  rarityBadge.style.color = item.rarity === 'legendary' ? '#000' : '#fff';

  wearBadge.textContent = item.conditionLabel.toUpperCase();
  wearBadge.style.borderColor = item.conditionColor;
  wearBadge.style.color = item.conditionColor;

  glow.style.background = `radial-gradient(circle, ${item.color}44 0%, transparent 70%)`;
  svgWrap.innerHTML = WEAPON_SVGS[item.type] || WEAPON_SVGS.rifle;
  svgWrap.style.color = item.color;

  nameEl.textContent = `${item.weapon} | ${item.skin}`;
  priceEl.textContent = formatMoney(item.price);
  subpriceEl.textContent = `Base: ${formatMoney(item.basePrice)} (${item.conditionMult.toFixed(2)}x - ${item.conditionLabel})`;
  botPriceEl.textContent = formatMoney(botSellValue);

  modal.classList.add('show');
}

function hideUnboxModal() {
  document.getElementById('unbox-modal').classList.remove('show');
}

// Modal Multi (2 a 5 itens)
function mostrarResultadoMultiplo(items, totalCost) {
  const modal = document.getElementById('multi-unbox-modal');
  const titleEl = document.getElementById('multi-modal-title');
  const costEl = document.getElementById('multi-cost');
  const valEl = document.getElementById('multi-value');
  const gridEl = document.getElementById('multi-items-grid');
  const botBtnEl = document.getElementById('multi-bot-total');

  const totalWon = items.reduce((sum, i) => sum + i.price, 0);
  const botTotal = Math.round(totalWon * 0.45 * 100) / 100;

  titleEl.textContent = `🎉 VOCÊ ABRIU ${items.length} CAIXAS!`;
  costEl.textContent = formatMoney(totalCost);
  valEl.textContent = formatMoney(totalWon);
  botBtnEl.textContent = formatMoney(botTotal);

  gridEl.innerHTML = '';
  items.forEach(item => {
    const card = document.createElement('div');
    card.className = `multi-item-card ${item.rarity}`;
    const svg = WEAPON_SVGS[item.type] || WEAPON_SVGS.rifle;

    card.innerHTML = `
      <div class="multi-item-svg" style="color: ${item.color}">
        ${svg}
      </div>
      <div class="multi-item-name">${item.weapon} | ${item.skin}</div>
      <span class="multi-item-wear" style="color: ${item.conditionColor}; border-color: ${item.conditionColor}">
        ${item.conditionLabel}
      </span>
      <div class="multi-item-price">${formatMoney(item.price)}</div>
    `;
    gridEl.appendChild(card);
  });

  modal.classList.add('show');
}

function hideMultiUnboxModal() {
  document.getElementById('multi-unbox-modal').classList.remove('show');
}

function keepCurrentSkin() {
  hideUnboxModal();
  showToast(`${state.pendingUnboxItem.weapon} | ${state.pendingUnboxItem.skin} guardada no inventário MongoDB!`, '🎒');
  state.pendingUnboxItem = null;
}

async function sellToBotFromModal() {
  if (!state.pendingUnboxItem) return;
  const uid = state.pendingUnboxItem.uid;
  hideUnboxModal();
  await window.sellItemToBot(uid);
  state.pendingUnboxItem = null;
}

function keepAllMultiSkins() {
  hideMultiUnboxModal();
  showToast(`${state.pendingMultiItems.length} skins salvas no inventário MongoDB!`, '🎒');
  state.pendingMultiItems = [];
}

async function sellAllMultiToBot() {
  if (!state.pendingMultiItems || state.pendingMultiItems.length === 0) return;
  const uids = state.pendingMultiItems.map(i => i.uid);
  hideMultiUnboxModal();

  try {
    const res = await fetch(`${API_URL}/api/skins/vender-lote`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uids: uids, sellType: 'bot' })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      updateBalanceUI(data.novoSaldo, data.payout);
      // Remove do inventário local
      state.inventory = state.inventory.filter(i => !uids.includes(i.uid));
      atualizarInventario();
      sfx.coin();
      showToast(`${data.count} skins vendidas ao bot por ${formatMoney(data.payout)} (45%)!`, '🤖');
    }
  } catch (e) {
    showToast('Erro ao vender lote de skins no backend.', '❌');
  }
  state.pendingMultiItems = [];
}

// ==============================================================================
// 7. INVENTÁRIO & MERCADO (ATUALIZAÇÃO & VENDAS AUTORITATIVAS)
// ==============================================================================
let activeFilter = 'all';

function atualizarInventario() {
  const badge = document.getElementById('inv-count-badge');
  if (badge) badge.textContent = state.inventory.length;

  const totalSkinsEl = document.getElementById('inv-total-skins');
  const totalValueEl = document.getElementById('inv-total-value');

  if (totalSkinsEl) totalSkinsEl.textContent = state.inventory.length;
  if (totalValueEl) {
    const totalVal = state.inventory.reduce((sum, item) => sum + (item.price || item.basePrice || 0), 0);
    totalValueEl.textContent = formatMoney(totalVal);
  }

  const grid = document.getElementById('inventory-grid');
  const empty = document.getElementById('empty-inventory');
  if (!grid || !empty) return;

  grid.innerHTML = '';

  const filtered = activeFilter === 'all'
    ? state.inventory
    : state.inventory.filter(item => item.rarity === activeFilter);

  if (filtered.length === 0) {
    empty.style.display = 'block';
    return;
  }
  empty.style.display = 'none';

  filtered.forEach(item => {
    const card = document.createElement('div');
    card.className = `skin-card ${item.rarity}`;
    card.id = `inv-card-${item.uid}`;

    const currentPrice = item.price || item.basePrice || 10;
    const botPrice = Math.round(currentPrice * 0.45 * 100) / 100;
    const svg = WEAPON_SVGS[item.type] || WEAPON_SVGS.rifle;

    const conditionLabel = item.conditionLabel || 'Normal';
    const conditionColor = item.conditionColor || '#90caf9';
    const conditionMult = item.conditionMult || 1.0;

    let actionsHTML = '';
    if (item.status === 'on_market') {
      actionsHTML = `
        <div class="market-status-box">
          <span class="market-spinner">⏳</span>
          <strong>À venda para Players...</strong>
          <span id="market-timer-${item.uid}">Aguardando comprador (${item.marketRemaining || 6}s)</span>
        </div>
      `;
    } else {
      actionsHTML = `
        <div class="skin-card-actions">
          <button class="btn-sell-bot" onclick="sellItemToBot('${item.uid}')">
            <span>Vender ao Bot</span>
            <strong>${formatMoney(botPrice)} (45%)</strong>
          </button>
          <button class="btn-sell-player" onclick="sellItemToPlayerMarket('${item.uid}')">
            <span>Vender no Mercado</span>
            <strong>${formatMoney(currentPrice)} (100%)</strong>
          </button>
        </div>
      `;
    }

    card.innerHTML = `
      <div class="card-top-row">
        <span class="skin-rarity-pill">${item.rarity}</span>
        <span class="skin-price-tag">${formatMoney(currentPrice)}</span>
      </div>
      <div class="skin-card-img-wrap" style="color: ${item.color}">
        ${svg}
      </div>
      <div class="skin-card-name">${item.weapon} | ${item.skin}</div>
      <div class="skin-card-sub">
        <span class="skin-wear-pill" style="color: ${conditionColor}; border-color: ${conditionColor}">
          ${conditionLabel} (${conditionMult.toFixed(2)}x)
        </span>
      </div>
      ${actionsHTML}
    `;

    grid.appendChild(card);
  });
}

// Venda ao Bot via API
window.sellItemToBot = async function(uid) {
  if (!state.user) return;
  try {
    const res = await fetch(`${API_URL}/api/skins/vender`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uid: uid, sellType: 'bot' })
    });
    const data = await res.json();
    if (!res.ok || data.error) {
      showToast(data.error || 'Erro ao vender skin.', '❌');
      return;
    }

    // Remove do inventário local
    state.inventory = state.inventory.filter(i => i.uid !== uid);
    updateBalanceUI(data.novoSaldo, data.payout);
    atualizarInventario();
    sfx.coin();
    showToast(`Skin vendida ao bot por ${formatMoney(data.payout)} (45%)! Saldo salvo no MongoDB.`, '🤖');
  } catch (err) {
    showToast('Falha ao comunicar com o servidor Flask (:5000).', '❌');
  }
};

// Venda para Players com contagem regressiva simulada
window.sellItemToPlayerMarket = function(uid) {
  const item = state.inventory.find(i => i.uid === uid);
  if (!item || item.status === 'on_market') return;

  item.status = 'on_market';
  const waitSeconds = Math.floor(Math.random() * 9) + 4;
  item.marketRemaining = waitSeconds;

  atualizarInventario();
  showToast(`${item.weapon} | ${item.skin} anunciada por ${formatMoney(item.price)}!`, '📦');

  const interval = setInterval(async () => {
    item.marketRemaining -= 1;
    const timerEl = document.getElementById(`market-timer-${item.uid}`);
    if (timerEl) {
      timerEl.textContent = `Aguardando comprador (${item.marketRemaining}s)`;
    }

    if (item.marketRemaining <= 0) {
      clearInterval(interval);
      try {
        const res = await fetch(`${API_URL}/api/skins/vender`, {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ uid: item.uid, sellType: 'player' })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          state.inventory = state.inventory.filter(i => i.uid !== item.uid);
          updateBalanceUI(data.novoSaldo, data.payout);
          atualizarInventario();
          sfx.win();
          showToast(`🎉 UM JOGADOR COMPROU sua ${item.weapon} | ${item.skin} por ${formatMoney(data.payout)} (100%)!`, '💰');
        }
      } catch (e) {
        showToast('Erro ao concluir venda no mercado.', '❌');
      }
    }
  }, 1000);

  state.activeMarketTimers[uid] = interval;
};

// ==============================================================================
// 8. MINI-GAME DE REFLEXO (VALIDADO NO BACKEND)
// ==============================================================================
const DIFF_CONFIG = {
  easy: { time: 5.0, reward: 10.00 },
  medium: { time: 1.3, reward: 45.00 },
  hard: { time: 0.7, reward: 100.00 }
};

let clickerTimer = null;
let clickerInterval = null;

function setClickerDifficulty(diff) {
  if (!DIFF_CONFIG[diff]) return;
  state.clickerDiff = diff;
  document.querySelectorAll('.diff-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.diff === diff);
  });
  if (state.clickerActive) {
    spawnNextTarget();
  }
}

function startClickerGame() {
  if (!state.user) {
    document.getElementById('auth-modal').classList.add('show');
    showToast('Entre com sua conta do GitHub ou teste para farmar dinheiro!', '⚠️');
    return;
  }
  sfx.init();
  state.clickerActive = true;
  document.getElementById('arena-overlay').style.display = 'none';
  spawnNextTarget();
}

function spawnNextTarget() {
  clearTimeout(clickerTimer);
  clearInterval(clickerInterval);

  const arena = document.getElementById('target-arena');
  const target = document.getElementById('red-target');
  const timerFill = document.getElementById('arena-timer-fill');
  const statTime = document.getElementById('stat-time');

  const config = DIFF_CONFIG[state.clickerDiff];
  const durationMs = config.time * 1000;

  const targetSize = 64;
  const maxX = arena.clientWidth - targetSize - 20;
  const maxY = arena.clientHeight - targetSize - 20;
  const randX = Math.max(15, Math.floor(Math.random() * maxX));
  const randY = Math.max(15, Math.floor(Math.random() * maxY));

  target.style.left = `${randX}px`;
  target.style.top = `${randY}px`;
  target.style.transform = 'none';
  target.style.display = 'flex';

  timerFill.style.transition = 'none';
  timerFill.style.width = '100%';
  requestAnimationFrame(() => {
    timerFill.style.transition = `width ${durationMs}ms linear`;
    timerFill.style.width = '0%';
  });

  statTime.textContent = `${config.time.toFixed(1)}s`;

  const startTime = Date.now();
  clickerInterval = setInterval(() => {
    const elapsed = (Date.now() - startTime) / 1000;
    const remaining = Math.max(0, config.time - elapsed);
    statTime.textContent = `${remaining.toFixed(1)}s`;
  }, 50);

  clickerTimer = setTimeout(() => {
    clearInterval(clickerInterval);
    target.style.display = 'none';
    sfx.buzz();
    spawnNextTarget();
  }, durationMs);
}

async function onTargetClicked(e) {
  if (!state.clickerActive || !state.user) return;
  e.stopPropagation();

  clearTimeout(clickerTimer);
  clearInterval(clickerInterval);

  try {
    // Requisita a recompensa validada ao backend Flask
    const res = await fetch(`${API_URL}/api/minigame/recompensa`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ difficulty: state.clickerDiff })
    });

    const data = await res.json();
    if (res.ok && data.success) {
      state.clickerStats.hits += 1;
      state.clickerStats.totalEarned += data.reward;
      updateBalanceUI(data.novoSaldo, data.reward);
      sfx.coin();

      document.getElementById('stat-hits').textContent = state.clickerStats.hits;
      document.getElementById('stat-earned').textContent = formatMoney(state.clickerStats.totalEarned);

      createFloatingText(e.clientX, e.clientY, `+${formatMoney(data.reward)}`);
    }
  } catch (err) {
    console.warn("Erro ao creditar recompensa:", err);
  }

  spawnNextTarget();
}

function createFloatingText(screenX, screenY, text) {
  const container = document.getElementById('floating-container');
  const arena = document.getElementById('target-arena');
  const rect = arena.getBoundingClientRect();

  const relX = screenX - rect.left;
  const relY = screenY - rect.top;

  const floatEl = document.createElement('div');
  floatEl.className = 'floating-text';
  floatEl.textContent = text;
  floatEl.style.left = `${relX}px`;
  floatEl.style.top = `${relY}px`;
  container.appendChild(floatEl);

  setTimeout(() => floatEl.remove(), 800);
}

// ==============================================================================
// 9. ROLETA DE APOSTAS / SLOTS (AUTORITATIVA NO BACKEND COM REGRA DO X)
// ==============================================================================
function setBetPercentage(pct) {
  const input = document.getElementById('bet-amount-input');
  if (!input) return;
  const calculated = Math.max(1, Math.floor(state.balance * (pct / 100)));
  input.value = calculated;
}

async function spinSlots() {
  if (!state.user) {
    document.getElementById('auth-modal').classList.add('show');
    showToast('Entre com sua conta do GitHub ou teste para apostar!', '⚠️');
    return;
  }

  if (state.isSpinningSlots) return;

  const input = document.getElementById('bet-amount-input');
  const bet = parseFloat(input.value);

  if (isNaN(bet) || bet <= 0) {
    showToast('Digite um valor de aposta válido!', '⚠️');
    return;
  }

  if (bet > state.balance) {
    showToast('Saldo insuficiente para esta aposta!', '⚠️');
    sfx.buzz();
    return;
  }

  sfx.init();
  state.isSpinningSlots = true;

  const btnSpin = document.getElementById('btn-spin-slots');
  btnSpin.disabled = true;

  const banner = document.getElementById('slot-result-banner');
  banner.textContent = 'Girando os carretéis autoritativos... 🍀';
  banner.style.color = '#fff';

  const reelEls = [
    document.getElementById('reel-1'),
    document.getElementById('reel-2'),
    document.getElementById('reel-3')
  ];

  const symbolEls = [
    document.getElementById('symbol-1'),
    document.getElementById('symbol-2'),
    document.getElementById('symbol-3')
  ];

  reelEls.forEach(r => r.classList.add('spinning'));

  const spinIntervals = [null, null, null];
  const allSymbols = ['❌', '🟢', '🟩', '❇️', '💚', '7️⃣'];

  reelEls.forEach((_, idx) => {
    spinIntervals[idx] = setInterval(() => {
      symbolEls[idx].textContent = allSymbols[Math.floor(Math.random() * allSymbols.length)];
      sfx.tick();
    }, 80);
  });

  try {
    const res = await fetch(`${API_URL}/api/slots/apostar`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bet: bet })
    });

    const data = await res.json();
    if (!res.ok || data.error) {
      showToast(data.error || 'Erro ao apostar no servidor.', '❌');
      sfx.buzz();
      spinIntervals.forEach(clearInterval);
      reelEls.forEach(r => r.classList.remove('spinning'));
      state.isSpinningSlots = false;
      btnSpin.disabled = false;
      return;
    }

    const finalSymbols = data.symbols;
    const stopTimes = [1100, 1700, 2300];

    stopTimes.forEach((time, idx) => {
      setTimeout(() => {
        clearInterval(spinIntervals[idx]);
        symbolEls[idx].textContent = finalSymbols[idx];
        reelEls[idx].classList.remove('spinning');
        sfx.playTone(500 + idx * 150, 'triangle', 0.1, 0.2);
      }, time);
    });

    setTimeout(() => {
      state.isSpinningSlots = false;
      btnSpin.disabled = false;
      updateBalanceUI(data.novoSaldo);

      if (data.multiplier >= 65) {
        sfx.jackpot();
      } else if (data.multiplier > 0) {
        sfx.win();
      } else {
        sfx.buzz();
      }

      banner.innerHTML = data.multiplier > 0 
        ? `<strong class="green-text">${data.message}</strong>`
        : `<span class="danger-text">${data.message}</span>`;

      showToast(data.multiplier > 0 ? `Ganho: ${formatMoney(data.payout)}` : 'Aposta perdida.', '🎰');
    }, 2450);

  } catch (err) {
    spinIntervals.forEach(clearInterval);
    reelEls.forEach(r => r.classList.remove('spinning'));
    state.isSpinningSlots = false;
    btnSpin.disabled = false;
    showToast('Falha na conexão com o servidor Flask (:5000).', '❌');
  }
}

// ==============================================================================
// 10. LOGIN LOCAL DE DESENVOLVIMENTO
// ==============================================================================
async function handleDevLogin() {
  const input = document.getElementById('dev-user-input');
  const username = input ? input.value.trim() : 'Jogador_CSGO';

  try {
    const res = await fetch(`${API_URL}/auth/dev-login`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username })
    });
    
    const data = await res.json();
    if (res.ok && data.success) {
      onUserAuthenticated(data.user);
    } else {
      showToast(data.error || 'Erro ao conectar ao MongoDB.', '❌');
    }
  } catch (err) {
    console.error("Erro no dev login:", err);
    showToast('Servidor Flask (:5000) inacessível no momento. Inicie-o com python app.py.', '❌');
  }
}

// ==============================================================================
// 11. INICIALIZAÇÃO DE ABAS & EVENT LISTENERS
// ==============================================================================
function initTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      sfx.init();
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      tab.classList.add('active');
      const targetId = tab.dataset.tab;
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add('active');
      }

      state.currentTab = targetId;
      if (targetId === 'tab-inventory') {
        atualizarInventario();
      }
    });
  });
}

function initEventListeners() {
  // Configuração dos links de autenticação para apontar sempre para o backend correto
  const headerGithubBtn = document.getElementById('btn-header-github');
  if (headerGithubBtn) headerGithubBtn.href = `${API_URL}/auth/github`;

  const modalGithubBtn = document.getElementById('btn-modal-github');
  if (modalGithubBtn) modalGithubBtn.href = `${API_URL}/auth/github`;

  // Botão Sair
  const logoutBtn = document.getElementById('btn-logout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', handleLogout);
  }

  // Toggle Som
  const soundToggle = document.getElementById('sound-toggle');
  if (soundToggle) {
    soundToggle.addEventListener('click', () => {
      sfx.enabled = !sfx.enabled;
      document.getElementById('sound-status').textContent = sfx.enabled ? 'Som Ligado' : 'Som Mudo';
      soundToggle.style.opacity = sfx.enabled ? '1' : '0.6';
    });
  }

  // Seletor de Quantidade de Abertura (1x a 5x)
  document.querySelectorAll('.qty-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      setOpenQuantity(btn.dataset.qty);
    });
  });

  // Modais de Abertura Individual
  const btnModalKeep = document.getElementById('modal-btn-keep');
  if (btnModalKeep) btnModalKeep.addEventListener('click', keepCurrentSkin);

  const btnModalBot = document.getElementById('modal-btn-bot');
  if (btnModalBot) btnModalBot.addEventListener('click', sellToBotFromModal);

  // Modais de Abertura Múltipla (2 a 5 caixas)
  const btnMultiKeep = document.getElementById('btn-multi-keep-all');
  if (btnMultiKeep) btnMultiKeep.addEventListener('click', keepAllMultiSkins);

  const btnMultiBot = document.getElementById('btn-multi-bot-all');
  if (btnMultiBot) btnMultiBot.addEventListener('click', sellAllMultiToBot);

  // Mini-game de Reflexo
  const btnStartClicker = document.getElementById('btn-start-clicker');
  if (btnStartClicker) btnStartClicker.addEventListener('click', startClickerGame);

  const targetEl = document.getElementById('red-target');
  if (targetEl) targetEl.addEventListener('click', onTargetClicked);

  document.querySelectorAll('.diff-btn').forEach(btn => {
    btn.addEventListener('click', () => setClickerDifficulty(btn.dataset.diff));
  });

  // Roleta de Apostas (Slots)
  document.querySelectorAll('.btn-pct').forEach(btn => {
    btn.addEventListener('click', () => setBetPercentage(parseFloat(btn.dataset.pct)));
  });
  const btnSpinSlots = document.getElementById('btn-spin-slots');
  if (btnSpinSlots) btnSpinSlots.addEventListener('click', spinSlots);

  // Filtros de Inventário
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.dataset.filter;
      atualizarInventario();
    });
  });

  // Login de Desenvolvimento
  const devBtn = document.getElementById('btn-dev-login');
  if (devBtn) {
    devBtn.addEventListener('click', handleDevLogin);
  }

  const devInput = document.getElementById('dev-user-input');
  if (devInput) {
    devInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleDevLogin();
    });
  }
}

// ==============================================================================
// 12. INICIALIZAÇÃO GERAL AO CARREGAR A PÁGINA
// ==============================================================================
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initEventListeners();

  // Trata parâmetros de retorno do OAuth ou redirecionamentos
  const urlParams = new URLSearchParams(window.location.search);
  const authStatus = urlParams.get('auth');
  const authErr = urlParams.get('auth_error');

  if (authStatus === 'success') {
    showToast('Autenticação com o GitHub realizada com sucesso!', '🎉');
    // Limpa os parâmetros da URL sem recarregar a página
    window.history.replaceState({}, document.title, window.location.pathname);
  }

  if (authErr) {
    if (authErr === 'configure_github_keys') {
      showToast('Para usar o login oficial do GitHub, configure GITHUB_CLIENT_ID e GITHUB_CLIENT_SECRET no .env! Use o botão ENTRAR (TESTE) para testar imediatamente.', '⚙️');
    } else {
      showToast(`Falha na autenticação do GitHub (${authErr}).`, '❌');
    }
    window.history.replaceState({}, document.title, window.location.pathname);
  }

  // Verifica se já existe sessão ativa no Flask
  checkAuthSession();
});
