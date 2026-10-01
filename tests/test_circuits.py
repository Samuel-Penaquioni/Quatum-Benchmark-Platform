import unittest

from benchmark import BenchmarkConfig
from benchmark import create_ghz_circuit
from benchmark import create_efficientsu2_circuit

class TestCircuits(unittest.TestCase):
    def test_circuits(self):
        self.assertEqual(create_ghz_circuit(BenchmarkConfig(num_qubits=3)).num_qubits, 3)
        self.assertEqual(create_efficientsu2_circuit(BenchmarkConfig(num_qubits=3, reps=1)).num_qubits, 3)

if __name__ == '__main__':
    unittest.main()
