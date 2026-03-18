#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP 3 - Interface Streamlit — Assistant Vocal Mr Smith
Auto-analyse dès l'enregistrement + orbe vocal animé
"""

import streamlit as st
import numpy as np
import soundfile as sf
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

/* ── HEADER ── */
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
    animation: fadeInUp 1s ease 0.3s both;
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.scanner-wrap { position: relative; height: 2px; margin: 1.2rem 0; overflow: hidden; background: #0a1520; }
.scanner-line {
    position: absolute; top: 0; left: -30%; width: 30%; height: 100%;
    background: linear-gradient(90deg, transparent, #00e5ff, transparent);
    animation: scan 2.5s ease-in-out infinite;
}
@keyframes scan { 0% { left: -30%; } 100% { left: 110%; } }

/* ── ORBE VOCAL ── */
.orb-wrap {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; padding: 1.5rem 0 1rem;
    gap: 1rem;
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
/* Orbe en mode "parle" */
.orb-core.speaking {
    animation: coreTalk 0.15s ease-in-out infinite alternate;
    background: radial-gradient(circle at 35% 35%, #ff0af5, #6e004d 60%, #1a001e);
    box-shadow: 0 0 30px rgba(255,0,200,0.6), 0 0 80px rgba(255,0,200,0.3);
}
@keyframes coreTalk {
    from { transform: scale(0.95); }
    to   { transform: scale(1.12); }
}
.orb-ring.speaking {
    border-color: rgba(255,0,200,0.3);
    animation: orbTalk 0.3s ease-in-out infinite alternate;
}
@keyframes orbTalk {
    from { transform: scale(1); }
    to   { transform: scale(1.1); opacity: 0.8; }
}
.orb-status {
    font-size: 0.65rem; letter-spacing: 0.3em; text-transform: uppercase;
    color: #1e4060; text-align: center;
    animation: fadeInUp 0.3s ease;
}
.orb-status.active { color: #00e5ff; }

/* Waveform live (pendant analyse) */
.live-wave {
    display: flex; align-items: center; justify-content: center;
    gap: 3px; height: 40px;
}
.lw-bar {
    width: 3px; border-radius: 3px;
    background: linear-gradient(to top, #004d6e, #00e5ff);
    animation: lw 0.8s ease-in-out infinite;
    transform-origin: bottom;
}
.lw-bar:nth-child(1)  { height:8px;  animation-delay:0.00s; }
.lw-bar:nth-child(2)  { height:18px; animation-delay:0.06s; }
.lw-bar:nth-child(3)  { height:28px; animation-delay:0.12s; }
.lw-bar:nth-child(4)  { height:20px; animation-delay:0.18s; }
.lw-bar:nth-child(5)  { height:34px; animation-delay:0.24s; }
.lw-bar:nth-child(6)  { height:26px; animation-delay:0.30s; }
.lw-bar:nth-child(7)  { height:36px; animation-delay:0.36s; }
.lw-bar:nth-child(8)  { height:26px; animation-delay:0.42s; }
.lw-bar:nth-child(9)  { height:34px; animation-delay:0.48s; }
.lw-bar:nth-child(10) { height:20px; animation-delay:0.54s; }
.lw-bar:nth-child(11) { height:28px; animation-delay:0.60s; }
.lw-bar:nth-child(12) { height:16px; animation-delay:0.66s; }
.lw-bar:nth-child(13) { height:8px;  animation-delay:0.72s; }
@keyframes lw {
    0%,100% { transform: scaleY(0.25); opacity:0.3; }
    50%      { transform: scaleY(1);   opacity:1; }
}

/* ── TABS ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(8,18,28,0.8) !important;
    border: 1px solid rgba(0,229,255,0.1) !important;
    border-radius: 12px !important; padding: 5px !important; gap: 4px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important; color: #2a5070 !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 0.78rem !important;
    letter-spacing: 0.08em !important; border-radius: 9px !important;
    border: none !important; padding: 0.55rem 1.4rem !important; transition: all 0.25s !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: rgba(0,229,255,0.08) !important; color: #00e5ff !important;
    border: 1px solid rgba(0,229,255,0.2) !important;
    box-shadow: 0 0 20px rgba(0,229,255,0.1) !important;
}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

[data-testid="stAudioInput"], [data-testid="stFileUploader"] {
    background: rgba(8,18,28,0.6) !important;
    border: 1px dashed rgba(0,229,255,0.15) !important;
    border-radius: 12px !important; transition: border-color 0.3s !important;
}
[data-testid="stFileUploader"] label, [data-testid="stAudioInput"] label {
    color: #2a5070 !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.78rem !important;
}
audio { width: 100%; border-radius: 8px; margin-top: 0.5rem; }

/* ── GLASS CARD ── */
.glass-card {
    background: rgba(10, 22, 35, 0.75);
    border: 1px solid rgba(0, 229, 255, 0.1);
    border-radius: 16px; padding: 1.4rem 1.6rem; margin: 0.8rem 0;
    position: relative; overflow: hidden; backdrop-filter: blur(10px);
    transition: border-color 0.3s, box-shadow 0.3s;
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

/* ── PIPELINE ── */
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
    border: 1px solid rgba(0,229,255,0.2); white-space: nowrap;
    z-index: 1; box-shadow: 0 0 12px rgba(0,229,255,0.1);
}
.pipe-err { color: #ff6b81; font-size: 0.8rem; z-index: 1; }

/* ── RÉPONSE ── */
.response-box {
    position: relative; border-radius: 16px; padding: 2.2rem 2rem;
    margin: 1rem 0; text-align: center; overflow: hidden;
    background: rgba(8,22,38,0.9); border: 1px solid rgba(0,229,255,0.2);
    animation: responseAppear 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.response-box::after {
    content: ''; position: absolute; bottom: 0; left: 10%; right: 10%; height: 1px;
    background: linear-gradient(90deg, transparent, #00e5ff, transparent);
    box-shadow: 0 0 20px #00e5ff; animation: pulseLine 2s ease infinite;
}
@keyframes pulseLine { 0%,100% { opacity:0.5; } 50% { opacity:1; } }
@keyframes responseAppear {
    from { opacity: 0; transform: scale(0.95) translateY(20px); }
    to   { opacity: 1; transform: scale(1) translateY(0); }
}
.response-lbl { font-size: 0.6rem; letter-spacing: 0.35em; color: #1e4060; text-transform: uppercase; margin-bottom: 0.8rem; }
.response-txt {
    font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 700;
    color: #e8f4fd; line-height: 1.4; text-shadow: 0 0 40px rgba(0,229,255,0.2);
}

/* ── HISTORIQUE ── */
.hist-row {
    display: grid; grid-template-columns: 55px 1fr auto;
    align-items: center; gap: 12px; padding: 0.75rem 0;
    border-bottom: 1px solid rgba(15,32,48,0.8);
    animation: fadeIn 0.3s ease;
}
.hist-row:last-child { border-bottom: none; }
@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
.hist-t  { font-size: 0.68rem; color: #1e4060; }
.hist-in { font-size: 0.8rem;  color: #c9d8e8; }
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
    <div class="vox-sub">Assistant Vocal &nbsp</div>
</div>
<div class="scanner-wrap"><div class="scanner-line"></div></div>
""", unsafe_allow_html=True)

