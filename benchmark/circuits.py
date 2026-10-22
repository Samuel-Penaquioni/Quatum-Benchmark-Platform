from qiskit import QuantumCircuit
from qiskit.circuit.library import efficient_su2
from benchmark.config import BenchmarkConfig
import numpy as np

def create_ghz_circuit(config: BenchmarkConfig) -> QuantumCircuit:
    qc = QuantumCircuit(config.num_qubits, name='GHZ')
    qc.h(0)
    # Entangled the qubits
    for i in range(config.num_qubits - 1):
        qc.cx(i, i + 1)
    qc.measure_all(add_bits=True)
    return qc

def create_efficientsu2_circuit(config: BenchmarkConfig) -> QuantumCircuit:
    ansatz = efficient_su2(
        num_qubits=config.num_qubits,
        su2_gates=['ry', 'rz'],
        entanglement='linear',
        reps=config.reps
    )
    # Assign parameters (e.g., zeros or random numbers)
    params = np.zeros(ansatz.num_parameters)
    qc = ansatz.assign_parameters(params)
    qc.measure_all(add_bits=True)
    return qc