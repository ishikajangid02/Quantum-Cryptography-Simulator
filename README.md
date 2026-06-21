# 🔐 Quantum Cryptography Simulator — BB84 Protocol

An interactive simulator for **Quantum Key Distribution** using the BB84 protocol,
built with **Qiskit** and **Streamlit**.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 📁 Project Structure

```
quantum_crypto/
├── app.py            ← Streamlit UI (main entry point)
├── quantum_bb84.py   ← Core quantum logic (BB84 protocol, Qiskit)
├── utils.py          ← Visualization & helper functions
├── requirements.txt  ← Python dependencies
└── README.md         ← This file
```

---

## ✨ Features

| Feature | Description |
|---|---|
| BB84 Protocol | Full Alice → Eve (optional) → Bob simulation |
| Qiskit Circuits | Real quantum circuits with X and H gates |
| QBER Analysis | Quantum Bit Error Rate calculation |
| Eavesdropping Detection | Eve causes ~25% QBER, threshold at 11% |
| Histograms | Measurement result distributions (1024 shots) |
| Bit Visualizer | Color-coded qubit comparison grid |
| Step-by-step Mode | Reveal simulation stages one at a time |
| Multiple Input Modes | Auto-generate, binary string, or ASCII text |
| Download Key | Export key + metadata as a text report |
| Security Comparison | Quantum vs classical encryption overview |

---

## 🔬 Quantum Concepts Demonstrated

- **Superposition** — Hadamard gate puts qubits in |+⟩/|−⟩ states
- **Measurement collapse** — wrong-basis measurement yields random results
- **No-cloning theorem** — Eve can't copy qubits without disturbing them
- **Quantum advantage** — interception is physically detectable

---

## 📦 Dependencies

- `qiskit` — quantum circuit construction and transpilation
- `qiskit-aer` — local quantum simulator backend
- `streamlit` — web UI framework
- `matplotlib` — all visualizations

---

## 👩‍🔬 Authors

University Mini-Project · Quantum Cryptography Simulator
