#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP 3 - Interface Streamlit — Assistant Vocal Mr Smith
Audio natif (st.audio_input) → ASR → LLM (+ émotion webcam) → TTS
"""

import streamlit as st
import numpy as np
import os, sys
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Mr Smith", page_icon="🎙️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #02070d !important;
    color: #a8c8e8;
    font-family: 'JetBrains Mono', monospace;
    overflow-x: hidden;
}
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 800px 600px at 15% 10%, #001f3f44 0%, transparent 70%),
        radial-gradient(ellipse 600px 400px at 85% 80%, #00e5ff08 0%, transparent 70%);
    pointer-events: none; z-index: 0;
}
[data-testid="stSidebar"], header, footer,
[data-testid="stToolbar"], #MainMenu { display: none !important; }
.block-container { padding: 0 1.2rem 4rem !important; max-width: 780px !important; position: relative; z-index: 1; }

#particles-canvas {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none; z-index: 0; opacity: 0.4;
}

.vox-header { padding: 3rem 0 0.5rem; text-align: center; position: relative; }
.vox-title {
    font-family: 'Syne', sans-serif; font-size: 4.5rem; font-weight: 800;
    letter-spacing: -4px; line-height: 1; position: relative; display: inline-block;
    color: transparent; -webkit-text-stroke: 1px #00e5ff44;
}
.vox-title::after {
    content: 'Mr Smith'; position: absolute; inset: 0;
    background: linear-gradient(135deg, #00e5ff, #0077b6 40%, #00e5ff 80%);
    background-size: 200% 200%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: shimmer 3s ease infinite;
}
@keyframes shimmer {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.vox-sub {
    font-size: 0.65rem; letter-spacing: 0.45em; color: #1e4060;
    margin-top: 0.5rem; text-transform: uppercase;
}
.scanner-wrap { position: relative; height: 2px; margin: 1.2rem 0; overflow: hidden; background: #0a1520; }
.scanner-line {
    position: absolute; top: 0; left: -30%; width: 30%; height: 100%;
    background: linear-gradient(90deg, transparent, #00e5ff, transparent);
    animation: scan 2.5s ease-in-out infinite;
}
@keyframes scan { 0% { left: -30%; } 100% { left: 110%; } }

.orb-wrap {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; padding: 1.5rem 0 1rem; gap: 1rem;
}
.orb-ring-container {
    position: relative; width: 160px; height: 160px;
    display: flex; align-items: center; justify-content: center;
}
.orb-ring {
    position: absolute; border-radius: 50%; border: 1px solid rgba(0,229,255,0.15);
    animation: orbPulse 3s ease-in-out infinite;
}
.orb-ring:nth-child(1) { width: 160px; height: 160px; animation-delay: 0s; }
.orb-ring:nth-child(2) { width: 130px; height: 130px; animation-delay: 0.4s; border-color: rgba(0,229,255,0.25); }
.orb-ring:nth-child(3) { width: 100px; height: 100px; animation-delay: 0.8s; border-color: rgba(0,229,255,0.4); }
@keyframes orbPulse {
    0%, 100% { transform: scale(1);    opacity: 0.4; }
    50%       { transform: scale(1.08); opacity: 1; }
}
.orb-core {
    width: 72px; height: 72px; border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #0af5ff, #004d6e 60%, #001a2e);
    box-shadow: 0 0 30px rgba(0,229,255,0.5), 0 0 60px rgba(0,229,255,0.2), inset 0 0 20px rgba(0,229,255,0.3);
    animation: coreBreath 2.5s ease-in-out infinite;
    position: relative; z-index: 2;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem;
}
@keyframes coreBreath {
    0%, 100% { transform: scale(1);    box-shadow: 0 0 30px rgba(0,229,255,0.5), 0 0 60px rgba(0,229,255,0.2); }
    50%       { transform: scale(1.06); box-shadow: 0 0 50px rgba(0,229,255,0.8), 0 0 100px rgba(0,229,255,0.3); }
}
.orb-status {
    font-size: 0.65rem; letter-spacing: 0.3em; text-transform: uppercase;
    color: #1e4060; text-align: center;
}

[data-testid="stAudioInput"], [data-testid="stFileUploader"] {
    background: rgba(8,18,28,0.6) !important;
    border: 1px dashed rgba(0,229,255,0.15) !important;
    border-radius: 12px !important;
}
audio { width: 100%; border-radius: 8px; margin-top: 0.5rem; }

.glass-card {
    background: rgba(10, 22, 35, 0.75);
    border: 1px solid rgba(0, 229, 255, 0.1);
    border-radius: 16px; padding: 1.4rem 1.6rem; margin: 0.8rem 0;
    position: relative; overflow: hidden;
}
.glass-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,229,255,0.4), transparent);
}
.card-label {
    font-size: 0.62rem; letter-spacing: 0.35em; text-transform: uppercase;
    color: #00e5ff; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;
}
.card-label::before { content: ''; width: 16px; height: 1px; background: #00e5ff; display: inline-block; }

.pipe-wrap { display: flex; flex-direction: column; gap: 6px; }
.pipe-step {
    display: flex; align-items: center; gap: 14px;
    padding: 0.85rem 1.1rem; border-radius: 10px;
    border: 1px solid #0f2030; background: rgba(8,18,28,0.8);
    position: relative; overflow: hidden;
    opacity: 0; transform: translateX(-20px);
    animation: stepIn 0.4s ease forwards;
}
.pipe-step::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
    background: #00e5ff; box-shadow: 0 0 10px #00e5ff;
}
.pipe-step.err::before { background: #ff4757; box-shadow: 0 0 10px #ff4757; }
.pipe-step::after {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(90deg, rgba(0,229,255,0.03), transparent 60%);
}
.pipe-step:nth-child(1) { animation-delay: 0.05s; }
.pipe-step:nth-child(2) { animation-delay: 0.15s; }
.pipe-step:nth-child(3) { animation-delay: 0.25s; }
.pipe-step:nth-child(4) { animation-delay: 0.35s; }
.pipe-step:nth-child(5) { animation-delay: 0.45s; }
@keyframes stepIn { to { opacity: 1; transform: translateX(0); } }
.pipe-icon { font-size: 1rem; min-width: 22px; z-index: 1; }
.pipe-lbl { font-size: 0.6rem; letter-spacing: 0.25em; text-transform: uppercase; color: #1e4060; min-width: 72px; z-index: 1; }
.pipe-val { font-size: 0.82rem; color: #c9d8e8; flex: 1; z-index: 1; }
.pipe-badge {
    font-size: 0.65rem; padding: 3px 10px; border-radius: 20px;
    background: rgba(0,229,255,0.08); color: #00e5ff;
    border: 1px solid rgba(0,229,255,0.2); white-space: nowrap; z-index: 1;
}
.pipe-err { color: #ff6b81; font-size: 0.8rem; z-index: 1; }

.response-box {
    position: relative; border-radius: 16px; padding: 2.2rem 2rem;
    margin: 1rem 0; text-align: center; overflow: hidden;
    background: rgba(8,22,38,0.9); border: 1px solid rgba(0,229,255,0.2);
    animation: responseAppear 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.response-box::after {
    content: ''; position: absolute; bottom: 0; left: 10%; right: 10%; height: 1px;
    background: linear-gradient(90deg, transparent, #00e5ff, transparent);
}
@keyframes responseAppear {
    from { opacity: 0; transform: scale(0.95) translateY(20px); }
    to   { opacity: 1; transform: scale(1) translateY(0); }
}
.response-lbl { font-size: 0.6rem; letter-spacing: 0.35em; color: #1e4060; text-transform: uppercase; margin-bottom: 0.8rem; }
.response-txt {
    font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 700;
    color: #e8f4fd; line-height: 1.4;
}

.emo-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(0,229,255,0.06); border: 1px solid rgba(0,229,255,0.2);
    border-radius: 20px; padding: 4px 14px; font-size: 0.65rem; color: #00e5ff;
    margin: 0.4rem 0;
}

.hist-row {
    display: grid; grid-template-columns: 55px 1fr auto auto;
    align-items: center; gap: 12px; padding: 0.75rem 0;
    border-bottom: 1px solid rgba(15,32,48,0.8);
}
.hist-row:last-child { border-bottom: none; }
.hist-t  { font-size: 0.68rem; color: #1e4060; }
.hist-in { font-size: 0.8rem;  color: #c9d8e8; }
.hist-emo { font-size: 0.75rem; }
.hist-badge { font-size: 0.62rem; padding: 2px 9px; border-radius: 20px; background: rgba(0,229,255,0.06); color: #0099bb; border: 1px solid rgba(0,229,255,0.15); }

.vox-divider { height: 1px; background: linear-gradient(90deg, transparent, #0f2030, transparent); margin: 1.2rem 0; }
.stSpinner > div { border-top-color: #00e5ff !important; }
[data-testid="stMarkdownContainer"] p { margin: 0; }
</style>

<canvas id="particles-canvas"></canvas>
<script>
(function(){
    const c = document.getElementById('particles-canvas');
    if(!c) return;
    const ctx = c.getContext('2d');
    let W, H, pts = [];
    function resize(){ W=c.width=window.innerWidth; H=c.height=window.innerHeight; }
    resize();
    window.addEventListener('resize', resize);
    for(let i=0;i<60;i++){
        pts.push({ x:Math.random()*W, y:Math.random()*H,
                   vx:(Math.random()-.5)*.3, vy:(Math.random()-.5)*.3,
                   r:Math.random()*1.5+.5, a:Math.random() });
    }
    function draw(){
        ctx.clearRect(0,0,W,H);
        pts.forEach(p=>{
            p.x+=p.vx; p.y+=p.vy;
            if(p.x<0||p.x>W) p.vx*=-1;
            if(p.y<0||p.y>H) p.vy*=-1;
            ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
            ctx.fillStyle=`rgba(0,229,255,${p.a*0.4})`; ctx.fill();
        });
        for(let i=0;i<pts.length;i++) for(let j=i+1;j<pts.length;j++){
            const dx=pts[i].x-pts[j].x, dy=pts[i].y-pts[j].y, d=Math.sqrt(dx*dx+dy*dy);
            if(d<120){ ctx.beginPath(); ctx.moveTo(pts[i].x,pts[i].y); ctx.lineTo(pts[j].x,pts[j].y);
                       ctx.strokeStyle=`rgba(0,229,255,${(1-d/120)*0.08})`; ctx.stroke(); }
        }
        requestAnimationFrame(draw);
    }
    draw();
})();
</script>
""", unsafe_allow_html=True)

