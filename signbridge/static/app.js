import { HandLandmarker, FilesetResolver } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/+esm";

const $ = (id) => document.getElementById(id);
const CONNECT = [[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],[13,17],[17,18],[18,19],[19,20],[0,17]];
const api = (url, opt) => fetch(url, opt).then(async (r) => { if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText); return r.json(); });
const post = (url, body) => api(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
function toast(t) { const e = $("toast"); e.textContent = t; e.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => (e.hidden = true), 3200); }

/* ---------- tabs ---------- */
document.querySelectorAll(".tabs button").forEach((b) => b.addEventListener("click", () => {
  document.querySelectorAll(".tabs button").forEach((x) => x.setAttribute("aria-selected", x === b));
  document.querySelectorAll(".view").forEach((v) => (v.hidden = v.id !== "view-" + b.dataset.tab));
}));

/* ---------- status ---------- */
let known = new Set(), status = null;
async function refresh() {
  status = await api("/api/status");
  known = new Set(status.labels.map((l) => l.label.toLowerCase()));
  const m = status.model;
  $("modelState").textContent = m ? `${m.algorithm}, ${(m.accuracy * 100).toFixed(1)}% accuracy` : "No model yet";
  $("modelState").classList.toggle("ok", !!m);
  $("labels").innerHTML = "";
  for (const l of status.labels) {
    const li = document.createElement("li");
    li.className = l.count < status.min_per_label ? "low" : "";
    li.innerHTML = `<span></span><small>${l.count}</small><button aria-label="Delete"></button>`;
    li.firstChild.textContent = l.label; li.lastChild.textContent = "×";
    li.lastChild.onclick = async () => { await api("/api/labels/" + encodeURIComponent(l.label), { method: "DELETE" }); refresh(); };
    $("labels").append(li);
  }
  if (!status.labels.length) $("labels").innerHTML = '<li class="note" style="border:0">No signs yet. Record one above, or import a dataset.</li>';
  if (m) renderScores(m.scores, m.algorithm);
  loadHistory();
}
function renderScores(scores, best) {
  $("scores").innerHTML = Object.entries(scores).sort((a, b) => b[1] - a[1]).map(([k, v]) =>
    `<div class="score ${k === best ? "best" : ""}"><span>${k.replace("_", " ")}</span><i style="--w:${(v * 100).toFixed(0)}%"></i><span>${(v * 100).toFixed(1)}%</span></div>`).join("");
}
async function loadHistory() {
  const h = await api("/api/history");
  $("history").innerHTML = "";
  for (const e of h) { const li = document.createElement("li"); li.innerHTML = "<b></b><span></span>"; li.firstChild.textContent = e.source === "sign" ? "Signed" : "Heard"; li.lastChild.textContent = e.text; $("history").append(li); }
}

/* ---------- training ---------- */
$("trainBtn").onclick = async () => {
  $("trainBtn").disabled = true; $("trainMsg").textContent = "Training five models, this can take a minute…";
  try { const r = await post("/api/train", {}); $("trainMsg").textContent = `Best: ${r.algorithm}`; renderScores(r.scores, r.algorithm); await refresh(); }
  catch (e) { $("trainMsg").textContent = e.message; }
  $("trainBtn").disabled = false;
};

