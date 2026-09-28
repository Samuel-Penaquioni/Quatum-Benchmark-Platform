import unittest

from qiskit import QuantumCircuit
from qiskit.circuit.library import efficient_su2
import numpy as np

from dataclasses import dataclass

@dataclass
class BenchmarkConfig:
    num_qubits: int = 4
    shots: int = 8192
    reps: int = 2


class MyTestCase(unittest.TestCase):
    def test_circuits(self):
        self.assertEqual(self.create_ghz_circuit(BenchmarkConfig(num_qubits=3)).num_qubits, 3)
        self.assertEqual(self.create_efficientsu2_circuit(BenchmarkConfig(num_qubits=3, reps=1)).num_qubits, 3)

    def create_ghz_circuit(self, config: BenchmarkConfig) -> QuantumCircuit:
        qc = QuantumCircuit(config.num_qubits, name='GHZ')
        qc.h(0)
        # Entangled the qubits
        for i in range(config.num_qubits - 1):
            qc.cx(i, i + 1)
        qc.measure_all(add_bits=True)
        return qc

    def create_efficientsu2_circuit(self, config: BenchmarkConfig) -> QuantumCircuit:
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


if __name__ == '__main__':
    unittest.main()