# ════════════════════════ HEADER ════════════════════════
st.markdown("""
<div class="vox-header">
    <div class="vox-title">Mr Smith</div>
    <div class="vox-sub">Assistant Vocal &nbsp;&bull;&nbsp; Émotion Faciale</div>
</div>
<div class="scanner-wrap"><div class="scanner-line"></div></div>
""", unsafe_allow_html=True)

# ════════════════════════ CONFIG ════════════════════════
import requests as _req
OLLAMA_URL   = "http://localhost:11434"
OLLAMA_MODEL = "phi3:mini"
SYSTEM_PROMPT = (
    "Tu es Mr Smith, un assistant vocal empathique en français. "
    "Quand le contexte mentionne l'émotion du visage de l'utilisateur, adapte ta réponse : "
    "réconforte si triste, félicite si joyeux, calme si en colère, rassure si apeuré. "
    "Réponds en une seule phrase courte et naturelle en français."
)

_TP_DIR = str(Path(__file__).parent)
if _TP_DIR not in sys.path:
    sys.path.insert(0, _TP_DIR)

def query_ollama(prompt):
    try:
        r = _req.post(f"{OLLAMA_URL}/api/generate", json={
            "model": OLLAMA_MODEL, "prompt": prompt,
            "system": SYSTEM_PROMPT, "stream": False,
            "options": {"num_predict": 80, "stop": [".", "!", "?"]}
        }, timeout=60)
        r.raise_for_status()
        return r.json()["response"].strip(), True
    except _req.exceptions.ConnectionError:
        return "Ollama non accessible — lance: docker compose up -d", False
    except Exception as e:
        return str(e), False