/* ---------- camera + hand tracking ---------- */
let landmarker, current = null, recording = null, ws, lastSend = 0;
const video = $("video"), canvas = $("overlay"), ctx = canvas.getContext("2d");
function connect() {
  ws = new WebSocket(`ws://${location.host}/ws`);
  ws.onmessage = (e) => onPrediction(JSON.parse(e.data));
  ws.onclose = () => setTimeout(connect, 1000);
}
async function startCamera() {
  try {
    video.srcObject = await navigator.mediaDevices.getUserMedia({ video: { width: 960, height: 720 } });
    await video.play();
    const fs = await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm");
    landmarker = await HandLandmarker.createFromOptions(fs, {
      baseOptions: { modelAssetPath: "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" },
      runningMode: "VIDEO", numHands: 1,
    });
    $("camMsg").hidden = true; requestAnimationFrame(loop);
  } catch (e) { $("camMsg").textContent = "Camera unavailable: allow camera access and reload."; }
}
function loop() {
  if (video.videoWidth) {
    canvas.width = video.videoWidth; canvas.height = video.videoHeight;
    const r = landmarker.detectForVideo(video, performance.now());
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (r.landmarks.length) {
      const pts = r.landmarks[0];
      // the image is not mirrored when given to MediaPipe, so its handedness label is flipped
      const hand = r.handednesses[0][0].categoryName === "Left" ? "Right" : "Left";
      current = { landmarks: pts.map((p) => [p.x, p.y, p.z]), hand };
      drawHand(ctx, pts.map((p) => [p.x * canvas.width, p.y * canvas.height]), canvas.width / 160, "#ffcf33", "#fff");
      const now = performance.now();
      if (recording && now - recording.t > 66) { recording.t = now; recording.frames.push(current); }
      if (ws.readyState === 1 && now - lastSend > 70) { lastSend = now; ws.send(JSON.stringify(current)); }
    } else { current = null; onPrediction({ trained: true, label: null, confidence: 0 }); }
  }
  requestAnimationFrame(loop);
}
function drawHand(c, p, w, line, dot) {
  c.lineWidth = w; c.lineCap = "round"; c.strokeStyle = line;
  c.beginPath(); for (const [a, b] of CONNECT) { c.moveTo(...p[a]); c.lineTo(...p[b]); } c.stroke();
  c.fillStyle = dot; for (const q of p) { c.beginPath(); c.arc(q[0], q[1], w * .9, 0, 7); c.fill(); }
}

/* ---------- recognition to sentence ---------- */
const words = []; let hold = { label: null, since: 0 }, lockedUntil = 0;
function onPrediction(p) {
  const strong = p.label && p.confidence >= 0.7;
  $("liveLabel").textContent = p.trained === false ? "?" : strong ? p.label : "–";
  $("meterFill").style.width = strong ? Math.round(p.confidence * 100) + "%" : "0";
  $("liveHint").textContent = p.trained === false ? "Train a model in Signs & training first." : strong ? `${Math.round(p.confidence * 100)}% sure` : "Hold a sign still to add it to your sentence.";
  const now = performance.now();
  if (!strong) { hold = { label: null, since: now }; return; }
  if (hold.label !== p.label) { hold = { label: p.label, since: now }; return; }
  if (now - hold.since > 1000 && now > lockedUntil) { words.push(p.label); lockedUntil = now + 1500; hold.since = now; renderSentence(); }
}
function renderSentence() {
  const s = $("sentence"); s.innerHTML = "";
  if (!words.length) s.innerHTML = '<span class="empty">Your sentence will appear here.</span>';
  for (const w of words) { const e = document.createElement("span"); e.className = "w"; e.textContent = w; s.append(e); }
}
$("undoBtn").onclick = () => { words.pop(); renderSentence(); };
$("clearBtn").onclick = () => { words.length = 0; renderSentence(); };
$("speakBtn").onclick = async () => {
  if (!words.length) return;
  const t = joinWords(words);
  speechSynthesis.speak(new SpeechSynthesisUtterance(t));
  await post("/api/history", { source: "sign", text: t }); loadHistory();
};
// consecutive single letters read as one spelled word: H I -> "HI"
function joinWords(ws) { return ws.reduce((o, w, i) => o + (i && !(w.length === 1 && ws[i - 1].length === 1) ? " " : "") + w, ""); }

/* ---------- teaching ---------- */
$("recForm").onsubmit = async (e) => {
  e.preventDefault();
  if (!landmarker) return toast("Camera is not ready yet.");
  const label = $("recLabel").value.trim(), btn = $("recBtn");
  btn.disabled = true; btn.textContent = "Recording…";
  recording = { frames: [], t: 0 };
  await new Promise((r) => setTimeout(r, 2000));
  const frames = recording.frames; recording = null;
  btn.disabled = false; btn.textContent = "Record 2 seconds";
  if (!frames.length) return toast("No hand seen. Keep your hand in view while recording.");
  await post("/api/samples", { label, frames }); toast(`Saved ${frames.length} samples for "${label}".`); refresh();
};

