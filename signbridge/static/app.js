// Signbridge frontend: MediaPipe finds the hand in the browser, Python recognises the sign.
const HOLD_MS = 700;   // how long a sign must be held to become a word
const MIN_CONF = 0.8;  // minimum model confidence
const SHOTS = 40;      // samples captured per recording
const BONES = [[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],
               [9,13],[13,14],[14,15],[15,16],[13,17],[17,18],[18,19],[19,20],[0,17]];

const $ = s => document.querySelector(s);
const el = (tag, cls, text) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text) e.textContent = text;
  return e;
};

const video = $('#cam'), overlay = $('#overlay'), octx = overlay.getContext('2d');
const nowWord = $('#nowWord'), holdBar = $('#hold'), lang = $('#lang');

let ws, inflight = false, frame = null;           // frame = {landmarks, hand} while a hand is visible
let stable = null, since = 0, committed = null;   // hold-to-commit state
let sentence = [], rec = null, lastShot = 0;

async function api(path, body, method) {
  const r = await fetch(path, {
    method: method || (body ? 'POST' : 'GET'),
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || r.statusText);
  return data;
}

// ---------- drawing ----------
function drawHand(ctx, pts, boneColor, dotColor, width) {
  ctx.lineWidth = width; ctx.lineCap = 'round'; ctx.strokeStyle = boneColor;
  ctx.beginPath();
  for (const [a, b] of BONES) { ctx.moveTo(...pts[a]); ctx.lineTo(...pts[b]); }
  ctx.stroke();
  ctx.fillStyle = dotColor;
  for (const [x, y] of pts) { ctx.beginPath(); ctx.arc(x, y, width * 0.9, 0, Math.PI * 2); ctx.fill(); }
}

function drawCard(canvas, f) {  // f = 63 normalised features
  const ctx = canvas.getContext('2d'), pad = 16;
  const pts = Array.from({ length: 21 }, (_, i) => [-f[i * 3], f[i * 3 + 1]]);  // mirrored like the preview
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  const x0 = Math.min(...xs), y0 = Math.min(...ys);
  const w = Math.max(...xs) - x0 || 1, h = Math.max(...ys) - y0 || 1;
  const s = Math.min((canvas.width - 2 * pad) / w, (canvas.height - 2 * pad) / h);
  const ox = (canvas.width - w * s) / 2, oy = (canvas.height - h * s) / 2;
  drawHand(ctx, pts.map(([x, y]) => [ox + (x - x0) * s, oy + (y - y0) * s]), '#2f5bff', '#14213d', 3);
}

// ---------- live caption ----------
function showLive(word, progress = 0, msg) {
  nowWord.textContent = word || msg || (frame ? '…' : 'Show a sign');
  nowWord.classList.toggle('idle', !word);
  holdBar.style.width = `${progress * 100}%`;
}

function onPrediction(p) {
  if (!frame) return;
  if (!p.trained) return showLive(null, 0, 'Teach a few signs, then train the model');
  if (!p.label || p.confidence < MIN_CONF) { stable = null; return showLive(null); }
  if (p.label !== stable) { stable = p.label; since = performance.now(); }
  const held = performance.now() - since;
  showLive(p.label, Math.min(held / HOLD_MS, 1));
  if (held >= HOLD_MS && p.label !== committed) {
    committed = p.label;
    sentence.push(p.label);
    renderSentence();
  }
}

// ---------- websocket ----------
function setPill(text, live) { const p = $('#pill'); p.textContent = text; p.classList.toggle('live', live); }

function connect() {
  ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`);
  ws.onopen = () => setPill('connected', true);
  ws.onclose = () => { inflight = false; setPill('reconnecting', false); setTimeout(connect, 1000); };
  ws.onmessage = e => { inflight = false; onPrediction(JSON.parse(e.data)); };
}

// ---------- camera + hand tracking ----------
function onHands(res) {
  octx.clearRect(0, 0, overlay.width, overlay.height);
  const lm = res.multiHandLandmarks && res.multiHandLandmarks[0];
  if (!lm) { frame = null; stable = committed = null; if (!rec) showLive(null); return; }
  frame = { landmarks: lm.map(p => [p.x, p.y, p.z]), hand: res.multiHandedness[0].label };
  drawHand(octx, lm.map(p => [p.x * overlay.width, p.y * overlay.height]), '#ff7a1a', '#ffffff', 3);
  if (rec) capture();
  else if (!inflight && ws && ws.readyState === 1) { inflight = true; ws.send(JSON.stringify(frame)); }
}

async function start() {
  const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 960, height: 540 }, audio: false });
  video.srcObject = stream;
  await video.play();
  overlay.width = video.videoWidth; overlay.height = video.videoHeight;
  $('#stage').style.aspectRatio = `${video.videoWidth} / ${video.videoHeight}`;

  const hands = new Hands({ locateFile: f => `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469240/${f}` });
  hands.setOptions({ maxNumHands: 1, modelComplexity: 1, minDetectionConfidence: 0.6, minTrackingConfidence: 0.5 });
  hands.onResults(onHands);
  const loop = async () => { await hands.send({ image: video }); requestAnimationFrame(loop); };
  loop();
}

// ---------- sentence + history ----------
function renderSentence() {
  $('#sentence').replaceChildren(...sentence.map(w => el('span', 'word', w)));
}

function speak(text) {
  if (!text) return;
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang.value;
  speechSynthesis.cancel();
  speechSynthesis.speak(u);
}

async function loadHistory() {
  const rows = await api('/api/history');
  $('#history').replaceChildren(...rows.map(r => {
    const li = el('li');
    li.append(el('b', '', r.source === 'sign' ? 'Signed' : 'Spoken'), document.createTextNode(r.text));
    return li;
  }));
}

$('#speak').onclick = () => {
  const text = sentence.join(' ');
  if (!text) return;
  speak(text);
  api('/api/history', { source: 'sign', text }).then(loadHistory);
};
$('#undo').onclick = () => { sentence.pop(); renderSentence(); };
$('#clear').onclick = () => { sentence = []; renderSentence(); };

// ---------- teach: record samples ----------
const recBtn = $('#record'), recStatus = $('#recStatus');

recBtn.onclick = () => {
  const label = $('#label').value.trim();
  if (!label) { recStatus.textContent = 'Type the word for this sign first.'; return; }
  if (rec) return;
  rec = { label, frames: [], start: performance.now() + 2000 };
  recBtn.disabled = true;
  const tick = setInterval(() => {
    if (!rec) return clearInterval(tick);
    const left = rec.start - performance.now();
    recStatus.textContent = left > 0 ? `Get ready… ${Math.ceil(left / 1000)}`
      : frame ? `Recording ${rec.frames.length} of ${SHOTS}` : 'Show your hand to the camera.';
  }, 150);
};

function capture() {
  const now = performance.now();
  if (now < rec.start || now - lastShot < 80) return;
  lastShot = now;
  rec.frames.push(frame);
  if (rec.frames.length >= SHOTS) finishRecording();
}

async function finishRecording() {
  const { label, frames } = rec;
  rec = null;
  recBtn.disabled = false;
  try {
    await api('/api/samples', { label, frames });
    recStatus.textContent = `Saved ${frames.length} samples for “${label}”. Record another round or a new sign.`;
  } catch (e) { recStatus.textContent = e.message; }
  refresh();
}

// ---------- teach: labels + training ----------
async function refresh() {
  const s = await api('/api/status');
  $('#labels').replaceChildren(...s.labels.map(l => {
    const chip = el('span', 'chip', l.label);
    const del = el('button', '', '×');
    del.title = `Delete “${l.label}”`;
    del.onclick = async () => { await api(`/api/labels/${encodeURIComponent(l.label)}`, null, 'DELETE'); refresh(); };
    chip.append(el('em', '', String(l.count)), del);
    return chip;
  }));
  $('#train').disabled = s.labels.length < 2;
  const m = s.model;
  $('#modelInfo').textContent = m
    ? `Active model: ${m.algorithm}, ${Math.round(m.accuracy * 100)}% accuracy on ${m.n_samples} samples.`
    : `No model trained yet. Record at least 2 signs (${s.min_per_label}+ samples each).`;
  $('#scores').textContent = m
    ? 'Compared: ' + Object.entries(m.scores).map(([k, v]) => `${k} ${Math.round(v * 100)}%`).join(', ')
    : '';
}

$('#train').onclick = async e => {
  const btn = e.currentTarget;
  btn.disabled = true; btn.textContent = 'Training…';
  let error = '';
  try { await api('/api/train', {}); } catch (err) { error = err.message; }
  btn.textContent = 'Train model';
  await refresh();
  if (error) $('#modelInfo').textContent = error;
};

// ---------- voice to signs ----------
async function showSigns(text, save) {
  const known = new Map((await api('/api/status')).labels.map(l => [l.label.toLowerCase(), l.label]));
  const cards = text.split(/\s+/).filter(Boolean).map(word => {
    const key = word.toLowerCase().replace(/[^\p{L}\p{N}'-]/gu, '');
    const card = el('figure', 'sign');
    if (known.has(key)) {
      const c = document.createElement('canvas');
      c.width = c.height = 120;
      card.append(c);
      api(`/api/sign/${encodeURIComponent(known.get(key))}`).then(d => drawCard(c, d.features));
    } else {
      card.classList.add('unknown');
      card.append(el('div', 'blank', '?'));
    }
    card.append(el('figcaption', '', word));
    return card;
  });
  $('#signs').replaceChildren(...cards);
  if (save) api('/api/history', { source: 'speech', text }).then(loadHistory);
}

$('#show').onclick = () => showSigns($('#text').value, true);
$('#text').onkeydown = e => { if (e.key === 'Enter') showSigns(e.target.value, true); };

$('#mic').onclick = () => {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { alert('Speech recognition needs Chrome or Edge.'); return; }
  const r = new SR();
  r.lang = lang.value;
  r.interimResults = true;
  $('#mic').classList.add('on');
  r.onresult = e => {
    const results = Array.from(e.results);
    const text = results.map(x => x[0].transcript).join(' ');
    $('#text').value = text;
    if (results[results.length - 1].isFinal) showSigns(text, true);
  };
  r.onend = () => $('#mic').classList.remove('on');
  r.start();
};

// ---------- go ----------
refresh();
loadHistory();
connect();
start().catch(err => showLive(null, 0, `Camera unavailable: ${err.message}`));
