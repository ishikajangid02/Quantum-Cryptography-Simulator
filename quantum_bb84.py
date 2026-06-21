"""
quantum_bb84.py
Core quantum logic for BB84 Quantum Key Distribution Protocol using Qiskit.

BB84 Overview:
- Alice prepares qubits in random bases (Z or X) with random bits
- Bob measures in random bases
- They compare bases publicly and keep only matching ones
- If Eve intercepts, she disturbs qubits → detectable error rate
"""

import random
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram


# ─────────────────────────────────────────────
# Core BB84 Functions
# ─────────────────────────────────────────────

def generate_random_bits(n: int) -> list[int]:
    """Generate n random classical bits (0 or 1)."""
    return [random.randint(0, 1) for _ in range(n)]


def generate_random_bases(n: int) -> list[str]:
    """
    Generate n random bases.
    'Z' = computational basis (|0⟩, |1⟩)
    'X' = Hadamard basis (|+⟩, |−⟩)
    """
    return [random.choice(['Z', 'X']) for _ in range(n)]


def alice_encode(bits: list[int], bases: list[str]) -> list[QuantumCircuit]:
    """
    Alice encodes each bit into a qubit using her chosen basis.
    
    Encoding rules:
    - Z basis, bit=0 → |0⟩  (no gate)
    - Z basis, bit=1 → |1⟩  (X gate)
    - X basis, bit=0 → |+⟩  (H gate)
    - X basis, bit=1 → |−⟩  (X then H gate)
    """
    circuits = []
    for bit, basis in zip(bits, bases):
        qc = QuantumCircuit(1, 1)
        if bit == 1:
            qc.x(0)          # Flip to |1⟩
        if basis == 'X':
            qc.h(0)          # Apply Hadamard → superposition
        circuits.append(qc)
    return circuits


def eve_intercept(circuits, eve_bases, simulator):
    """
    Eve intercepts and re-sends qubits.
    She measures in a random basis, then re-prepares based on her result.
    This introduces errors when her basis ≠ Alice's basis.
    """
    eve_bits = []
    new_circuits = []

    for qc, eve_basis in zip(circuits, eve_bases):
        # Eve measures
        measure_qc = qc.copy()
        if eve_basis == 'X':
            measure_qc.h(0)
        measure_qc.measure(0, 0)

        job = simulator.run(measure_qc, shots=1)
        result = job.result()
        counts = result.get_counts()
        measured_bit = int(list(counts.keys())[0])
        eve_bits.append(measured_bit)

        # Eve re-prepares qubit based on her measurement
        new_qc = QuantumCircuit(1, 1)
        if measured_bit == 1:
            new_qc.x(0)
        if eve_basis == 'X':
            new_qc.h(0)
        new_circuits.append(new_qc)

    return new_circuits, eve_bits


def bob_measure(circuits: list[QuantumCircuit],
                bob_bases: list[str],
                simulator: AerSimulator) -> list[int]:
    """
    Bob measures each qubit in his randomly chosen basis.
    If Bob's basis matches Alice's, he gets the correct bit.
    Otherwise, result is random (50/50).
    """
    bob_bits = []
    for qc, basis in zip(circuits, bob_bases):
        measure_qc = qc.copy()
        if basis == 'X':
            measure_qc.h(0)       # Rotate back from X basis before measuring
        measure_qc.measure(0, 0)

        job = simulator.run(measure_qc, shots=1)
        result = job.result()
        counts = result.get_counts()
        bit = int(list(counts.keys())[0])
        bob_bits.append(bit)

    return bob_bits


def sift_key(alice_bits: list[int],
             alice_bases: list[str],
             bob_bases: list[str],
             bob_bits: list[int]) -> tuple[list[int], list[int], list[int]]:
    """
    Sifting: Alice and Bob compare bases publicly.
    Only keep bits where their bases match → raw key.
    Returns (alice_key, bob_key, matching_indices)
    """
    alice_key, bob_key, indices = [], [], []
    for i, (ab, bb) in enumerate(zip(alice_bases, bob_bases)):
        if ab == bb:
            alice_key.append(alice_bits[i])
            bob_key.append(bob_bits[i])
            indices.append(i)
    return alice_key, bob_key, indices


