(() => {
  // Each page keeps its own state: <body data-slug="otzhimaniya" data-default-plan="20" data-root="../">
  const { slug = '', defaultPlan = '10', root = './' } = document.body.dataset;
  const KEY = 'rep-counter-v1' + (slug ? ':' + slug : '');
  let state = { plan: +defaultPlan, count: 0, sets: [], sound: true };
  try { Object.assign(state, JSON.parse(localStorage.getItem(KEY)) || {}); } catch (e) {}

  const $ = id => document.getElementById(id);
  const app = $('app');
  const planInput = $('plan');
  planInput.value = state.plan;

  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }

  function beep(freq = 880, ms = 120) {
    if (!state.sound) return;
    try {
      const ctx = beep.ctx || (beep.ctx = new AudioContext());
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.frequency.value = freq; o.connect(g); g.connect(ctx.destination);
      g.gain.setValueAtTime(0.2, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + ms / 1000);
      o.start(); o.stop(ctx.currentTime + ms / 1000);
    } catch (e) {}
  }

  function vibrate(pattern) {
    if (state.sound && navigator.vibrate) navigator.vibrate(pattern);
  }

  function render(bump) {
    const left = Math.max(state.plan - state.count, 0);
    $('count').textContent = state.count;
    $('count').dataset.digits = String(state.count).length;
    $('done').textContent = state.count;
    $('total').textContent = state.plan;
    $('left').textContent = left;
    $('bar').style.width = Math.min(state.count / state.plan * 100, 100) + '%';
    app.classList.toggle('finished', state.count >= state.plan);
    const sum = state.sets.reduce((a, b) => a + b, 0);
    $('sets').textContent = state.sets.length
      ? `Подходы: ${state.sets.join(' · ')}  —  всего за тренировку: ${sum + state.count}`
      : '';
    $('sound').setAttribute('aria-pressed', state.sound);
    $('sound').textContent = state.sound ? '🔊' : '🔇';
    if (bump) { const c = $('count'); c.classList.remove('bump'); void c.offsetWidth; c.classList.add('bump'); }
    save();
  }

  // ---- Hints: short lines at key moments of a workout. Built by script only, so
  // they are not part of the page text that search engines index.
  const HINTS_KEY = 'rep-counter-hints';
  const isTouch = matchMedia('(hover: none)').matches;
  const DONE_LINES = ['Сделано. Вы решили — и выполнили.', 'План выполнен. Это и есть сила воли.',
    'Готово. Ещё одна маленькая победа.'];
  let hintPrefs = { off: false, visits: 0 };
  try { Object.assign(hintPrefs, JSON.parse(localStorage.getItem(HINTS_KEY)) || {}); } catch (e) {}
  try {
    if (!sessionStorage.getItem(HINTS_KEY)) { sessionStorage.setItem(HINTS_KEY, '1'); hintPrefs.visits++; }
  } catch (e) {}
  const saveHints = () => { try { localStorage.setItem(HINTS_KEY, JSON.stringify(hintPrefs)); } catch (e) {} };
  saveHints();
  // First few visits explain the idea; after that only the key moments remain
  const newcomer = hintPrefs.visits <= 3;
  const shown = new Set();
  let doneLine = 0, hintTimer;

  const hintBox = document.createElement('div');
  hintBox.className = 'hint';
  hintBox.setAttribute('aria-live', 'polite');
  hintBox.innerHTML = '<span></span><button type="button" aria-label="Больше не показывать подсказки" title="Больше не показывать подсказки">×</button>';
  document.querySelector('.progress').after(hintBox);
  hintBox.querySelector('button').addEventListener('click', e => {
    hintPrefs.off = true; saveHints(); hideHint(); e.currentTarget.blur();
  });

  function showHint(id, text, ms = 4500) {
    if (hintPrefs.off || (id !== 'done' && shown.has(id))) return;
    shown.add(id);
    hintBox.querySelector('span').textContent = text;
    hintBox.classList.add('show');
    clearTimeout(hintTimer);
    hintTimer = setTimeout(hideHint, ms);
  }
  function hideHint() { hintBox.classList.remove('show'); }

  function hintForCount() {
    const { count, plan } = state, left = plan - count;
    if (count === plan) showHint('done', DONE_LINES[doneLine++ % DONE_LINES.length]);
    else if (left === 3 && plan >= 8 && newcomer) showHint('left3', 'Осталось три. Финиш уже виден.');
    else if (count === Math.ceil(plan / 2) && plan >= 6) showHint('half', 'Половина позади. Смотрите, как тает «осталось».');
    else if (count === 1 && newcomer) showHint('first', 'Есть первое. Каждое нажатие — отметка прогресса.');
  }

  function add(n) {
    state.count = Math.max(state.count + n, 0);
    if (n > 0) {
      const reached = state.count === state.plan;
      beep(reached ? 1320 : 880, reached ? 400 : 80);
      vibrate(reached ? [80, 60, 80, 60, 200] : 25);
    }
    render(n > 0);
    if (n > 0) hintForCount();
  }

  function finishSet() {
    if (state.count > 0) {
      state.sets.push(state.count); state.count = 0; render();
      if (newcomer) showHint('set', 'Подход записан. Внизу — ваш итог за тренировку.');
    }
  }

  function reset() {
    if (confirm('Сбросить счётчик и подходы?')) { state.count = 0; state.sets = []; render(); shown.clear(); hideHint(); }
  }

  function toggleFullscreen() {
    document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen().catch(() => {});
  }

  function setPlan(v) { if (v > 0) { state.plan = v; planInput.value = v; render(); } }

  planInput.addEventListener('input', () => setPlan(parseInt(planInput.value, 10)));
  // Enter in the plan field returns focus to the counter
  planInput.addEventListener('keydown', e => { if (e.key === 'Enter') planInput.blur(); e.stopPropagation(); });
  document.querySelectorAll('[data-plan]').forEach(b =>
    b.addEventListener('click', () => { setPlan(+b.dataset.plan); b.blur(); }));

  // On-screen buttons: the same actions as the keyboard, for phones
  const buttons = {
    minus: () => add(-1), finish: finishSet, reset,
    sound: () => { state.sound = !state.sound; render(); },
    fullscreen: toggleFullscreen,
  };
  for (const [id, action] of Object.entries(buttons)) {
    $(id).addEventListener('click', e => { action(); e.currentTarget.blur(); });
  }
  if (!document.fullscreenEnabled) $('fullscreen').hidden = true;

  document.addEventListener('keydown', e => {
    if (e.repeat || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.code === 'Space') { e.preventDefault(); add(1); }
    else if (e.code === 'Backspace' || e.code === 'Minus' || e.code === 'NumpadSubtract') { e.preventDefault(); add(-1); }
    else if (e.code === 'Enter' || e.code === 'NumpadEnter') { e.preventDefault(); finishSet(); }
    else if (e.code === 'KeyR') reset();
    else if (e.code === 'KeyF') toggleFullscreen();
  });
  // Tap/click on the counter screen (not on its controls) also counts
  app.addEventListener('pointerdown', e => {
    if (e.button !== 0 || e.target.closest('.plan, .top, .controls, .hint button, a')) return;
    // First tap after editing the plan only closes the field, it doesn't count
    if (document.activeElement === planInput) { e.preventDefault(); planInput.blur(); return; }
    add(1);
  });
  // Keep a valid plan if the field was left empty
  planInput.addEventListener('blur', () => { planInput.value = state.plan; });

  // Keep the screen on during a workout (the lock is dropped whenever the tab is hidden)
  let wakeLock = null;
  async function keepAwake() {
    if (wakeLock || !navigator.wakeLock || document.visibilityState !== 'visible') return;
    try {
      wakeLock = await navigator.wakeLock.request('screen');
      wakeLock.addEventListener('release', () => { wakeLock = null; });
    } catch (e) {}
  }
  document.addEventListener('pointerdown', keepAwake);
  document.addEventListener('keydown', keepAwake);
  document.addEventListener('visibilitychange', keepAwake);

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
  if (newcomer && state.count === 0 && !state.sets.length) {
    showHint('intro', isTouch
      ? 'Не считайте в уме — касайтесь экрана, а внимание — на технику.'
      : 'Не считайте в уме — жмите пробел, а внимание — на технику.', 7000);
  }
})();
