(() => {
  // Each exercise keeps its own state, shared by its translations:
  // <body data-store="otzhimaniya" data-default-plan="20" data-root="../">
  const { store = '', defaultPlan = '10', root = './' } = document.body.dataset;
  const KEY = 'rep-counter-v1' + (store ? ':' + store : '');
  const lang = document.documentElement.lang === 'ru' ? 'ru' : 'en';
  const T = {
    en: {
      sets: (list, total) => `Sets: ${list}  —  workout total: ${total}`,
      reset: 'Reset the counter and sets?',
      hide: 'Don’t show tips again',
      // The "one rep at a time" method: never look past the next rep
      intro: ['Just one rep. Do it, then press space.', 'Just one rep. Do it, then tap the screen.'],
      first: 'One done. Now just one more.',
      half: n => `You didn’t do half. You did one, ${n} times.`,
      done: [n => n >= 3 ? `${n} times just one. That’s all it took.` : 'Done. One at a time.',
        'Done. You decided — and you did it.', 'Done. One more small win.'],
      pause: ['Forget the rest. Just the next one. The 1× button hides the goal.',
        'Forget the rest. Just the next one.'],
      oneOn: '“Just one” mode: no goal, no countdown. Only the next rep.',
      oneStep: n => `${n} times just one.`,
      set: 'Set saved. Rest — then again, just one.',
      offer: 'Эта страница есть на русском', offerGo: 'Открыть',
    },
    ru: {
      sets: (list, total) => `Подходы: ${list}  —  всего за тренировку: ${total}`,
      reset: 'Сбросить счётчик и подходы?',
      hide: 'Больше не показывать подсказки',
      intro: ['Только одно повторение. Сделайте — и нажмите пробел.',
        'Только одно повторение. Сделайте — и коснитесь экрана.'],
      first: 'Одно есть. Теперь — ещё одно.',
      half: n => `Вы не делали половину — вы сделали ${n} раз по одному.`,
      done: [n => n >= 3 ? `${n} раз по одному. Вот и всё.` : 'Сделано. По одному.',
        'Сделано. Вы решили — и выполнили.', 'Готово. Ещё одна маленькая победа.'],
      pause: ['Не думайте обо всех — только о следующем. Кнопка 1× скроет план.',
        'Не думайте обо всех. Только о следующем.'],
      oneOn: 'Режим «Только одно»: без плана и остатка. Только следующее.',
      oneStep: n => `${n} раз по одному.`,
      set: 'Подход записан. Отдохните — и снова только одно.',
      offer: 'This page is also in English', offerGo: 'Open',
    },
  }[lang];
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
    $('sets').textContent = state.sets.length ? T.sets(state.sets.join(' · '), sum + state.count) : '';
    $('sound').setAttribute('aria-pressed', state.sound);
    $('sound').textContent = state.sound ? '🔊' : '🔇';
    if (bump) { const c = $('count'); c.classList.remove('bump'); void c.offsetWidth; c.classList.add('bump'); }
    save();
  }

  // ---- Hints: short lines at key moments of a workout. Built by script only, so
  // they are not part of the page text that search engines index.
  const HINTS_KEY = 'rep-counter-hints';
  const isTouch = matchMedia('(hover: none)').matches;
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
  hintBox.innerHTML = `<span></span><button type="button" aria-label="${T.hide}" title="${T.hide}">×</button>`;
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
    const { count, plan } = state;
    if (count === 1 && newcomer) return showHint('first', T.first);
    // "Just one" mode hides the goal, so hints don't mention it either
    if (oneMode) { if (count % 5 === 0) showHint('one' + count, T.oneStep(count)); return; }
    if (count === plan) {
      const line = T.done[doneLine++ % T.done.length];
      showHint('done', typeof line === 'function' ? line(count) : line);
    } else if (count === Math.ceil(plan / 2) && plan >= 6) showHint('half', T.half(count));
  }

  // A long pause between reps is when it's hardest: remind to think only of the next one
  const PAUSE_MS = 15000;
  let pauseTimer, pauses = 0;
  function watchPause() {
    clearTimeout(pauseTimer);
    pauseTimer = setTimeout(() => {
      if (document.hidden || state.count === 0 || (!oneMode && state.count >= state.plan) || pauses >= 2) return;
      showHint('pause' + pauses, T.pause[pauses === 0 && !oneMode ? 0 : 1], 6000);
      pauses++;
    }, PAUSE_MS);
  }

  // "Just one" mode: only the count is on screen, no goal and no countdown
  const ONE_KEY = 'rep-counter-one';
  let oneMode = false;
  try { oneMode = localStorage.getItem(ONE_KEY) === '1'; } catch (e) {}
  function applyOne() {
    app.classList.toggle('one', oneMode);
    $('one').setAttribute('aria-pressed', oneMode);
  }
  function toggleOne() {
    oneMode = !oneMode;
    try { localStorage.setItem(ONE_KEY, oneMode ? '1' : '0'); } catch (e) {}
    applyOne();
    if (oneMode) showHint('oneOn', T.oneOn, 5000);
  }

  function add(n) {
    state.count = Math.max(state.count + n, 0);
    if (n > 0) {
      const reached = state.count === state.plan;
      beep(reached ? 1320 : 880, reached ? 400 : 80);
      vibrate(reached ? [80, 60, 80, 60, 200] : 25);
    }
    render(n > 0);
    if (n > 0) { hintForCount(); watchPause(); }
  }

  function finishSet() {
    if (state.count > 0) {
      state.sets.push(state.count); state.count = 0; render(); clearTimeout(pauseTimer);
      if (newcomer) showHint('set', T.set);
    }
  }

  function reset() {
    if (confirm(T.reset)) {
      state.count = 0; state.sets = []; render();
      shown.clear(); hideHint(); clearTimeout(pauseTimer); pauses = 0;
    }
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
    fullscreen: toggleFullscreen, one: toggleOne,
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
    if (e.button !== 0 || e.target.closest('.plan, .top, .controls, .hint button, .lang-offer, a')) return;
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

  applyOne();
  render();
  if (newcomer && state.count === 0 && !state.sets.length) showHint('intro', T.intro[isTouch ? 1 : 0], 7000);

  // ---- Offer the other language when the browser prefers it. Script-only, never a
  // redirect: search engines and people who chose this language stay on this page.
  const LANG_KEY = 'rep-counter-lang';
  // the footer link is relative, so it also works on a local copy of the site
  const alt = document.querySelector(`footer a[hreflang="${lang === 'en' ? 'ru' : 'en'}"]`);
  const prefersRu = (navigator.languages || [navigator.language || ''])
    .slice(0, 2).some(l => /^(ru|uk|be|kk)\b/i.test(l));
  let langChoice = null;
  try { langChoice = localStorage.getItem(LANG_KEY); } catch (e) {}
  // Remember a language picked from the footer link, so we stop offering
  document.querySelectorAll('footer a[hreflang]').forEach(a => a.addEventListener('click', () => {
    try { localStorage.setItem(LANG_KEY, a.hreflang); } catch (e) {}
  }));
  if (alt && !langChoice && (lang === 'en') === prefersRu) {
    const offer = document.createElement('div');
    offer.className = 'lang-offer';
    offer.lang = lang === 'en' ? 'ru' : 'en';
    offer.innerHTML = `<span>${T.offer}</span> <a href="${alt.href}">${T.offerGo}</a>`
      + `<button type="button" aria-label="×">×</button>`;
    const remember = v => { try { localStorage.setItem(LANG_KEY, v); } catch (e) {} };
    offer.querySelector('a').addEventListener('click', () => remember(offer.lang));
    offer.querySelector('button').addEventListener('click', () => { remember(lang); offer.remove(); });
    document.querySelector('.plan').before(offer);
  }
})();
