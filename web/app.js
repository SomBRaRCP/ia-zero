const chat = document.getElementById('chat');
const form = document.getElementById('chat-form');
const input = document.getElementById('msg');
const statusEl = document.getElementById('status');
const badge = document.getElementById('badge-profile');
const modeBar = document.getElementById('mode-bar');
const autoToggle = document.getElementById('auto-mode');

function addMsg(text, who) {
  const div = document.createElement('div');
  div.className = `msg ${who}`;
  div.innerHTML = (text || '').replace(/\n/g, '<br/>');
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function updateModeUI(profile) {
  badge.textContent = profile || 'conversacional';
  document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
  const btn = document.querySelector(`.mode-btn[data-mode="${profile}"]`);
  if (btn) btn.classList.add('active');
}

function updateAutoUI(enabled) {
  if (!autoToggle) return;
  autoToggle.checked = !!enabled;
  if (enabled) modeBar.classList.add('disabled');
  else modeBar.classList.remove('disabled');
}

async function setAuto(enabled) {
  statusEl.textContent = 'Atualizando modo automatico...';
  try {
    const res = await fetch(`/api/auto/${enabled ? 1 : 0}`, { method: 'POST' });
    if (!res.ok) throw new Error('erro');
    const data = await res.json();
    updateAutoUI(data.auto);
    updateModeUI(data.profile);
    statusEl.textContent = data.auto ? 'Modo automatico ativado.' : 'Modo automatico desativado.';
  } catch (err) {
    statusEl.textContent = 'Falha ao alterar modo automatico.';
  }
}

async function setMode(mode) {
  statusEl.textContent = 'Trocando modo...';
  try {
    const res = await fetch(`/api/profile/${mode}`, { method: 'POST' });
    if (!res.ok) throw new Error('erro');
    const data = await res.json();
    updateModeUI(data.profile);
    updateAutoUI(false);
    statusEl.textContent = `Modo atual: ${data.profile}`;
  } catch (err) {
    statusEl.textContent = 'Falha ao trocar modo.';
  }
}

async function sendMessage(msg) {
  statusEl.textContent = 'Enviando...';
  addMsg(msg, 'user');
  input.value = '';
  input.focus();
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, auto: autoToggle ? !!autoToggle.checked : undefined })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'erro');
    addMsg(data.reply, 'bot');
    updateModeUI(data.profile);
    if (typeof data.auto === 'boolean') updateAutoUI(data.auto);
    statusEl.textContent = 'Pronto.';
  } catch (err) {
    addMsg('Falha ao enviar mensagem.', 'bot');
    statusEl.textContent = 'Erro.';
  }
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const msg = input.value.trim();
  if (!msg) return;
  sendMessage(msg);
});

modeBar.addEventListener('click', (e) => {
  const btn = e.target.closest('.mode-btn');
  if (!btn) return;
  if (autoToggle && autoToggle.checked) {
    setAuto(false).then(() => setMode(btn.dataset.mode));
    return;
  }
  setMode(btn.dataset.mode);
});

// define modo default
document.addEventListener('DOMContentLoaded', () => {
  fetch('/api/state')
    .then(r => r.json())
    .then(data => {
      updateModeUI(data.profile);
      updateAutoUI(data.auto);
      statusEl.textContent = data.auto ? 'Modo automatico ativado.' : `Modo atual: ${data.profile}`;
    })
    .catch(() => {
      updateModeUI('conversacional');
      updateAutoUI(true);
    });

  if (autoToggle) {
    autoToggle.addEventListener('change', () => {
      setAuto(autoToggle.checked);
    });
  }
  addMsg('Ola! Envie sua pergunta. (modo automatico escolhe o melhor perfil)', 'bot');
});
