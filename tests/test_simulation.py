import unittest

from benchmark import BenchmarkConfig
from benchmark import create_simulator
from benchmark import transpile_circuit
from benchmark import execute_circuit
from benchmark import get_counts

from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit


class TestSimulation(unittest.TestCase):
    def test_simulation(self):
        qc = QuantumCircuit(1, 1)
        qc.measure(0, 0)

        sim = create_simulator()
        self.assertIsInstance(sim, AerSimulator)

        tc = transpile_circuit(qc, sim)
        self.assertIsNotNone(tc)

        result = execute_circuit(sim, tc, 1024)
        counts = get_counts(result)

        self.assertEqual(sum(counts.values()), 1024)


if __name__ == '__main__':
    unittest.main()
