"""
app.py  ─  Quantum Cryptography Simulator (BB84 Protocol)
Run with:  streamlit run app.py
"""

import streamlit as st
import time

from quantum_bb84 import (
    run_bb84_simulation,
    generate_random_bits,
)
from utils import (
    text_to_bits,
    bits_to_str,
    key_to_hex,
    generate_random_message,
    basis_symbol,
    plot_bit_comparison,
    plot_key_comparison,
    plot_error_rate_comparison,
    plot_qiskit_circuit,
    plot_measurement_histogram,
    classical_security_score,
    key_to_download_str,
)

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Quantum Cryptography Simulator",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS  (dark terminal aesthetic)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: #0D1117;
    color: #E6EDF3;
}
.stApp { background-color: #0D1117; }

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #161B22 0%, #0D1117 50%, #161B22 100%);
    border: 1px solid #21262D;
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, #60A5FA22 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #60A5FA, #A78BFA, #F472B6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.3rem 0;
    line-height: 1.1;
}
.hero-sub {
    color: #8B949E;
    font-size: 0.82rem;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.05em;
}

/* ── Section cards ── */
.section-card {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: #60A5FA;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Metric cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 0.6rem;
    margin-top: 0.8rem;
}
.metric-card {
    background: #0D1117;
    border: 1px solid #21262D;
    border-radius: 8px;
    padding: 0.9rem 0.7rem;
    text-align: center;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    line-height: 1;
}
.metric-label {
    font-size: 0.65rem;
    color: #8B949E;
    margin-top: 0.2rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Bit table ── */
.bit-row {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    margin: 0.4rem 0;
}
.bit-cell {
    width: 28px;
    height: 28px;
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    border: 1px solid transparent;
}
.bit-match    { background:#4ADE8022; border-color:#4ADE8066; color:#4ADE80; }
.bit-mismatch { background:#F8717122; border-color:#F8717166; color:#F87171; }
.bit-neutral  { background:#21262D;   border-color:#30363D;   color:#8B949E; }
.bit-basis-z  { background:#60A5FA22; border-color:#60A5FA66; color:#60A5FA; }
.bit-basis-x  { background:#F472B622; border-color:#F472B666; color:#F472B6; }

/* ── Status badges ── */
.badge-safe    { background:#4ADE8022; color:#4ADE80; border:1px solid #4ADE8066; border-radius:20px; padding:4px 14px; font-size:0.78rem; font-weight:600; display:inline-block; }
.badge-danger  { background:#F8717122; color:#F87171; border:1px solid #F8717166; border-radius:20px; padding:4px 14px; font-size:0.78rem; font-weight:600; display:inline-block; }
.badge-warn    { background:#FBBF2422; color:#FBBF24; border:1px solid #FBBF2466; border-radius:20px; padding:4px 14px; font-size:0.78rem; font-weight:600; display:inline-block; }

/* ── Key display ── */
.key-display {
    background: #0D1117;
    border: 1px solid #21262D;
    border-left: 3px solid #4ADE80;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #4ADE80;
    word-break: break-all;
    letter-spacing: 0.1em;
}

/* ── Step indicator ── */
.step-row {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin: 0.6rem 0;
}
.step-dot {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 700;
}
.step-done  { background:#4ADE8033; color:#4ADE80; border:1px solid #4ADE80; }
.step-info  { background:#60A5FA33; color:#60A5FA; border:1px solid #60A5FA; }
.step-warn  { background:#FBBF2433; color:#FBBF24; border:1px solid #FBBF24; }
.step-text  { color:#C9D1D9; font-size:0.82rem; padding-top:3px; }
.step-label { color:#8B949E; font-size:0.72rem; margin-top:2px; }

/* ── Streamlit widget tweaks ── */
div[data-testid="stSlider"] label   { color:#8B949E !important; font-size:0.8rem; }
div[data-testid="stToggle"] label   { color:#C9D1D9 !important; }
.stButton>button {
    background: linear-gradient(135deg, #1F6FEB, #388BFD);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
    letter-spacing: 0.04em;
    padding: 0.55rem 1.4rem;
    transition: opacity .15s;
}
.stButton>button:hover { opacity: 0.85; }
div[data-testid="stSidebar"] { background:#0D1117; border-right:1px solid #21262D; }
h1,h2,h3 { font-family:'Syne',sans-serif; color:#E6EDF3; }

/* ── Expander ── */
details summary { color:#60A5FA !important; font-size:0.82rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session state defaults
# ─────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "step" not in st.session_state:
    st.session_state.step = 0
if "step_mode" not in st.session_state:
    st.session_state.step_mode = False


# ─────────────────────────────────────────────
# Hero
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">🔐 Quantum Cryptography Simulator</div>
  <div class="hero-sub">BB84 QKD Protocol · Qiskit · Eavesdropping Detection · Superposition & Measurement</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Sidebar — Controls
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">⚙ CONFIGURATION</div>', unsafe_allow_html=True)

    n_bits = st.slider("Number of qubits", min_value=8, max_value=40, value=20, step=2,
                       help="More qubits → more key material but longer simulation")

    st.markdown("---")
    st.markdown('<div class="section-title">📨 MESSAGE</div>', unsafe_allow_html=True)

    msg_mode = st.radio("Bit source", ["Auto-generate random bits",
                                        "Enter binary string",
                                        "Enter ASCII text"],
                         index=0, label_visibility="collapsed")

    alice_bits_input = None
    if msg_mode == "Enter binary string":
        bin_str = st.text_input("Binary string", value="10110010",
                                 max_chars=40, placeholder="e.g. 10110010")
        if bin_str:
            clean = ''.join(c for c in bin_str if c in '01')
            if clean:
                alice_bits_input = [int(b) for b in clean][:n_bits]
                n_bits = len(alice_bits_input)

    elif msg_mode == "Enter ASCII text":
        ascii_msg = st.text_input("ASCII message", value="QKD",
                                   max_chars=6, placeholder="e.g. QKD")
        if ascii_msg:
            alice_bits_input = text_to_bits(ascii_msg)[:n_bits]
            n_bits = len(alice_bits_input)
            st.caption(f"→ {len(alice_bits_input)} bits from '{ascii_msg}'")

    st.markdown("---")
    st.markdown('<div class="section-title">🕵 EVE</div>', unsafe_allow_html=True)
    enable_eve = st.toggle("Enable Eavesdropper (Eve)", value=False)
    if enable_eve:
        st.markdown('<span class="badge-danger">⚠ Eve is active — expect ~25% QBER</span>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-safe">✓ No eavesdropper</span>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">🧭 MODE</div>', unsafe_allow_html=True)
    step_mode = st.toggle("Step-by-step mode", value=False,
                           help="Reveal simulation stages one at a time")
    st.session_state.step_mode = step_mode

    st.markdown("---")
    col_run, col_reset = st.columns(2)
    with col_run:
        run_btn = st.button("▶ Run", use_container_width=True)
    with col_reset:
        reset_btn = st.button("↺ Reset", use_container_width=True)

    if reset_btn:
        st.session_state.result = None
        st.session_state.step   = 0
        st.rerun()

    if run_btn:
        with st.spinner("Running quantum simulation…"):
            result = run_bb84_simulation(
                n_bits=n_bits,
                enable_eve=enable_eve,
                alice_bits_input=alice_bits_input,
            )
            st.session_state.result = result
            st.session_state.step   = 0 if step_mode else 99

    # ── Info panel ──
    with st.expander("📖 How BB84 Works"):
        st.markdown("""
**BB84** (Bennett & Brassard, 1984) is the first quantum key distribution protocol.

1. **Alice** prepares qubits in random bases (Z or X)
2. **Bob** measures in random bases
3. They compare bases publicly → keep matches
4. If **Eve** intercepts, she disturbs qubits → detectable ~25% error rate

**Bases:**
- `⊕` (Z-basis): |0⟩ or |1⟩
- `⊗` (X-basis): |+⟩ or |−⟩

**Security principle:** The *no-cloning theorem* means Eve can't copy a qubit without disturbing it.
        """)


# ─────────────────────────────────────────────
# Main content
# ─────────────────────────────────────────────
result = st.session_state.result

if result is None:
    # Landing state
    st.markdown("""
<div class="section-card" style="text-align:center; padding:3rem;">
  <div style="font-size:3rem; margin-bottom:1rem;">⚛</div>
  <div style="font-family:'Syne',sans-serif; font-size:1.2rem; color:#C9D1D9; margin-bottom:0.5rem;">
    Configure and run the simulation
  </div>
  <div style="color:#8B949E; font-size:0.82rem;">
    Adjust settings in the sidebar, then click <strong style="color:#60A5FA">▶ Run</strong>
  </div>
</div>
""", unsafe_allow_html=True)

    # Quick explainer cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
<div class="section-card">
<div class="section-title">⚛ Superposition</div>
<div style="color:#8B949E; font-size:0.8rem;">
Qubits exist in multiple states simultaneously. Alice encodes bits using X-basis (|+⟩/|−⟩) — a superposition that collapses only upon measurement.
</div>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
<div class="section-card">
<div class="section-title">🔭 Measurement</div>
<div style="color:#8B949E; font-size:0.8rem;">
Measuring a qubit in the wrong basis yields a random result. This is the physical foundation of BB84 security — Eve's wrong-basis measurement disturbs the state.
</div>
</div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
<div class="section-card">
<div class="section-title">🔐 Quantum Advantage</div>
<div style="color:#8B949E; font-size:0.8rem;">
Classical eavesdropping is undetectable. Quantum eavesdropping always leaves a fingerprint — QBER spikes to ~25% when Eve is active.
</div>
</div>""", unsafe_allow_html=True)

else:
    # ─────────────────────────────────────────
    # Step-by-step controller
    # ─────────────────────────────────────────
    STEPS = ["Alice Encodes", "Bob Measures", "Key Sifting",
             "Error Analysis", "Visualizations", "Security Report"]
    current_step = st.session_state.step

    if st.session_state.step_mode and current_step < len(STEPS):
        step_cols = st.columns([6, 1])
        with step_cols[0]:
            st.progress((current_step) / len(STEPS))
            st.caption(f"Step {current_step + 1} / {len(STEPS)} — {STEPS[current_step] if current_step < len(STEPS) else 'Done'}")
        with step_cols[1]:
            if st.button("Next →"):
                st.session_state.step += 1
                st.rerun()

    show = lambda idx: (current_step >= idx) or (not st.session_state.step_mode)

    # ─────────────────────────────────────────
    # SECTION 1 — Alice
    # ─────────────────────────────────────────
    if show(0):
        with st.expander("① Alice — Encoding", expanded=True):
            alice_bits  = result["alice_bits"]
            alice_bases = result["alice_bases"]
            n = len(alice_bits)

            st.markdown('<div class="section-title">🔴 Alice\'s Bits</div>', unsafe_allow_html=True)
            bit_html  = '<div class="bit-row">'
            base_html = '<div class="bit-row">'
            for i, (bit, base) in enumerate(zip(alice_bits, alice_bases)):
                bit_html  += f'<div class="bit-cell bit-neutral">{bit}</div>'
                cls = "bit-basis-z" if base == "Z" else "bit-basis-x"
                base_html += f'<div class="bit-cell {cls}">{basis_symbol(base)}</div>'
            bit_html  += '</div>'
            base_html += '</div>'

            st.markdown("**Bits:**")
            st.markdown(bit_html, unsafe_allow_html=True)
            st.markdown("**Bases:**")
            st.markdown(base_html, unsafe_allow_html=True)
            st.caption("⊕ = Z-basis (computational)  |  ⊗ = X-basis (Hadamard/superposition)")

    # ─────────────────────────────────────────
    # SECTION 2 — Eve (if active)
    # ─────────────────────────────────────────
    if result["enable_eve"] and show(0):
        with st.expander("🕵 Eve — Intercepting", expanded=False):
            eve_bits  = result["eve_bits"]
            eve_bases = result["eve_bases"]
            st.markdown('<div class="section-title" style="color:#F87171">🕵 Eve\'s Measurement</div>',
                        unsafe_allow_html=True)
            st.warning("⚠ Eve is intercepting qubits and re-sending them. This causes quantum state disturbance.", icon="⚠")
            bit_html  = '<div class="bit-row">'
            base_html = '<div class="bit-row">'
            for bit, base in zip(eve_bits, eve_bases):
                bit_html  += f'<div class="bit-cell bit-mismatch">{bit}</div>'
                cls = "bit-basis-z" if base == "Z" else "bit-basis-x"
                base_html += f'<div class="bit-cell {cls}">{basis_symbol(base)}</div>'
            bit_html  += '</div>'
            base_html += '</div>'
            st.markdown("**Eve's measured bits:**")
            st.markdown(bit_html, unsafe_allow_html=True)
            st.markdown("**Eve's bases:**")
            st.markdown(base_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────
    # SECTION 3 — Bob
    # ─────────────────────────────────────────
    if show(1):
        with st.expander("② Bob — Measurement", expanded=True):
            bob_bits  = result["bob_bits"]
            bob_bases = result["bob_bases"]
            matching  = set(result["matching_indices"])

            st.markdown('<div class="section-title" style="color:#4ADE80">🔵 Bob\'s Results</div>',
                        unsafe_allow_html=True)
            bit_html  = '<div class="bit-row">'
            base_html = '<div class="bit-row">'
            for i, (bit, base) in enumerate(zip(bob_bits, bob_bases)):
                cls = "bit-match" if i in matching else "bit-mismatch"
                bit_html  += f'<div class="bit-cell {cls}">{bit}</div>'
                bcls = "bit-basis-z" if base == "Z" else "bit-basis-x"
                base_html += f'<div class="bit-cell {bcls}">{basis_symbol(base)}</div>'
            bit_html  += '</div>'
            base_html += '</div>'

            st.markdown("**Received bits** (green = matching basis with Alice):")
            st.markdown(bit_html, unsafe_allow_html=True)
            st.markdown("**Bob's bases:**")
            st.markdown(base_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────
    # SECTION 4 — Key Sifting
    # ─────────────────────────────────────────
    if show(2):
        with st.expander("③ Key Sifting & Comparison", expanded=True):
            alice_key   = result["alice_key"]
            bob_key     = result["bob_key"]
            secure_key  = result["secure_key"]
            n_match     = len(result["matching_indices"])
            n_total     = result["n_bits"]

            st.markdown('<div class="section-title">🗝 Sifted Key</div>', unsafe_allow_html=True)
            # Metrics
            st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-value" style="color:#60A5FA">{n_total}</div>
    <div class="metric-label">Qubits sent</div>
  </div>
  <div class="metric-card">
    <div class="metric-value" style="color:#A78BFA">{n_match}</div>
    <div class="metric-label">Matching bases</div>
  </div>
  <div class="metric-card">
    <div class="metric-value" style="color:#4ADE80">{len(secure_key)}</div>
    <div class="metric-label">Secure key bits</div>
  </div>
  <div class="metric-card">
    <div class="metric-value" style="color:#FBBF24">{n_match/n_total*100:.0f}%</div>
    <div class="metric-label">Sift efficiency</div>
  </div>
</div>
""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Sifted key rows with mismatch highlights
            st.markdown("**Alice's sifted key:**")
            k_html = '<div class="bit-row">'
            for a, b in zip(alice_key, bob_key):
                cls = "bit-match" if a == b else "bit-mismatch"
                k_html += f'<div class="bit-cell {cls}">{a}</div>'
            k_html += '</div>'
            st.markdown(k_html, unsafe_allow_html=True)

            st.markdown("**Bob's sifted key:**")
            k_html2 = '<div class="bit-row">'
            for a, b in zip(alice_key, bob_key):
                cls = "bit-match" if a == b else "bit-mismatch"
                k_html2 += f'<div class="bit-cell {cls}">{b}</div>'
            k_html2 += '</div>'
            st.markdown(k_html2, unsafe_allow_html=True)

            st.markdown("<br>**Final secure key (binary):**", unsafe_allow_html=True)
            st.markdown(f'<div class="key-display">{bits_to_str(secure_key) or "— no secure bits —"}</div>',
                        unsafe_allow_html=True)

            if secure_key:
                st.markdown(f'<div class="key-display" style="border-left-color:#A78BFA; color:#A78BFA; margin-top:6px;">HEX: {key_to_hex(secure_key)}</div>',
                             unsafe_allow_html=True)

                # Download button
                dl_str = key_to_download_str(
                    secure_key, result["error_rate"],
                    result["n_bits"], result["enable_eve"]
                )
                st.download_button(
                    "⬇ Download Key Report",
                    data=dl_str,
                    file_name="quantum_key.txt",
                    mime="text/plain",
                )

    # ─────────────────────────────────────────
    # SECTION 5 — Error Analysis
    # ─────────────────────────────────────────
    if show(3):
        with st.expander("④ QBER & Eavesdropping Detection", expanded=True):
            error_rate   = result["error_rate"]
            eve_detected = result["eavesdropping_detected"]

            st.markdown('<div class="section-title">📡 Quantum Bit Error Rate</div>',
                        unsafe_allow_html=True)

            col_l, col_r = st.columns([2, 3])
            with col_l:
                color = "#F87171" if eve_detected else "#4ADE80"
                st.markdown(f"""
<div class="metric-card" style="padding:1.5rem;">
  <div class="metric-value" style="color:{color}; font-size:2.4rem;">{error_rate:.1f}%</div>
  <div class="metric-label">QBER</div>
  <br>
""", unsafe_allow_html=True)
                if eve_detected:
                    st.markdown('<span class="badge-danger">⚠ Eavesdropping DETECTED</span>',
                                unsafe_allow_html=True)
                else:
                    st.markdown('<span class="badge-safe">✓ Channel is SECURE</span>',
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # Step-by-step log
                st.markdown("""
<div style="margin-top:1rem;">
""", unsafe_allow_html=True)
                steps_data = [
                    ("step-done", "1", "Qubits transmitted by Alice"),
                    ("step-done", "2", "Measured by Bob"),
                    ("step-done", "3", "Bases compared & sifted"),
                    ("step-warn" if eve_detected else "step-done",
                     "4",
                     f"QBER = {error_rate:.1f}% {'⚠ > 10%' if eve_detected else '✓ < 10%'}"),
                ]
                if result["enable_eve"]:
                    steps_data.append(("step-warn", "!", "Eve intercepted — channel compromised"))

                html_steps = ""
                for cls, num, text in steps_data:
                    html_steps += f"""
<div class="step-row">
  <div class="step-dot {cls}">{num}</div>
  <div class="step-text">{text}</div>
</div>"""
                st.markdown(html_steps, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_r:
                # Error rate comparison chart
                error_no_eve   = error_rate if not result["enable_eve"] else 1.5
                error_with_eve = error_rate if result["enable_eve"] else 24.5
                img_bytes = plot_error_rate_comparison(error_no_eve, error_with_eve)
                st.image(img_bytes, use_container_width=True)

    # ─────────────────────────────────────────
    # SECTION 6 — Visualizations
    # ─────────────────────────────────────────
    if show(4):
        with st.expander("⑤ Quantum Circuit & Histograms", expanded=True):
            st.markdown('<div class="section-title">⚛ Qiskit Visualizations</div>',
                        unsafe_allow_html=True)

            v1, v2 = st.columns(2)
            with v1:
                st.markdown("**Sample Circuit (qubit 0)**")
                circuit_img = plot_qiskit_circuit(result["sample_circuit"])
                st.image(circuit_img, use_container_width=True)

            with v2:
                st.markdown("**Measurement Histogram**")
                hist_img = plot_measurement_histogram(result["hist_counts"])
                st.image(hist_img, use_container_width=True)

            st.markdown("---")
            st.markdown("**Bit-by-bit Qubit Comparison**")
            bit_compare_img = plot_bit_comparison(
                result["alice_bits"], result["bob_bits"],
                result["alice_bases"], result["bob_bases"],
                result["matching_indices"]
            )
            st.image(bit_compare_img, use_container_width=True)

            st.markdown("**Sifted Key Bit Comparison**")
            key_compare_img = plot_key_comparison(result["alice_key"], result["bob_key"])
            st.image(key_compare_img, use_container_width=True)

    # ─────────────────────────────────────────
    # SECTION 7 — Security Report
    # ─────────────────────────────────────────
    if show(5):
        with st.expander("⑥ Quantum vs Classical Security", expanded=True):
            st.markdown('<div class="section-title">🛡 Security Analysis</div>',
                        unsafe_allow_html=True)
            security = classical_security_score(len(result["secure_key"]))

            col_q, col_c = st.columns(2)
            with col_q:
                st.markdown("""
<div class="section-card" style="border-left:3px solid #60A5FA;">
<div class="section-title">⚛ Quantum (BB84)</div>
<ul style="color:#C9D1D9; font-size:0.82rem; padding-left:1.2rem; line-height:1.9;">
  <li>Key exchanged over quantum channel</li>
  <li>Eavesdropping is <strong style="color:#4ADE80">physically detectable</strong></li>
  <li>Based on no-cloning theorem</li>
  <li>Information-theoretically secure</li>
  <li>QBER threshold: ~11%</li>
</ul>
</div>
""", unsafe_allow_html=True)

            with col_c:
                st.markdown("""
<div class="section-card" style="border-left:3px solid #F87171;">
<div class="section-title">💻 Classical (RSA/AES)</div>
<ul style="color:#C9D1D9; font-size:0.82rem; padding-left:1.2rem; line-height:1.9;">
  <li>Key exchange over classical channel</li>
  <li>Eavesdropping is <strong style="color:#F87171">undetectable</strong></li>
  <li>Security based on computational hardness</li>
  <li>Breakable by quantum computers (Shor's)</li>
  <li>No inherent detection mechanism</li>
</ul>
</div>
""", unsafe_allow_html=True)

            st.markdown(f"""
<div class="section-card" style="margin-top:0.5rem;">
<div class="section-title">🔑 Your Generated Key</div>
<div style="font-size:0.82rem; color:#C9D1D9; line-height:1.9;">
  Key length: <strong style="color:#60A5FA">{security.get('key_length', 0)} bits</strong><br>
  Possible combinations: <strong style="color:#A78BFA">{security.get('combinations', 'N/A')}</strong><br>
  Undetectable intercept: <strong style="color:#4ADE80">{security.get('undetectable_intercept', 'N/A')}</strong>
</div>
<div style="color:#8B949E; font-size:0.78rem; margin-top:0.7rem; border-top:1px solid #21262D; padding-top:0.7rem;">
  {security.get('quantum_advantage', '')}
</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("""
<hr style="border-color:#21262D; margin-top:3rem;">
<div style="text-align:center; color:#8B949E; font-size:0.72rem; padding-bottom:1rem;">
  Quantum Cryptography Simulator · BB84 Protocol · Built with Qiskit + Streamlit
</div>
""", unsafe_allow_html=True)
