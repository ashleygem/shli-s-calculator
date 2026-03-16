/* ═══════════════════════════════════════════════════════════════
   Scientific Calculator — Ashley Gem W. Baje
   ashcal.js
   ═══════════════════════════════════════════════════════════════ */

// ─── State ────────────────────────────────────────────────────────────────────
let isDeg   = false;   // false = RAD, true = DEG
let history = [];

// ─── DOM Refs ─────────────────────────────────────────────────────────────────
const displayPanel   = document.getElementById('displayPanel');
const mainDisplay    = document.getElementById('mainDisplay');
const exprLabel      = document.getElementById('exprLabel');
const glowStrip      = document.getElementById('glowStrip');
const modeLabel      = document.getElementById('modeLabel');
const convBtn        = document.getElementById('convBtn');
const historyContent = document.getElementById('historyContent');
const errorToast     = document.getElementById('errorToast');

// ─── Display Helpers ──────────────────────────────────────────────────────────
function getDisplay()    { return mainDisplay.textContent; }
function setDisplay(val) { mainDisplay.textContent = String(val); flashGlow(); }
function setExpr(val)    { exprLabel.textContent   = String(val); }

function appendDisplay(ch) {
  const cur = getDisplay();
  setDisplay(cur === '0' ? ch : cur + ch);
}

function flashGlow() {
  glowStrip.classList.add('flash');
  setTimeout(() => glowStrip.classList.remove('flash'), 80);
}

// ─── Error Toast ──────────────────────────────────────────────────────────────
let toastTimer = null;
function showError(msg = 'Check your values and operators') {
  errorToast.textContent = '⚠ ' + msg;
  errorToast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => errorToast.classList.remove('show'), 2600);
}

// ─── Expression Normalisation for eval ───────────────────────────────────────
function buildEvalExpr(expr) {
  return expr
    .replace(/÷/g, '/')
    .replace(/×/g, '*')
    .replace(/−/g, '-')
    .replace(/\^/g, '**');
}

// ─── Core Actions ─────────────────────────────────────────────────────────────
function doDigit(d) {
  const cur = getDisplay();
  setDisplay(cur === '0' ? d : cur + d);
}

function doOp(sym) {
  setDisplay(getDisplay() + sym);
}

function doClear() {
  setDisplay('0');
  setExpr('');
}

function doDel() {
  const cur = getDisplay();
  if (cur.length <= 1 || cur === 'Error') {
    setDisplay('0');
  } else {
    setDisplay(cur.slice(0, -1) || '0');
  }
}

function doEquals() {
  const expr = getDisplay();
  try {
    const raw    = buildEvalExpr(expr);
    let   result = Function('"use strict"; return (' + raw + ')')();
    if (!isFinite(result)) throw new Error('Result is not finite');
    const formatted = Number.isInteger(result) ? result : parseFloat(result.toFixed(10));
    setExpr(expr + '  =');
    setDisplay(formatted);
    history.push({ expr, result: formatted });
    refreshHistory();
  } catch (e) {
    setDisplay('Error');
    setExpr('');
    setTimeout(() => setDisplay('0'), 1200);
  }
}

// ─── Scientific Operations ────────────────────────────────────────────────────
function toRad(v)   { return isDeg ? v * Math.PI / 180 : v; }
function fromRad(v) { return isDeg ? v * 180 / Math.PI : v; }

const sciActions = {
  sin:  v => Math.sin(toRad(v)),
  cos:  v => Math.cos(toRad(v)),
  tan:  v => Math.tan(toRad(v)),
  asin: v => fromRad(Math.asin(v)),
  acos: v => fromRad(Math.acos(v)),
  atan: v => fromRad(Math.atan(v)),
  sqrt: v => Math.sqrt(v),
  log:  v => Math.log10(v),
  ln:   v => Math.log(v),
  fact: v => { let r = 1; for (let i = 2; i <= Math.round(v); i++) r *= i; return r; },
  rnd:  v => Math.round(v),
};

function doSciOp(fn) {
  try {
    const val = parseFloat(getDisplay());
    if (isNaN(val)) throw new Error('Not a number');
    const result = fn(val);
    if (!isFinite(result) || isNaN(result)) throw new Error('Math error');
    setExpr(getDisplay() + '  =');
    const formatted = Number.isInteger(result) ? result : parseFloat(result.toFixed(10));
    setDisplay(formatted);
    history.push({ expr: getDisplay(), result: formatted });
    refreshHistory();
  } catch (ex) {
    showError(ex.message);
  }
}

// ─── Utility Actions ──────────────────────────────────────────────────────────
function doDot() {
  const cur    = getDisplay();
  const tokens = cur.replace(/[+\-×÷*/()]/g, '|');
  const last   = tokens.split('|').pop();
  if (!last.includes('.')) setDisplay(cur + '.');
}

function doMod()     { setDisplay(getDisplay() + '%'); }
function doLBracket(){ appendDisplay('('); }
function doRBracket(){ appendDisplay(')'); }
function doPow()     { setDisplay(getDisplay() + '^'); }

