# Quantum Cryptography Simulator: BB84 Quantum Key Distribution

An interactive simulation of the BB84 Quantum Key Distribution (QKD) protocol developed using Qiskit and Streamlit. The application demonstrates secure quantum communication, key generation, eavesdropping detection, and Quantum Bit Error Rate (QBER) analysis through an interactive web interface.

## Overview

This project provides a practical implementation of the BB84 protocol, one of the foundational quantum cryptography schemes. The simulator models communication between Alice and Bob while allowing users to introduce an adversarial eavesdropper (Eve) and observe the resulting impact on key integrity and channel security.

The application illustrates key quantum computing principles including superposition, measurement collapse, basis mismatch effects, and the no-cloning theorem.

## Key Features

* Interactive BB84 protocol simulation
* Optional eavesdropper (Eve) injection
* Quantum Bit Error Rate (QBER) computation
* Qiskit-based quantum circuit generation
* Measurement histogram visualization
* Step-by-step protocol execution mode
* Secure key extraction and analysis
* Exportable key generation reports
* Comparative analysis of secure and compromised channels

## Technology Stack

* Python
* Qiskit
* Qiskit Aer
* Streamlit
* NumPy
* Matplotlib

## Project Structure

```text
quantum_crypto/
├── app.py
├── quantum_bb84.py
├── utils.py
├── requirements.txt
└── README.md
```

## Experimental Results

The simulator demonstrates expected BB84 behavior under both secure and adversarial conditions:

| Scenario            | QBER | Channel Status         |
| ------------------- | ---- | ---------------------- |
| No Eavesdropper     | ~0%  | Secure                 |
| Active Eavesdropper | >11% | Eavesdropping Detected |

The observed increase in QBER under interception validates the protocol's ability to detect unauthorized observation of transmitted qubits.

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

The application will be available locally at:

```text
http://localhost:8501
```

## Future Enhancements

* Integration with real quantum hardware backends
* Support for additional QKD protocols
* Multi-party communication simulations
* Advanced attack scenario modeling
* Performance benchmarking across simulator backends