# ════════════════════════ COMPOSANTS ════════════════════════
@st.cache_resource(show_spinner=False)
def load_components():
    try:
        import imageio_ffmpeg
        _d = str(Path(imageio_ffmpeg.get_ffmpeg_exe()).parent)
        if _d not in os.environ.get("PATH", ""):
            os.environ["PATH"] = _d + os.pathsep + os.environ.get("PATH", "")
    except: pass
    from asr_component import WhisperASR
    from tts_component import PytTTSSynthesizer
    C = {}
    try:
        C["asr"] = WhisperASR(model_size="base")
    except Exception as e:
        print(f"[ERROR] ASR: {e}"); C["asr"] = None
    try:
        C["tts"] = PytTTSSynthesizer()
    except Exception as e:
        print(f"[ERROR] TTS: {e}"); C["tts"] = None
    return C

@st.cache_resource(show_spinner=False)
def load_face_detector():
    try:
        from face_emotion_component import FaceEmotionDetector
        return FaceEmotionDetector()
    except Exception as e:
        print(f"[WARNING] Détecteur émotion non disponible: {e}")
        return None

def detect_emotion_from_image(img_bytes):
    """Détecte l'émotion depuis les bytes d'une image (st.camera_input)."""
    det = load_face_detector()
    if det is None:
        return None
    try:
        import cv2
        arr = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            return None
        dets = det.predict_frame(frame)
        if dets:
            return dets[0]   # {emotion, emoji, confidence, scores, bbox}
    except Exception as e:
        print(f"[WARNING] Émotion: {e}")
    return None

