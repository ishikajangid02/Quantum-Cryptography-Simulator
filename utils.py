"""
utils.py
Helper functions for visualization, formatting, and data export.
"""

import io
import random
import string
import matplotlib
matplotlib.use("Agg")   # Non-interactive backend for Streamlit
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram, circuit_drawer


# ─────────────────────────────────────────────
# Text / Key Helpers
# ─────────────────────────────────────────────

def text_to_bits(text: str) -> list[int]:
    """Convert ASCII text to a flat list of bits (8 bits per char)."""
    bits = []
    for char in text:
        byte = format(ord(char), '08b')
        bits.extend(int(b) for b in byte)
    return bits


def bits_to_text(bits: list[int]) -> str:
    """Convert a list of bits back to ASCII text (silently skip bad bytes)."""
    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte = ''.join(str(b) for b in bits[i:i+8])
        try:
            chars.append(chr(int(byte, 2)))
        except ValueError:
            pass
    return ''.join(chars)


def bits_to_str(bits: list[int]) -> str:
    """Format a list of bits as a compact string like '10110...'"""
    return ''.join(str(b) for b in bits)


def key_to_hex(bits: list[int]) -> str:
    """Convert a bit list to a hexadecimal string."""
    if not bits:
        return "N/A"
    padded = bits + [0] * ((4 - len(bits) % 4) % 4)
    hex_str = ''
    for i in range(0, len(padded), 4):
        nibble = padded[i:i+4]
        hex_str += format(int(''.join(str(b) for b in nibble), 2), 'X')
    return hex_str


def generate_random_message(length: int = 4) -> str:
    """Generate a random short word-like string for demo purposes."""
    return ''.join(random.choices(string.ascii_uppercase, k=length))


def basis_symbol(basis: str) -> str:
    """Return a pretty Unicode symbol for a basis."""
    return "⊕" if basis == 'Z' else "⊗"


# ─────────────────────────────────────────────
# Matplotlib Figures
# ─────────────────────────────────────────────

