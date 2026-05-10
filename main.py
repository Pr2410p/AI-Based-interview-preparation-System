"""
main.py - Intelligent AI Interview & Candidate Readiness Platform
Single-render interview loop: no page reloads between questions.
"""

import streamlit as st
import textwrap
import time

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Interview Pro | SaaS Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── IMPORTS ──────────────────────────────────────────────────────────────────
from streamlit_option_menu import option_menu
from app.database import init_db
from app.auth.auth_manager import login_user, signup_user, logout_user
from app.interview.question_bank import get_all_domains, get_difficulties, get_languages
from app.utils.suggestions import get_performance_insights, get_course_guides
from app.utils.coding_lab import get_lab_challenges, execute_code
from app.ml_models.evaluator import evaluate_answer, generate_improvement_suggestions
from app.interview.interview_engine import (
    InterviewSession, clear_interview_session, get_time_greeting,
)
from app.utils.voice_engine import voice_engine
from app.utils.ui_components import (
    inject_css, render_header, render_alert,
    render_metric_card, render_result_card, render_response_detail,
    render_ai_panel, render_webcam_panel, render_zoom_topbar, render_transcript,
)
from app.utils.dashboard import (
    get_user_interview_history, plot_score_trend, plot_domain_radar,
    plot_difficulty_distribution, get_summary_stats,
)
from app.utils.resume_analyzer import analyze_resume
from app.utils.voice_assistant import ask_assistant, listen_and_respond

# ── INIT ─────────────────────────────────────────────────────────────────────
init_db()
inject_css()