# ════════════════════════ CONFIG OLLAMA ════════════════════════
import requests as _req
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "phi3:mini"
SYSTEM_PROMPT = "Tu es un assistant vocal en français. Réponds en une seule phrase courte et naturelle."

_TP_DIR = str(Path(__file__).parent)
if _TP_DIR not in sys.path:
    sys.path.insert(0, _TP_DIR)

def query_ollama(prompt):
    try:
        r = _req.post(f"{OLLAMA_URL}/api/generate", json={
            "model": OLLAMA_MODEL, "prompt": prompt,
            "system": SYSTEM_PROMPT, "stream": False,
            "options": {"num_predict": 60, "stop": [".", "!", "?"]}
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

def run_pipeline(audio_path, C):
    R = {k: {"ok": False, "error": ""} for k in ["asr", "llm", "tts"]}
    if not C.get("asr"):
        R["asr"]["error"] = "ASR non disponible"; return R
    try:
        t, c = C["asr"].transcribe_file(audio_path, language="fr")
        if not t: R["asr"]["error"] = "Transcription vide"; return R
        R["asr"] = {"ok": True, "transcript": t, "confidence": c, "error": ""}
    except Exception as e: R["asr"]["error"] = str(e); return R
    resp, ok = query_ollama(R["asr"]["transcript"])
    R["llm"] = {"ok": ok, "response": resp, "model": OLLAMA_MODEL, "error": "" if ok else resp}
    if not ok: return R
    if C.get("tts"):
        try:
            wav = "_vox_resp.wav"; C["tts"].synthesize(resp, wav)
            R["tts"] = {"ok": True, "wav": wav, "error": ""}
        except Exception as e: R["tts"] = {"ok": False, "wav": None, "error": str(e)}
    return R

# ════════════════════════ ORBE + INPUT ════════════════════════
if "history" not in st.session_state: st.session_state.history = []
if "last_audio_hash" not in st.session_state: st.session_state.last_audio_hash = None

# Orbe — état initial : en attente
st.markdown("""
<div class="orb-wrap">
    <div class="orb-ring-container">
        <div class="orb-ring"></div>
        <div class="orb-ring"></div>
        <div class="orb-ring"></div>
        <div class="orb-core">🎙</div>
    </div>
    <div class="orb-status">en attente</div>
    <div class="live-wave">
        <div class="lw-bar"></div><div class="lw-bar"></div><div class="lw-bar"></div>
        <div class="lw-bar"></div><div class="lw-bar"></div><div class="lw-bar"></div>
        <div class="lw-bar"></div><div class="lw-bar"></div><div class="lw-bar"></div>
        <div class="lw-bar"></div><div class="lw-bar"></div><div class="lw-bar"></div>
        <div class="lw-bar"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABS INPUT ──
tab_mic, tab_file = st.tabs(["⬤  Microphone", "↑  Fichier WAV"])
audio_path = None

with tab_mic:
    ab = st.audio_input(" ", label_visibility="collapsed")
    if ab:
        data = ab.read()
        h = hash(data)
        with open("_vox_in.wav","wb") as f: f.write(data)
        audio_path = "_vox_in.wav"
        st.session_state.last_audio_hash = h

with tab_file:
    up = st.file_uploader(" ", type=["wav","mp3"], label_visibility="collapsed")
    if up:
        data = up.read()
        h = hash(data)
        with open("_vox_in.wav","wb") as f: f.write(data)
        audio_path = "_vox_in.wav"
        st.audio("_vox_in.wav")
        st.session_state.last_audio_hash = h

# ════════════════════════ AUTO-ANALYSE ════════════════════════
if audio_path:
    # Orbe "analyse en cours" — waveform rose/violet
    st.markdown("""
    <div style="text-align:center; margin: 0.5rem 0;">
        <div style="font-size:0.65rem; letter-spacing:0.3em; color:#00e5ff; text-transform:uppercase;
                    animation: fadeInUp 0.3s ease;">
            ◎ analyse en cours...
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(""):
        C = load_components()
        R = run_pipeline(audio_path, C)

    # ── PIPELINE ──
    st.markdown('<div class="glass-card"><div class="card-label">Pipeline</div><div class="pipe-wrap">', unsafe_allow_html=True)
    steps = [
        ("asr", "🎙", "ASR",
         lambda r: (f'"{r["transcript"]}"', f'{r["confidence"]:.0%}')),
        ("llm", "🤖", "LLM",
         lambda r: (r["response"][:55] + "…" if len(r["response"]) > 55 else r["response"], r["model"])),
        ("tts", "🔊", "TTS",
         lambda r: ("audio synthétisé", "")),
    ]
    html = ""
    for key, icon, lbl, fmt in steps:
        r = R[key]
        cls = "pipe-step" + (" err" if not r["ok"] else "")
        if r["ok"]:
            val, badge = fmt(r)
            b = f'<span class="pipe-badge">{badge}</span>' if badge else ""
            html += f'<div class="{cls}"><span class="pipe-icon">{icon}</span><span class="pipe-lbl">{lbl}</span><span class="pipe-val">{val}</span>{b}</div>'
        else:
            html += f'<div class="{cls} err"><span class="pipe-icon">✗</span><span class="pipe-lbl">{lbl}</span><span class="pipe-err">{r["error"]}</span></div>'
    st.markdown(html + '</div></div>', unsafe_allow_html=True)

    # ── RÉPONSE ──
    if R["llm"]["ok"]:
        st.markdown(f'''
        <div class="response-box">
            <div class="response-lbl">Réponse de l\'assistant</div>
            <div class="response-txt">{R["llm"]["response"]}</div>
        </div>''', unsafe_allow_html=True)

    if R["tts"]["ok"] and R["tts"].get("wav") and Path(R["tts"]["wav"]).exists():
        st.audio(R["tts"]["wav"])

    if R["asr"]["ok"] and R["llm"]["ok"]:
        st.session_state.history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "input": R["asr"]["transcript"],
            "model": R["llm"]["model"],
            "response": R["llm"]["response"]
        })

# ════════════════════════ HISTORIQUE ════════════════════════
if st.session_state.history:
    st.markdown('<div class="vox-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><div class="card-label">Historique</div>', unsafe_allow_html=True)
    rows = "".join(f'''
    <div class="hist-row">
        <span class="hist-t">{e["time"]}</span>
        <span class="hist-in">{e["input"]}</span>
        <span class="hist-badge">{e["model"]}</span>
    </div>''' for e in reversed(st.session_state.history))
    st.markdown(rows + '</div>', unsafe_allow_html=True)
    if st.button("Effacer l'historique"):
        st.session_state.history = []
        st.rerun()