def fig_to_bytes(fig: plt.Figure) -> bytes:
    """Serialize a Matplotlib figure to PNG bytes for st.image()."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight",
                facecolor=fig.get_facecolor(), dpi=130)
    buf.seek(0)
    return buf.read()


def plot_bit_comparison(alice_bits: list[int],
                        bob_bits: list[int],
                        alice_bases: list[str],
                        bob_bases: list[str],
                        matching_indices: list[int]) -> bytes:
    """
    Visual grid showing each qubit:
    - Alice's bit & basis
    - Bob's basis & received bit
    - Whether they match
    """
    n = len(alice_bits)
    fig, axes = plt.subplots(4, 1, figsize=(max(10, n * 0.55), 4.5))
    fig.patch.set_facecolor('#0D1117')

    rows = [
        ("Alice Bits",   alice_bits,
         ['#4ADE80' if i in matching_indices else '#6B7280' for i in range(n)]),
        ("Alice Bases",  [basis_symbol(b) for b in alice_bases],
         ['#60A5FA' for _ in range(n)]),
        ("Bob Bases",    [basis_symbol(b) for b in bob_bases],
         ['#F472B6' for _ in range(n)]),
        ("Bob Bits",     bob_bits,
         ['#4ADE80' if i in matching_indices else '#F87171' for i in range(n)]),
    ]

    for ax, (label, values, colors) in zip(axes, rows):
        ax.set_facecolor('#161B22')
        ax.set_xlim(-0.5, n - 0.5)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_xticks(range(n))
        ax.set_xticklabels(range(n), fontsize=7, color='#8B949E')
        ax.set_ylabel(label, color='#E6EDF3', fontsize=8, rotation=0,
                      ha='right', va='center', labelpad=80)
        for i, (val, color) in enumerate(zip(values, colors)):
            ax.add_patch(
                mpatches.FancyBboxPatch(
                    (i - 0.4, 0.15), 0.8, 0.7,
                    boxstyle="round,pad=0.05",
                    linewidth=0.5,
                    edgecolor='#30363D',
                    facecolor=color + '33'
                )
            )
            ax.text(i, 0.5, str(val), ha='center', va='center',
                    color=color, fontsize=9, fontweight='bold',
                    fontfamily='monospace')
        for spine in ax.spines.values():
            spine.set_edgecolor('#30363D')

    fig.suptitle("Qubit-by-Qubit Comparison", color='#E6EDF3',
                 fontsize=12, fontweight='bold', y=1.01)
    plt.tight_layout(pad=0.4)
    return fig_to_bytes(fig)


def plot_key_comparison(alice_key: list[int],
                        bob_key: list[int]) -> bytes:
    """Bar chart showing matching (green) vs mismatched (red) key bits."""
    n = len(alice_key)
    if n == 0:
        fig, ax = plt.subplots(figsize=(6, 2))
        fig.patch.set_facecolor('#0D1117')
        ax.set_facecolor('#161B22')
        ax.text(0.5, 0.5, "No matching bases found", ha='center', va='center',
                color='#8B949E', transform=ax.transAxes, fontsize=11)
        ax.axis('off')
        return fig_to_bytes(fig)

    colors = ['#4ADE80' if a == b else '#F87171'
              for a, b in zip(alice_key, bob_key)]

    fig, ax = plt.subplots(figsize=(max(8, n * 0.5), 2.8))
    fig.patch.set_facecolor('#0D1117')
    ax.set_facecolor('#161B22')
    bars = ax.bar(range(n), [1] * n, color=colors,
                  width=0.7, edgecolor='#0D1117', linewidth=0.8)

    for i, (a, b) in enumerate(zip(alice_key, bob_key)):
        ax.text(i, 0.5, str(a), ha='center', va='center',
                color='#0D1117', fontsize=9, fontweight='bold',
                fontfamily='monospace')

    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(0, 1.4)
    ax.set_yticks([])
    ax.set_xticks(range(n))
    ax.set_xticklabels([str(i) for i in range(n)],
                       fontsize=7, color='#8B949E')
    ax.set_title("Sifted Key Comparison (Green = Match, Red = Error)",
                 color='#E6EDF3', fontsize=10, pad=8)

    green_patch = mpatches.Patch(color='#4ADE80', label='Match')
    red_patch   = mpatches.Patch(color='#F87171', label='Mismatch (Eve)')
    ax.legend(handles=[green_patch, red_patch], loc='upper right',
              facecolor='#161B22', edgecolor='#30363D',
              labelcolor='#E6EDF3', fontsize=8)

    for spine in ax.spines.values():
        spine.set_edgecolor('#30363D')

    plt.tight_layout()
    return fig_to_bytes(fig)


def plot_error_rate_comparison(error_no_eve: float,
                                error_with_eve: float) -> bytes:
    """Bar chart comparing error rate with vs without Eve."""
    fig, ax = plt.subplots(figsize=(5, 3.5))
    fig.patch.set_facecolor('#0D1117')
    ax.set_facecolor('#161B22')

    labels = ['Without Eve', 'With Eve']
    values = [error_no_eve, error_with_eve]
    colors = ['#4ADE80', '#F87171']

    bars = ax.bar(labels, values, color=colors, width=0.45,
                  edgecolor='#0D1117', linewidth=0.8)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.8,
                f'{val:.1f}%', ha='center', va='bottom',
                color='#E6EDF3', fontsize=11, fontweight='bold')

    ax.axhline(y=11, color='#FBBF24', linestyle='--', linewidth=1.2,
               label='Detection threshold (11%)')
    ax.set_ylim(0, max(max(values) + 10, 35))
    ax.set_ylabel('Error Rate (%)', color='#8B949E', fontsize=9)
    ax.set_title('QBER: Classical vs Quantum Eavesdropping',
                 color='#E6EDF3', fontsize=10, pad=8)
    ax.legend(facecolor='#161B22', edgecolor='#30363D',
              labelcolor='#E6EDF3', fontsize=8)
    ax.tick_params(colors='#8B949E')
    for spine in ax.spines.values():
        spine.set_edgecolor('#30363D')

    plt.tight_layout()
    return fig_to_bytes(fig)


def plot_qiskit_circuit(qc: QuantumCircuit) -> bytes:
    """Render a Qiskit circuit as a PNG image."""
    fig = qc.draw(output='mpl',
                  style={
                      'backgroundcolor': '#161B22',
                      'textcolor': '#E6EDF3',
                      'gatetextcolor': '#0D1117',
                      'subtextcolor': '#8B949E',
                      'linecolor': '#8B949E',
                      'creglinecolor': '#F472B6',
                      'gatefacecolor': '#60A5FA',
                      'barrierfacecolor': '#30363D',
                  })
    return fig_to_bytes(fig)


def plot_measurement_histogram(counts: dict) -> bytes:
    """Render Qiskit measurement histogram as PNG."""
    fig, ax = plt.subplots(figsize=(4.5, 3))
    fig.patch.set_facecolor('#0D1117')
    ax.set_facecolor('#161B22')

    labels = list(counts.keys())
    values = list(counts.values())
    total  = sum(values)
    colors = ['#60A5FA', '#F472B6', '#4ADE80', '#FBBF24']

    bars = ax.bar(labels, values,
                  color=colors[:len(labels)],
                  edgecolor='#0D1117', linewidth=0.8)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + total * 0.01,
                f'{val/total*100:.1f}%',
                ha='center', va='bottom',
                color='#E6EDF3', fontsize=9)

    ax.set_xlabel('Measurement Outcome', color='#8B949E', fontsize=9)
    ax.set_ylabel('Counts', color='#8B949E', fontsize=9)
    ax.set_title('Measurement Results (1024 shots)',
                 color='#E6EDF3', fontsize=10, pad=6)
    ax.tick_params(colors='#8B949E')
    for spine in ax.spines.values():
        spine.set_edgecolor('#30363D')

    plt.tight_layout()
    return fig_to_bytes(fig)


# ─────────────────────────────────────────────
# Security & Classical Comparison
# ─────────────────────────────────────────────

def classical_security_score(key_length: int) -> dict:
    """
    Estimate classical brute-force effort vs quantum key length.
    Shows why quantum key distribution is fundamentally more secure.
    """
    if key_length == 0:
        return {"combinations": 0, "bits": 0, "verdict": "No key generated"}

    combinations = 2 ** key_length
    years_128bit = "~10³⁸ years"
    classical_equiv = f"2^{key_length} = {combinations:,} possible keys"
    undetectable_intercept = "IMPOSSIBLE" if key_length > 0 else "N/A"

    return {
        "key_length": key_length,
        "combinations": classical_equiv,
        "undetectable_intercept": undetectable_intercept,
        "quantum_advantage": (
            "Any eavesdropping disturbs quantum states (no-cloning theorem), "
            "making interception detectable — unlike classical encryption."
        )
    }


# ─────────────────────────────────────────────
# Download Helpers
# ─────────────────────────────────────────────

def key_to_download_str(secure_key: list[int],
                         error_rate: float,
                         n_bits: int,
                         eve_enabled: bool) -> str:
    """Format the key and metadata as a downloadable text report."""
    lines = [
        "=" * 50,
        "  QUANTUM KEY DISTRIBUTION — BB84 PROTOCOL",
        "  Generated by Quantum Cryptography Simulator",
        "=" * 50,
        "",
        f"  Total qubits transmitted : {n_bits}",
        f"  Eavesdropper (Eve) active : {'YES ⚠' if eve_enabled else 'NO ✓'}",
        f"  QBER (error rate)        : {error_rate:.2f}%",
        f"  Eavesdropping detected   : {'YES' if error_rate > 10 else 'NO'}",
        "",
        f"  Key length (bits)        : {len(secure_key)}",
        f"  Key (binary)             : {bits_to_str(secure_key)}",
        f"  Key (hex)                : {key_to_hex(secure_key)}",
        "",
        "=" * 50,
    ]
    return "\n".join(lines)