def calculate_error_rate(alice_key: list[int], bob_key: list[int]) -> float:
    """
    Calculate QBER (Quantum Bit Error Rate).
    Compares a sample of the shared key to detect eavesdropping.
    Eve's presence typically causes ~25% error rate.
    """
    if not alice_key:
        return 0.0
    mismatches = sum(a != b for a, b in zip(alice_key, bob_key))
    return (mismatches / len(alice_key)) * 100


def get_secure_key(alice_key: list[int], bob_key: list[int]) -> list[int]:
    """
    Return the final secure key (bits where Alice and Bob agree).
    In real BB84, a subset is sacrificed for error checking.
    """
    return [a for a, b in zip(alice_key, bob_key) if a == b]


# ─────────────────────────────────────────────
# Circuit Visualization Helper
# ─────────────────────────────────────────────

def build_sample_circuit(bit: int, alice_basis: str, bob_basis: str) -> QuantumCircuit:
    """
    Build a complete sample circuit showing Alice's encoding + Bob's measurement.
    Used purely for visualization purposes.
    """
    qc = QuantumCircuit(1, 1)
    qc.barrier(label="Alice")
    if bit == 1:
        qc.x(0)
    if alice_basis == 'X':
        qc.h(0)
    qc.barrier(label="Bob")
    if bob_basis == 'X':
        qc.h(0)
    qc.measure(0, 0)
    return qc


def run_measurement_histogram(bit: int,
                               alice_basis: str,
                               bob_basis: str,
                               simulator: AerSimulator,
                               shots: int = 1024):
    """
    Run the circuit multiple times to get a histogram of outcomes.
    Matching bases → deterministic result.
    Mismatched bases → ~50/50 distribution (superposition effect).
    """
    qc = QuantumCircuit(1, 1)
    if bit == 1:
        qc.x(0)
    if alice_basis == 'X':
        qc.h(0)
    if bob_basis == 'X':
        qc.h(0)
    qc.measure(0, 0)

    job = simulator.run(qc, shots=shots)
    result = job.result()
    return result.get_counts()


# ─────────────────────────────────────────────
# Full Simulation Runner
# ─────────────────────────────────────────────

def run_bb84_simulation(n_bits: int = 20,
                        enable_eve: bool = False,
                        alice_bits_input=None):
    """
    Run the complete BB84 protocol simulation.
    
    Returns a dictionary with all simulation data for display in the UI.
    """
    simulator = AerSimulator()

    # Step 1: Alice prepares
    alice_bits = alice_bits_input if alice_bits_input else generate_random_bits(n_bits)
    alice_bases = generate_random_bases(n_bits)
    circuits = alice_encode(alice_bits, alice_bases)

    # Step 2: Eve intercepts (optional)
    eve_bits = None
    eve_bases = None
    if enable_eve:
        eve_bases = generate_random_bases(n_bits)
        circuits, eve_bits = eve_intercept(circuits, eve_bases, simulator)

    # Step 3: Bob measures
    bob_bases = generate_random_bases(n_bits)
    bob_bits = bob_measure(circuits, bob_bases, simulator)

    # Step 4: Sift key
    alice_key, bob_key, matching_indices = sift_key(
        alice_bits, alice_bases, bob_bases, bob_bits
    )

    # Step 5: Error analysis
    error_rate = calculate_error_rate(alice_key, bob_key)
    secure_key = get_secure_key(alice_key, bob_key)

    # Step 6: Build sample circuit for visualization
    sample_qc = build_sample_circuit(alice_bits[0], alice_bases[0], bob_bases[0])
    hist_counts = run_measurement_histogram(
        alice_bits[0], alice_bases[0], bob_bases[0], simulator
    )

    return {
        "n_bits": n_bits,
        "alice_bits": alice_bits,
        "alice_bases": alice_bases,
        "bob_bases": bob_bases,
        "bob_bits": bob_bits,
        "eve_bits": eve_bits,
        "eve_bases": eve_bases,
        "matching_indices": matching_indices,
        "alice_key": alice_key,
        "bob_key": bob_key,
        "error_rate": error_rate,
        "secure_key": secure_key,
        "sample_circuit": sample_qc,
        "hist_counts": hist_counts,
        "enable_eve": enable_eve,
        "eavesdropping_detected": error_rate > 10.0,
    }
