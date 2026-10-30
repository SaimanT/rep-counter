(() => {
  // Each page keeps its own state: <body data-slug="otzhimaniya" data-default-plan="20" data-root="../">
  const { slug = '', defaultPlan = '10', root = './' } = document.body.dataset;
  const KEY = 'rep-counter-v1' + (slug ? ':' + slug : '');
  let state = { plan: +defaultPlan, count: 0, sets: [] };
  try { Object.assign(state, JSON.parse(localStorage.getItem(KEY)) || {}); } catch (e) {}

  const $ = id => document.getElementById(id);
  const app = $('app');
  const planInput = $('plan');
  planInput.value = state.plan;

  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }

  function beep(freq = 880, ms = 120) {
    try {
      const ctx = beep.ctx || (beep.ctx = new AudioContext());
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.frequency.value = freq; o.connect(g); g.connect(ctx.destination);
      g.gain.setValueAtTime(0.2, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + ms / 1000);
      o.start(); o.stop(ctx.currentTime + ms / 1000);
    } catch (e) {}
  }

  function render(bump) {
    const left = Math.max(state.plan - state.count, 0);
    $('count').textContent = state.count;
    $('done').textContent = state.count;
    $('total').textContent = state.plan;
    $('left').textContent = left;
    $('bar').style.width = Math.min(state.count / state.plan * 100, 100) + '%';
    app.classList.toggle('finished', state.count >= state.plan);
    const sum = state.sets.reduce((a, b) => a + b, 0);
    $('sets').textContent = state.sets.length
      ? `Подходы: ${state.sets.join(' · ')}  —  всего за тренировку: ${sum + state.count}`
      : '';
    if (bump) { const c = $('count'); c.classList.remove('bump'); void c.offsetWidth; c.classList.add('bump'); }
    save();
  }

  function add(n) {
    state.count = Math.max(state.count + n, 0);
    if (n > 0) beep(state.count === state.plan ? 1320 : 880, state.count === state.plan ? 400 : 80);
    render(n > 0);
  }

  function finishSet() {
    if (state.count > 0) { state.sets.push(state.count); state.count = 0; render(); }
  }

  function setPlan(v) { if (v > 0) { state.plan = v; planInput.value = v; render(); } }

  planInput.addEventListener('input', () => setPlan(parseInt(planInput.value, 10)));
  // Enter in the plan field returns focus to the counter
  planInput.addEventListener('keydown', e => { if (e.key === 'Enter') planInput.blur(); e.stopPropagation(); });
  document.querySelectorAll('[data-plan]').forEach(b =>
    b.addEventListener('click', () => { setPlan(+b.dataset.plan); b.blur(); }));

  document.addEventListener('keydown', e => {
    if (e.repeat || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.code === 'Space') { e.preventDefault(); add(1); }
    else if (e.code === 'Backspace' || e.code === 'Minus' || e.code === 'NumpadSubtract') { e.preventDefault(); add(-1); }
    else if (e.code === 'Enter' || e.code === 'NumpadEnter') { e.preventDefault(); finishSet(); }
    else if (e.code === 'KeyR') { if (confirm('Сбросить счётчик и подходы?')) { state.count = 0; state.sets = []; render(); } }
    else if (e.code === 'KeyF') {
      document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
    }
  });
  // Tap/click on the counter screen (not on its controls) also counts
  app.addEventListener('pointerdown', e => {
    if (e.button !== 0 || e.target.closest('.plan, .top, a')) return;
    // First tap after editing the plan only closes the field, it doesn't count
    if (document.activeElement === planInput) { e.preventDefault(); planInput.blur(); return; }
    add(1);
  });
  // Keep a valid plan if the field was left empty
  planInput.addEventListener('blur', () => { planInput.value = state.plan; });

  // Install as app
  let installEvent;
  window.addEventListener('beforeinstallprompt', e => { e.preventDefault(); installEvent = e; $('install').hidden = false; });
  $('install').addEventListener('click', async () => {
    if (!installEvent) return;
    installEvent.prompt(); await installEvent.userChoice; installEvent = null; $('install').hidden = true;
  });
  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    navigator.serviceWorker.register(root + 'sw.js').catch(() => {});
  }

  render();
})();