# ── SESSION DEFAULTS ─────────────────────────────────────────────────────────
for k, v in {
    "user": None, "nav_index": 0,
    "interview_phase": "setup",  # setup | running | results
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ════════════════════════════════════════════════════════════════════════════
# 🔐 AUTH
# ════════════════════════════════════════════════════════════════════════════

def page_auth():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""<div class="hero-section">
            <span class="hero-icon">🎯</span>
            <h1 class="hero-title">AI INTERVIEW PRO</h1>
            <p class="hero-subtitle">SaaS Performance & Readiness Platform</p>
        </div>""", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 LOG IN", "📝 SIGN UP"])
        with tab1:
            email = st.text_input("Work Email", placeholder="name@company.com", key="le")
            pw = st.text_input("Password", type="password", placeholder="••••••••", key="lp")
            if st.button("Access Dashboard →", use_container_width=True, key="bl"):
                if email and pw:
                    r = login_user(email, pw)
                    if r["success"]:
                        st.session_state.user = r["user"]
                        st.rerun()
                    else:
                        render_alert(r["message"], "error")
                else:
                    render_alert("Enter email and password.", "warning")
        with tab2:
            name = st.text_input("Full Name", placeholder="John Doe")
            em = st.text_input("Email", placeholder="name@company.com", key="se")
            role = st.selectbox("I am a...", ["Candidate", "Professional", "Student", "Recruiter"])
            pw2 = st.text_input("Password", type="password", key="sp")
            if st.button("Create Account →", use_container_width=True, key="bs"):
                if name and em and pw2:
                    r = signup_user(name, em, pw2, role.lower())
                    if r["success"]:
                        render_alert("Account created! Log in.", "success")
                    else:
                        render_alert(r["message"], "error")


# ════════════════════════════════════════════════════════════════════════════
# 🏠 HOME — Project Description
# ════════════════════════════════════════════════════════════════════════════

def page_home():
    user = st.session_state.user
    greeting = get_time_greeting()

    st.markdown(f"""<div class="hero-section">
        <span class="hero-icon">🎯</span>
        <h1 class="hero-title">{greeting}, {user['name'].split()[0]}!</h1>
        <p class="hero-subtitle">Welcome to the AI-Powered Interview & Readiness Platform</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("### 🚀 About AI Interview Pro")
    st.markdown("""**AI Interview Pro** is a next-generation SaaS platform that simulates **real interview
    experiences** using voice-driven AI. It provides automated questioning, real-time speech
    recognition, NLP-based evaluation, and performance analytics.""")

    st.markdown("### ✨ Key Features")
    features = [
        ("🗣️", "Voice-Driven", "Questions spoken aloud, answers captured via mic"),
        ("📊", "Analytics", "Score trends, skill radar, session history"),
        ("📱", "Responsive", "Access your career path from any device"),
        ("⚡", "SaaS Ready", "Professional performance & industry readiness")
    ]
    cols = st.columns(4)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i]:
            st.markdown(f"""<div class="card" style="text-align:center; height:100%;">
                <div style="font-size:2rem; margin-bottom:0.5rem;">{icon}</div>
                <h4 style="margin:0 0 0.4rem; color:#818cf8;">{title}</h4>
                <p style="color:#94a3b8; font-size:0.8rem; line-height:1.4;">{desc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 How It Works")
    steps = [("1", "Select domain & difficulty"),
             ("2", "AI greets you, asks questions via voice"),
             ("3", "Speak your answer or click Skip"),
             ("4", "Get instant AI feedback & results")]
    for col, (num, txt) in zip(st.columns(4), steps):
        with col:
            st.markdown(f"""<div class="card" style="text-align:center;">
                <div style="font-size:1.8rem; color:#6366f1; font-weight:900;">{num}</div>
                <p style="color:#94a3b8; font-size:0.78rem; margin:0.4rem 0 0;">{txt}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎯 Supported Domains")
    icons_map = {"Python": "🐍", "Machine Learning": "🤖", "Web Development": "🌐",
                 "Data Science": "📈", "DevOps": "⚙️"}
    for col, d in zip(st.columns(len(get_all_domains())), get_all_domains()):
        with col:
            st.markdown(f"""<div class="card" style="text-align:center;">
                <div style="font-size:2rem;">{icons_map.get(d,'💡')}</div>
                <p style="color:#f1f5f9; font-weight:600; margin:0.5rem 0 0;">{d}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("")
    if st.button("🚀 GO TO INTERVIEW →", use_container_width=True, type="primary", key="bgi"):
        st.session_state.nav_index = 1
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# 🎙️ INTERVIEW PAGE — Three clean phases
# ════════════════════════════════════════════════════════════════════════════

def page_interview():
    user = st.session_state.user
    phase = st.session_state.interview_phase

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE: SETUP — show config form, wait for START click
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if phase == "setup":
        render_header("🎙️ Start Your AI Interview", "Configure and begin.")

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            domain = st.selectbox("🎯 Target Domain", get_all_domains(), key="sd")
            diff = st.selectbox("⚡ Difficulty Level", get_difficulties(), key="sf")
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            clicked = st.button("🚀 START INTERVIEW NOW", use_container_width=True,
                                type="primary", key="bstart")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("""<div class="card" style="height:100%;">
                <h4 style="margin-top:0; color:#818cf8;">📋 Protocol</h4>
                <ul style="color:#94a3b8; font-size:0.88rem; line-height:1.8;">
                    <li>AI speaks 20 questions in total</li>
                    <li>10 Theory, 5 Practical, 5 Behavior</li>
                    <li>Female TTS voice (ElevenLabs style)</li>
                    <li>Manual SPEAK / STOP controls</li>
                    <li>20s silence auto-skips question</li>
                </ul>
            </div>""", unsafe_allow_html=True)

        if clicked:
            clear_interview_session()
            st.session_state.interview_session = InterviewSession(
                user["id"], domain, diff, "English"
            )
            st.session_state.interview_phase = "running"
            st.session_state.interview_paused = False
            st.rerun()
        return

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE: RUNNING — Zoom UI + Speak/Stop controls
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if phase == "running":
        if "interview_session" not in st.session_state:
            st.session_state.interview_phase = "setup"
            st.rerun()
            return

        session: InterviewSession = st.session_state.interview_session
        is_rec = getattr(voice_engine, "_recording", False)

        # Auto-transition to results if already complete
        if session.is_complete:
            with st.spinner("📦 Finalizing your results..."):
                summary = session.end_interview()
                session.save_to_db(summary)
                st.session_state.interview_result = summary
                st.session_state.interview_phase = "results"
            st.rerun()
            return

        # ── Greeting (once) ──────────────────────────────────────────────
        if not session.has_greeted:
            render_zoom_topbar(
                interview_title=f"{session.domain} Interview",
                timer_str="00:00", status="🗣️ GREETING", progress_pct=0.0,
            )
            col_ai, col_user = st.columns(2)
            with col_ai: render_ai_panel(is_speaking=True)
            with col_user: render_webcam_panel(user_name=user["name"], is_listening=False)

            with st.spinner("🗣️ AI is greeting you..."):
                session.do_greeting()
            st.rerun()
            return

        # ── Question Speech (once per question) ──────────────────────────
        if not session.has_spoken_current:
            q_num = session.current_index + 1
            render_zoom_topbar(
                interview_title=f"{session.domain} Interview",
                timer_str=session.elapsed_str, status="🗣️ ASKING", progress_pct=session.progress_pct,
            )
            col_ai, col_user = st.columns(2)
            with col_ai: render_ai_panel(is_speaking=True)
            with col_user: render_webcam_panel(user_name=user["name"], is_listening=False)
            
            with st.spinner("🗣️ AI speaking question..."):
                voice_engine.speak(f"Question {q_num}. {session.current_question_text}", language=session.language)
                session.has_spoken_current = True
            st.rerun()
            return

        # ── ZOOM UI ──────────────────────────────────────────────────────
        status_text = "🎙️ RECORDING..." if is_rec else "🔴 WAITING FOR RESPONSE"
        render_zoom_topbar(
            interview_title=f"{session.domain} Interview",
            timer_str=session.elapsed_str,
            status=status_text,
            progress_pct=session.progress_pct,
        )

        col_ai, col_user = st.columns(2)
        with col_ai:
            render_ai_panel(is_speaking=False)
        with col_user:
            render_webcam_panel(user_name=user["name"], is_listening=is_rec)

        # ── Current Question ─────────────────────────────────────────────
        render_transcript(
            current_question=session.current_question_text,
            question_num=session.current_index + 1,
            total=session.total_questions,
            progress_pct=session.progress_pct,
        )

        # ── Show last answer feedback ────────────────────────────────────
        last_status = st.session_state.get("last_turn_status", "")
        last_ans = st.session_state.get("last_answer", "")

        if last_ans:
            st.markdown(f"""
            <div class="answer-display" style="border-left:4px solid #10b981; background:rgba(16,185,129,0.1); padding:1rem; border-radius:0.5rem;">
                <div style="font-size:0.75rem; font-weight:700; color:#10b981;">✅ PREVIOUS ANSWER</div>
                <div style="margin-top:0.3rem;">"{last_ans}"</div>
            </div>
            """, unsafe_allow_html=True)
        elif last_status == "timeout_skipped":
            render_alert("⏱️ Previous question auto-skipped (silence timeout).", "warning")
        elif last_status == "error_skipped":
            render_alert("🔇 Previous question skipped (audio error).", "warning")

        st.markdown("---")

        # ── CONTROL BUTTONS & AUTO-SKIP ──────────────────────────────────
        paused = st.session_state.get("interview_paused", False)
        btns_col = st.columns([1, 1, 1, 1])

        with btns_col[0]:
            if not is_rec:
                if st.button("🎙 Speak", use_container_width=True, type="primary"):
                    st.session_state.interview_paused = False # Resume on speak
                    voice_engine.start_recording(language=session.language)
                    st.rerun()
            else:
                if st.button("⛔ Stop", use_container_width=True, type="primary"):
                    with st.spinner("Processing..."):
                        rec_result = voice_engine.stop_recording()
                    if rec_result["status"] == "success" and rec_result["text"].strip():
                        ans = rec_result["text"]
                        session.submit_answer(ans)
                        st.session_state.last_answer = ans
                        st.session_state.last_turn_status = "answered"
                    else:
                        session.submit_answer("[Inaudible]")
                        st.session_state.last_answer = None
                        st.session_state.last_turn_status = "error_skipped"
                    st.rerun()

        with btns_col[1]:
            if st.button("⏭ Skip", use_container_width=True, key="btn_skip"):
                session.submit_answer("[Skipped by user]")
                st.session_state.last_answer = None
                st.session_state.last_turn_status = "skipped"
                st.rerun()

        with btns_col[2]:
            pause_label = "▶ Resume" if paused else "⏸ Pause"
            if st.button(pause_label, use_container_width=True):
                st.session_state.interview_paused = not paused
                st.rerun()

        with btns_col[3]:
            if st.button("🛑 End", use_container_width=True):
                session.ended = True # Triggers auto-save in next pass
                st.rerun()

        # JS injected to automatically click skip after 20s if NOT recording AND NOT paused
        if not is_rec and not paused:
            import streamlit.components.v1 as components
            components.html("""
            <script>
                const timeoutId = setTimeout(function() {
                    const buttons = window.parent.document.querySelectorAll('button');
                    const skipBtn = Array.from(buttons).find(el => el.innerText.includes('Skip'));
                    if(skipBtn) skipBtn.click();
                }, 20000);
            </script>
            """, height=0)

        # ── Progress bar ─────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.progress(session.progress_pct)
        st.caption(f"Question {session.current_index + 1} of {session.total_questions}")

        return  # ← STOP: nothing else renders during interview

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE: RESULTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if phase == "results":
        if "interview_result" not in st.session_state:
            st.session_state.interview_phase = "setup"
            st.rerun()
            return

        summary = st.session_state.interview_result
        render_header("📊 Session Analysis", "Your AI readiness evaluation is complete.")
        render_result_card(summary)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: render_metric_card("Questions", str(summary.get("num_questions", 0)))
        with c2: render_metric_card("Time", summary.get("elapsed_str", "00:00"), color="#3b82f6")
        with c3: render_metric_card("Skips", str(summary.get("silence_skips", 0)), color="#f59e0b")
        with c4: render_metric_card("Score", f"{summary.get('percentage',0)}%", color="#10b981")

        st.markdown("### 💡 Improvement Suggestions")
        for s in summary.get("suggestions", []):
            st.markdown(f"- {s}")

        st.markdown("### 📝 Response Breakdown")
        responses = summary.get("responses", [])
        if responses:
            render_response_detail(responses)

        st.markdown("---")
        c_new, c_dash = st.columns(2)
        with c_new:
            if st.button("🔄 NEW INTERVIEW", use_container_width=True, key="bnew"):
                clear_interview_session()
                st.session_state.interview_phase = "setup"
                if "interview_result" in st.session_state:
                    del st.session_state["interview_result"]
                st.rerun()
        with c_dash:
            if st.button("📊 VIEW DASHBOARD", use_container_width=True, key="bdash"):
                clear_interview_session()
                st.session_state.interview_phase = "setup"
                if "interview_result" in st.session_state:
                    del st.session_state["interview_result"]
                st.session_state.nav_index = 2
                st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# 📊 DASHBOARD
# ════════════════════════════════════════════════════════════════════════════

def page_dashboard():
    user = st.session_state.user
    render_header("📊 Performance Dashboard", f"Analytics for {user['name'].split()[0]}")

    history = get_user_interview_history(user["id"])
    stats = get_summary_stats(history)

    m1, m2, m3, m4 = st.columns(4)
    with m1: render_metric_card("Sessions", str(stats["total"]))
    with m2: render_metric_card("Avg Score", f"{stats['avg']}%", color="#10b981")
    with m3: render_metric_card("Best", f"{stats['best']}%", color="#f59e0b")
    with m4: render_metric_card("Domains", str(stats["domains"]), color="#3b82f6")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    if history:
        c1, c2 = st.columns([2, 1])
        with c1: st.plotly_chart(plot_score_trend(history), use_container_width=True)
        with c2: st.plotly_chart(plot_domain_radar(history), use_container_width=True)
        st.plotly_chart(plot_difficulty_distribution(history), use_container_width=True)

        st.markdown("### 📋 History")
        for h in history[:10]:
            pct = h.get("percentage", 0)
            clr = "#10b981" if pct >= 70 else "#f59e0b" if pct >= 45 else "#ef4444"
            dur = h.get("duration_seconds", 0)
            st.markdown(f"""<div class="card" style="margin-bottom:0.5rem; padding:1rem;
                display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="font-weight:600; color:#f1f5f9;">{h.get('domain','')}</span>
                    <span style="color:#94a3b8; font-size:0.85rem; margin-left:0.75rem;">{h.get('difficulty','')}</span>
                    <span style="color:#64748b; font-size:0.8rem; margin-left:0.75rem;">⏱ {dur//60}m {dur%60}s</span>
                </div>
                <div style="background:{clr}22; padding:0.3rem 1rem; border-radius:20px; border:1px solid {clr}44;">
                    <span style="color:{clr}; font-weight:700;">{pct}%</span>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        render_alert("No data yet. Complete your first interview!", "info")
        if st.button("🚀 START FIRST INTERVIEW", use_container_width=True, key="bfirst"):
            st.session_state.nav_index = 1
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# 📄 RESUME
# ════════════════════════════════════════════════════════════════════════════

def page_resume():
    render_header("📄 Resume Intelligence", "Optimize your resume.")
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        pdf = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="ru")
        tgt = st.selectbox("Target Domain", get_all_domains(), key="rd")
        if pdf and st.button("🔍 ANALYZE", use_container_width=True, key="br"):
            with st.spinner("Analyzing..."):
                st.session_state.resume_result = analyze_resume(pdf.read(), tgt)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="card" style="height:100%;">
            <h4 style="margin-top:0; color:#818cf8;">📋 Tips</h4>
            <ul style="color:#94a3b8; font-size:0.9rem; line-height:1.8;">
                <li>Upload 1-2 page PDF</li><li>Select target domain</li>
                <li>AI scores keywords & structure</li><li>Get suggestions</li>
            </ul>
        </div>""", unsafe_allow_html=True)
    if "resume_result" in st.session_state:
        r = st.session_state.resume_result
        if "error" in r:
            render_alert(r["error"], "error")
        else:
            st.markdown("---")
            a, b, c = st.columns(3)
            with a: render_metric_card("Score", f"{r['overall_score']}%")
            with b: render_metric_card("Keywords", str(len(r['found_skills'])))
            with c: render_metric_card("Words", str(r['word_count']))
            for s in r['suggestions']: st.info(s)


# ════════════════════════════════════════════════════════════════════════════
# 👤 PROFILE
# ════════════════════════════════════════════════════════════════════════════

def page_profile():
    user = st.session_state.user
    render_header("👤 Account", "Manage your session.")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"""<div class="card" style="text-align:center;">
            <div style="font-size:3.5rem; margin-bottom:1rem;">👤</div>
            <h3 style="margin:0;">{user['name']}</h3>
            <p style="color:#64748b;">{user['email']}</p>
            <div style="background:rgba(99,102,241,0.1); padding:0.5rem; border-radius:8px;
                border:1px solid rgba(99,102,241,0.2); margin-top:1rem;">{user['role'].upper()}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        stats = get_summary_stats(get_user_interview_history(user["id"]))
        st.markdown("### 📈 Stats")
        a, b = st.columns(2)
        with a: render_metric_card("Interviews", str(stats["total"]))
        with b: render_metric_card("Avg Score", f"{stats['avg']}%", color="#10b981")
    st.markdown("---")
    if st.button("🚪 LOG OUT", use_container_width=True, key="bout"):
        logout_user()
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# 🤖 VOICE ASSISTANT — Learn anything via voice
# ════════════════════════════════════════════════════════════════════════════

def page_assistant():
    render_header("🤖 AI Voice Assistant", "Powered by Cohere AI — Ask me anything, I'll answer and speak!")

    # ── Chat history state ────────────────────────────────────────────────
    if "assistant_history" not in st.session_state:
        st.session_state.assistant_history = []

    # ── Chat Bubble Styling ───────────────────────────────────────────────
    st.markdown("""
        <style>
        .chat-container { display: flex; flex-direction: column; gap: 1.5rem; margin-bottom: 3rem; }
        .chat-row { display: flex; align-items: flex-start; gap: 1rem; width: 100%; }
        .chat-row.user { flex-direction: row-reverse; }
        
        .avatar { width: 38px; height: 38px; border-radius: 8px; display: flex; align-items: center; 
                  justify-content: center; font-size: 1.2rem; flex-shrink: 0; }
        .avatar.user { background: #6366f1; color: white; }
        .avatar.ai { background: #10b981; color: white; }
        
        .bubble { padding: 1rem 1.4rem; border-radius: 12px; max-width: 75%; font-size: 0.98rem; 
                  line-height: 1.6; position: relative; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .user-bubble { background: #312e81; color: #f8fafc; border: 1px solid #4338ca; }
        .ai-bubble { background: #1e293b; color: #f1f5f9; border: 1px solid #334155; }
        </style>
    """, unsafe_allow_html=True)

    # ── Chat Display ─────────────────────────────────────────────────────
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    if not st.session_state.assistant_history:
        st.markdown("""<div class="chat-row"><div class="avatar ai">🤖</div>
            <div class="bubble ai-bubble">Welcome to the AI Technical Lab. How can I help you excel today?</div>
        </div>""", unsafe_allow_html=True)
    else:
        for entry in reversed(st.session_state.assistant_history):
            # User
            st.markdown(f"""<div class="chat-row user">
                <div class="avatar user">👤</div>
                <div class="bubble user-bubble">{entry["question"]}</div>
            </div>""", unsafe_allow_html=True)
            # AI
            st.markdown(f"""<div class="chat-row">
                <div class="avatar ai">🤖</div>
                <div class="bubble ai-bubble">{entry["answer"]}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Input Controls ───────────────────────────────────────────────────
    input_col, mic_col = st.columns([6, 1])
    
    with input_col:
        question = st.text_input("Message...", placeholder="Ask about Python, React, Career tips...", key="assist_q", label_visibility="collapsed")
    
    with mic_col:
        speak_clicked = st.button("🎙️", use_container_width=True, help="Speak your question")

    # Handle Text Input
    if st.button("Send ➔", key="send_btn") or (question and st.session_state.get('last_q') != question):
        if question.strip():
            st.session_state.last_q = question
            with st.spinner("Thinking..."):
                answer = ask_assistant(question, speak=True)
                st.session_state.assistant_history.append({"question": question, "answer": answer, "mode": "text"})
            st.rerun()

    # Handle Voice Input
    if speak_clicked:
        with st.spinner("Listening..."):
            result = listen_and_respond()
            if result["status"] == "success":
                st.session_state.assistant_history.append({
                    "question": result["question"], 
                    "answer": result["answer"], 
                    "mode": "voice"
                })
                st.rerun()
            else:
                st.error(f"Error: {result.get('detail', 'Timeout')}")

    # ── Actions ──────────────────────────────────────────────────────────
    if st.session_state.assistant_history:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.assistant_history = []
            st.rerun()



# ════════════════════════════════════════════════════════════════════════════
# 💻 CODING LAB — Live Compiler & Challenges
# ════════════════════════════════════════════════════════════════════════════

def page_coding_lab():
    from code_editor import code_editor
    render_header("💻 Coding Lab", "Practice real-world coding challenges with an inbuilt compiler.")

    # ── Language & Challenge Selection ───────────────────────────────────
    c1, c2 = st.columns([1, 2])
    with c1:
        lang = st.selectbox("📝 Language", ["Python", "Java", "JavaScript", "C++", "SQL"], key="lab_lang")
        challenges = get_lab_challenges(lang)
        challenge = st.selectbox("🎯 Challenge", challenges, format_func=lambda x: x["title"], key="lab_chal")
    
    with c2:
        st.markdown(f"""<div class="card" style="height:100%;">
            <h4 style="margin:0; color:#818cf8;">{challenge['title']}</h4>
            <p style="color:#94a3b8; font-size:0.9rem; margin-top:0.5rem;">{challenge['description']}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Code Editor ──────────────────────────────────────────────────────
    editor_btns = [{
        "name": "Play", "feather": "Play", "primary": True, "hasText": True, "commands": ["submit"], "style": {"bottom": "0.5rem", "right": "0.5rem"}
    }]
    
    # Map languages to ACE editor modes
    ace_lang = lang.lower() if lang != "C++" else "cpp"
    
    response = code_editor(
        challenge["starter_code"], 
        lang=ace_lang, 
        buttons=editor_btns,
        height=[15, 30],
        key=f"editor_{challenge['id']}"
    )

    # ── Execution & Output ───────────────────────────────────────────────
    if response['type'] == "submit":
        code = response['text']
        with st.spinner("🤖 Compiling and executing via AI..."):
            from app.utils.coding_lab import grade_code_with_ai
            exec_res = execute_code(code, lang)
            eval_res = grade_code_with_ai(code, lang, challenge['title'])
            
        st.markdown("### 🖥️ Console & AI Evaluation")
        e1, e2 = st.columns([1, 1])
        with e1:
            st.markdown("**Native Output**")
            if exec_res["status"] == "success":
                st.code(exec_res["output"], language="text")
            else:
                st.error(exec_res["error"])
        
        with e2:
            st.markdown("**AI Technical Verdict**")
            st.markdown(f"""<div class="card" style="border-left:4px solid {'#10b981' if eval_res['status']=='Correct' else '#ef4444'};">
                <div style="display:flex; justify-content:space-between;">
                    <span style="font-weight:600; color:{'#10b981' if eval_res['status']=='Correct' else '#ef4444'};">{eval_res['status'].upper()}</span>
                    <span style="font-weight:700;">Score: {eval_res['score']}%</span>
                </div>
                <p style="color:#94a3b8; font-size:0.85rem; margin-top:0.5rem;">{eval_res['feedback']}</p>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 💡 SUGGESTIONS — Insights & Course Guides
# ════════════════════════════════════════════════════════════════════════════

def page_suggestions():
    user = st.session_state.user
    render_header("💡 Learning & Performance", "Personalized insights and curated course paths.")

    tab_insights, tab_guides = st.tabs(["📊 Performance Insights", "📚 Course Guides"])

    with tab_insights:
        insights = get_performance_insights(user["id"])
        if not insights:
            render_alert("Complete an interview first to see your performance analysis.", "info")
        else:
            for insight in insights:
                st.markdown(f"""<div class="card" style="border-left:4px solid { '#10b981' if insight['type']=='success' else '#f59e0b' };">
                    <h4 style="margin:0; color:#f1f5f9;">{insight['title']}</h4>
                    <p style="color:#94a3b8; font-size:0.95rem; margin-top:0.4rem;">{insight['text']}</p>
                </div>""", unsafe_allow_html=True)
                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    with tab_guides:
        guides = get_course_guides()
        c1, c2 = st.columns(2)
        for i, guide in enumerate(guides):
            target_col = c1 if i % 2 == 0 else c2
            with target_col:
                st.markdown(f"""<div class="card" style="margin-bottom:1.5rem; 
                    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
                    border: 1px solid rgba(255, 255, 255, 0.05); backdrop-filter: blur(8px);">
                    <h3 style="margin-top:0; color:#818cf8; font-size:1.4rem;">{guide['domain']}</h3>
                    <p style="color:#e2e8f0; font-weight:600; font-size:0.95rem; margin-bottom:0.8rem;">{guide['title']}</p>
                    <div style="border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 0.8rem;">
                        <ul style="color:#94a3b8; font-size:0.88rem; list-style-type: '⚡ '; padding-left: 1rem;">
                            {"".join([f"<li><a href='{r['link']}' target='_blank' style='color:#6366f1; text-decoration:none;'>{r['name']}</a></li>" for r in guide['resources']])}
                        </ul>
                    </div>
                </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 🎯 MAIN
# ════════════════════════════════════════════════════════════════════════════

PAGES = ["Home", "Start Interview", "Coding Lab", "Suggestions", "Dashboard", "Voice Assistant", "Resume Analyzer", "Profile"]
ICONS = ["house", "mic", "code-square", "lightbulb", "graph-up", "robot", "file-earmark-person", "person"]

def main():
    if not st.session_state.get("user"):
        page_auth()
        return

    with st.sidebar:
        st.markdown("""<div style="text-align:center; padding:1rem 0;">
            <div style="font-size:2.5rem;">🎯</div>
            <h3 style="margin:0.5rem 0 0; font-weight:800;">INTERVIEW PRO</h3>
            <p style="color:#64748b; font-size:0.8rem; margin:0;">AI-Powered SaaS</p>
        </div>""", unsafe_allow_html=True)

        idx = st.session_state.get("nav_index", 0)
        if idx < 0 or idx >= len(PAGES):
            idx = 0

        selected = option_menu(
            None, PAGES, icons=ICONS, default_index=idx,
            styles={
                "container": {"background-color": "#0d0d16", "padding": "0.5rem 0"},
                "nav-link": {"color": "#94a3b8", "font-size": "0.92rem",
                             "text-align": "left", "margin": "2px 0",
                             "--hover-color": "#1e1e2f"},
                "nav-link-selected": {"background-color": "#6366f1",
                                       "color": "white", "font-weight": "600"},
            },
        )
        if selected in PAGES:
            st.session_state.nav_index = PAGES.index(selected)

        st.markdown("---")
        st.caption("v2.0 SaaS • Build 2026.04")

    idx = st.session_state.get("nav_index", 0)
    [
        page_home, page_interview, page_coding_lab, page_suggestions, 
        page_dashboard, page_assistant, page_resume, page_profile
    ][idx]()


if __name__ == "__main__":
    main()