def build_prompt(transcript, emotion):
    """Construit le prompt LLM en incluant l'émotion si disponible."""
    if emotion and emotion.get("confidence", 0) > 0.25:
        prefix = f"[Émotion visage : {emotion['emoji']} {emotion['emotion']} ({emotion['confidence']:.0%})] "
    else:
        prefix = ""
    return f"{prefix}L'utilisateur dit : \"{transcript}\""

def run_pipeline(audio_path, C, emotion=None):
    R = {k: {"ok": False, "error": ""} for k in ["asr", "emotion", "llm", "tts"]}
    # ASR
    if not C.get("asr"):
        R["asr"]["error"] = "ASR non disponible"; return R
    try:
        t, c = C["asr"].transcribe_file(audio_path, language="fr")
        if not t: R["asr"]["error"] = "Transcription vide"; return R
        R["asr"] = {"ok": True, "transcript": t, "confidence": c, "error": ""}
    except Exception as e:
        R["asr"]["error"] = str(e); return R
    # Émotion
    if emotion:
        R["emotion"] = {"ok": True, "emotion": emotion["emotion"],
                        "emoji": emotion["emoji"], "confidence": emotion["confidence"], "error": ""}
    else:
        R["emotion"] = {"ok": False, "error": "aucun visage détecté"}
    # LLM
    prompt = build_prompt(R["asr"]["transcript"], emotion)
    resp, ok = query_ollama(prompt)
    R["llm"] = {"ok": ok, "response": resp, "model": OLLAMA_MODEL,
                "prompt": prompt, "error": "" if ok else resp}
    if not ok: return R
    # TTS
    if C.get("tts"):
        try:
            wav = "_vox_resp.wav"
            C["tts"].synthesize(resp, wav)
            R["tts"] = {"ok": True, "wav": wav, "error": ""}
        except Exception as e:
            R["tts"] = {"ok": False, "wav": None, "error": str(e)}
    return R

# ════════════════════════ SESSION ════════════════════════
if "history" not in st.session_state: st.session_state.history = []