/* ---------- voice to signs ---------- */
const signCache = new Map();
async function getSign(label) {
  const k = label.toLowerCase();
  if (!signCache.has(k)) { try { signCache.set(k, (await api("/api/sign/" + encodeURIComponent(label))).features); } catch { signCache.set(k, null); } }
  return signCache.get(k);
}
// known word -> its sign; unknown word -> fingerspelled with letter signs when they exist
async function plan(text) {
  const out = [];
  for (const raw of text.toLowerCase().match(/[\p{L}\p{N}']+/gu) || []) {
    const w = raw.replace(/'/g, "");
    if (known.has(w)) { out.push({ label: w, f: await getSign(w) }); continue; }
    const letters = [...w];
    if (letters.every((c) => known.has(c))) { for (const c of letters) out.push({ label: c, f: await getSign(c), spelled: true }); }
    else out.push({ label: w, f: null });
  }
  return out;
}
let playId = 0;
async function showSigns(text) {
  const id = ++playId, steps = await plan(text), box = $("tiles"); box.innerHTML = "";
  if (!steps.length) return;
  const els = steps.map((s) => {
    const d = document.createElement("div"); d.className = "tile" + (s.f ? "" : " miss");
    const cv = document.createElement("canvas"); cv.width = cv.height = 224;
    const sp = document.createElement("span"); sp.textContent = s.f ? s.label : `${s.label} (no sign yet)`;
    d.append(cv, sp); box.append(d);
    if (s.f) paintSign(cv, s.f);
    return d;
  });
  await post("/api/history", { source: "speech", text });
  for (let i = 0; i < steps.length && id === playId; i++) {
    if (!steps[i].f) continue;
    els.forEach((e, j) => e.classList.toggle("on", j === i));
    await new Promise((r) => setTimeout(r, steps[i].spelled ? 600 : 900));
  }
  els.forEach((e) => e.classList.remove("on")); loadHistory();
}
function paintSign(cv, f) {
  const c = cv.getContext("2d"), pts = [];
  for (let i = 0; i < 21; i++) pts.push([f[i * 3], f[i * 3 + 1]]);
  // features are wrist-centred and scaled to [-1,1]; fit them into the tile
  const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
  const minx = Math.min(...xs), maxx = Math.max(...xs), miny = Math.min(...ys), maxy = Math.max(...ys);
  const s = (cv.width - 40) / Math.max(maxx - minx, maxy - miny || 1);
  const mapped = pts.map(([x, y]) => [20 + (x - minx) * s + (cv.width - 40 - (maxx - minx) * s) / 2, 20 + (y - miny) * s + (cv.width - 40 - (maxy - miny) * s) / 2]);
  const dark = matchMedia("(prefers-color-scheme: dark)").matches;
  drawHand(c, mapped, 7, dark ? "#6f8bff" : "#2346f0", dark ? "#e8eef4" : "#13202c");
}
$("typeForm").onsubmit = (e) => { e.preventDefault(); const t = $("typeIn").value.trim(); if (t) { $("heard").textContent = t; showSigns(t); } };

const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let rec = null;
$("listenBtn").onclick = () => {
  if (!SR) return toast("Speech recognition needs Chrome or Edge.");
  if (rec) { rec.stop(); return; }
  rec = new SR(); rec.lang = $("lang").value; rec.interimResults = true; rec.continuous = true;
  rec.onstart = () => { $("listenBtn").textContent = "Stop listening"; $("heard").textContent = "Listening…"; };
  rec.onresult = (e) => {
    let interim = "", final = "";
    for (let i = e.resultIndex; i < e.results.length; i++) (e.results[i].isFinal ? (final += e.results[i][0].transcript) : (interim += e.results[i][0].transcript));
    $("heard").classList.add("live"); $("heard").textContent = final || interim;
    if (final.trim()) showSigns(final);
  };
  rec.onerror = (e) => toast(e.error === "not-allowed" ? "Microphone access was blocked." : "Speech error: " + e.error);
  rec.onend = () => { rec = null; $("listenBtn").textContent = "Start listening"; $("heard").classList.remove("live"); };
  rec.start();
};

connect(); refresh(); startCamera();