function doNeg() {
  const cur = getDisplay();
  const val = parseFloat(cur);
  if (!isNaN(val)) {
    setDisplay(cur.startsWith('-') ? Math.abs(val) : -val);
  } else {
    setDisplay('(' + cur + ')*-1');
  }
}

function doPi() { appendDisplay(String(parseFloat(Math.PI.toFixed(10)))); }
function doE()  { appendDisplay(String(parseFloat(Math.E.toFixed(10)))); }

function doConv() {
  isDeg = !isDeg;
  if (isDeg) {
    modeLabel.textContent = 'DEG';
    modeLabel.style.color = 'var(--neon-orange)';
    convBtn.textContent   = 'DEG';
    convBtn.classList.add('deg-mode');
  } else {
    modeLabel.textContent = 'RAD';
    modeLabel.style.color = 'var(--neon-lime)';
    convBtn.textContent   = 'RAD';
    convBtn.classList.remove('deg-mode');
  }
}

// ─── History ──────────────────────────────────────────────────────────────────
function refreshHistory() {
  if (history.length === 0) { historyContent.textContent = '—'; return; }
  const last = history.slice(-3).reverse();
  historyContent.innerHTML = last
    .map(h => `<div>${h.expr} = ${h.result}</div>`)
    .join('');
}

// ─── Button Press Animation ───────────────────────────────────────────────────
function pressAnim(btn) {
  btn.classList.add('pressed');
  setTimeout(() => btn.classList.remove('pressed'), 150);
}

// ─── Dispatch ─────────────────────────────────────────────────────────────────
function dispatch(action, val, btn) {
  if (btn) pressAnim(btn);

  switch (action) {
    case 'digit':    doDigit(val);              break;
    case 'op':       doOp(val);                 break;
    case 'clear':    doClear();                 break;
    case 'del':      doDel();                   break;
    case 'eq':       doEquals();                break;
    case 'dot':      doDot();                   break;
    case 'mod':      doMod();                   break;
    case 'neg':      doNeg();                   break;
    case 'lbracket': doLBracket();              break;
    case 'rbracket': doRBracket();              break;
    case 'pow':      doPow();                   break;
    case 'pi':       doPi();                    break;
    case 'e_const':  doE();                     break;
    case 'conv':     doConv();                  break;
    case 'sin':      doSciOp(sciActions.sin);   break;
    case 'cos':      doSciOp(sciActions.cos);   break;
    case 'tan':      doSciOp(sciActions.tan);   break;
    case 'asin':     doSciOp(sciActions.asin);  break;
    case 'acos':     doSciOp(sciActions.acos);  break;
    case 'atan':     doSciOp(sciActions.atan);  break;
    case 'sqrt':     doSciOp(sciActions.sqrt);  break;
    case 'log':      doSciOp(sciActions.log);   break;
    case 'ln':       doSciOp(sciActions.ln);    break;
    case 'fact':     doSciOp(sciActions.fact);  break;
    case 'rnd':      doSciOp(sciActions.rnd);   break;
  }
}

// ─── Click Binding ────────────────────────────────────────────────────────────
document.querySelectorAll('.btn[data-action]').forEach(btn => {
  btn.addEventListener('click', () => {
    dispatch(btn.dataset.action, btn.dataset.val || null, btn);
  });
});

// ─── Keyboard Binding ────────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  const k = e.key;
  if      (k >= '0' && k <= '9')             dispatch('digit', k);
  else if (k === '+')                         dispatch('op', '+');
  else if (k === '-')                         dispatch('op', '−');
  else if (k === '*')                         dispatch('op', '×');
  else if (k === '/')                       { e.preventDefault(); dispatch('op', '÷'); }
  else if (k === '.')                         dispatch('dot');
  else if (k === '%')                         dispatch('mod');
  else if (k === 'Enter' || k === '=')        dispatch('eq');
  else if (k === 'Backspace')                 dispatch('del');
  else if (k === 'Delete' || k.toLowerCase() === 'c') dispatch('clear');
  else if (k === '(')                         dispatch('lbracket');
  else if (k === ')')                         dispatch('rbracket');
  else if (k === '^')                         dispatch('pow');
});

// ─── Border Glow Pulsation ────────────────────────────────────────────────────
const borderColors = [
  'var(--neon-cyan)',
  'var(--neon-pink)',
  'var(--neon-purple)',
  'var(--neon-lime)',
  'var(--neon-orange)'
];
let borderIdx = 0;

function pulseBorder() {
  displayPanel.style.borderColor = borderColors[borderIdx % borderColors.length];
  borderIdx++;
  setTimeout(pulseBorder, 1800);
}
setTimeout(pulseBorder, 1800);

// ─── Startup Flash ────────────────────────────────────────────────────────────
setTimeout(() => {
  mainDisplay.classList.add('startup-flash');
  setTimeout(() => mainDisplay.classList.remove('startup-flash'), 750);
}, 200);