# ════════════════════════ ORBE ════════════════════════
st.markdown("""
<div class="orb-wrap">
    <div class="orb-ring-container">
        <div class="orb-ring"></div>
        <div class="orb-ring"></div>
        <div class="orb-ring"></div>
        <div class="orb-core">🎙</div>
    </div>
    <div class="orb-status">en attente</div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════ WEBCAM (photo) + AUDIO ════════════════════════
col_cam, col_mic = st.columns([1, 1])

with col_cam:
    st.markdown('<div style="font-size:0.58rem;letter-spacing:0.3em;color:#00e5ff;text-transform:uppercase;margin-bottom:0.4rem;">Webcam — émotion</div>', unsafe_allow_html=True)
    cam_img = st.camera_input(" ", label_visibility="collapsed")

with col_mic:
    st.markdown('<div style="font-size:0.58rem;letter-spacing:0.3em;color:#00e5ff;text-transform:uppercase;margin-bottom:0.4rem;">Microphone — parole</div>', unsafe_allow_html=True)
    ab = st.audio_input(" ", label_visibility="collapsed")

# ════════════════════════ ANALYSE AUTOMATIQUE ════════════════════════
audio_path = None
if ab:
    with open("_vox_in.wav", "wb") as f:
        f.write(ab.read())
    audio_path = "_vox_in.wav"

if audio_path:
    st.markdown('<div style="text-align:center;margin:0.5rem 0;font-size:0.65rem;letter-spacing:0.3em;color:#00e5ff;text-transform:uppercase;">◎ analyse en cours...</div>', unsafe_allow_html=True)

    # Détecter l'émotion depuis la photo webcam
    emotion = None
    if cam_img is not None:
        emotion = detect_emotion_from_image(cam_img.getvalue())

    with st.spinner(""):
        C = load_components()
        R = run_pipeline(audio_path, C, emotion=emotion)

    # ── PIPELINE ──
    st.markdown('<div class="glass-card"><div class="card-label">Pipeline</div><div class="pipe-wrap">', unsafe_allow_html=True)
    html = ""

    r = R["asr"]
    if r["ok"]:
        html += f'<div class="pipe-step"><span class="pipe-icon">🎙</span><span class="pipe-lbl">ASR</span><span class="pipe-val">"{r["transcript"]}"</span><span class="pipe-badge">{r["confidence"]:.0%}</span></div>'
    else:
        html += f'<div class="pipe-step err"><span class="pipe-icon">✗</span><span class="pipe-lbl">ASR</span><span class="pipe-err">{r["error"]}</span></div>'

    r = R["emotion"]
    if r["ok"]:
        html += f'<div class="pipe-step"><span class="pipe-icon">{r["emoji"]}</span><span class="pipe-lbl">Émotion</span><span class="pipe-val">{r["emotion"]}</span><span class="pipe-badge">{r["confidence"]:.0%}</span></div>'
    else:
        html += f'<div class="pipe-step err"><span class="pipe-icon">👤</span><span class="pipe-lbl">Émotion</span><span class="pipe-err">{r["error"]}</span></div>'

    r = R["llm"]
    if r["ok"]:
        txt = r["response"][:55] + "…" if len(r["response"]) > 55 else r["response"]
        html += f'<div class="pipe-step"><span class="pipe-icon">🤖</span><span class="pipe-lbl">LLM</span><span class="pipe-val">{txt}</span><span class="pipe-badge">{r["model"]}</span></div>'
    else:
        html += f'<div class="pipe-step err"><span class="pipe-icon">✗</span><span class="pipe-lbl">LLM</span><span class="pipe-err">{r["error"]}</span></div>'

    r = R["tts"]
    if r["ok"]:
        html += '<div class="pipe-step"><span class="pipe-icon">🔊</span><span class="pipe-lbl">TTS</span><span class="pipe-val">audio synthétisé</span></div>'
    elif r.get("error"):
        html += f'<div class="pipe-step err"><span class="pipe-icon">✗</span><span class="pipe-lbl">TTS</span><span class="pipe-err">{r["error"]}</span></div>'

    st.markdown(html + '</div></div>', unsafe_allow_html=True)

    # Badge fusion vocal + émotion
    if R["asr"]["ok"] and R["emotion"]["ok"]:
        e = R["emotion"]
        st.markdown(f'<div><span class="emo-badge">🔗 fusion · vocal + visage · {e["emoji"]} {e["emotion"]}</span></div>', unsafe_allow_html=True)

    # ── RÉPONSE ──
    if R["llm"]["ok"]:
        st.markdown(f'''
        <div class="response-box">
            <div class="response-lbl">Réponse de l\'assistant</div>
            <div class="response-txt">{R["llm"]["response"]}</div>
        </div>''', unsafe_allow_html=True)

    if R["tts"]["ok"] and R["tts"].get("wav") and Path(R["tts"]["wav"]).exists():
        st.audio(R["tts"]["wav"], autoplay=True)

    if R["asr"]["ok"] and R["llm"]["ok"]:
        st.session_state.history.append({
            "time":     datetime.now().strftime("%H:%M:%S"),
            "input":    R["asr"]["transcript"],
            "model":    R["llm"]["model"],
            "emotion":  (R["emotion"]["emoji"] + " " + R["emotion"]["emotion"]) if R["emotion"]["ok"] else "—",
        })

# ════════════════════════ HISTORIQUE ════════════════════════
if st.session_state.history:
    st.markdown('<div class="vox-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><div class="card-label">Historique</div>', unsafe_allow_html=True)
    rows = "".join(
        f'<div class="hist-row"><span class="hist-t">{e["time"]}</span>'
        f'<span class="hist-in">{e["input"]}</span>'
        f'<span class="hist-emo">{e.get("emotion","—")}</span>'
        f'<span class="hist-badge">{e["model"]}</span></div>'
        for e in reversed(st.session_state.history)
    )
    st.markdown(rows + '</div>', unsafe_allow_html=True)
    if st.button("Effacer l'historique"):
        st.session_state.history = []
        st.rerun()
