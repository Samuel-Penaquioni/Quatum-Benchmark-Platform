import unittest

from benchmark.config import BenchmarkConfig
from benchmark.circuits import create_ghz_circuit, create_efficientsu2_circuit

class TestCircuits(unittest.TestCase):
    def test_ghz_number_of_qubits(self):
        self.assertEqual(create_ghz_circuit(BenchmarkConfig(num_qubits=3)).num_qubits, 3)

    def test_efficientsu2_number_of_qubits(self):
        self.assertEqual(create_efficientsu2_circuit(BenchmarkConfig(num_qubits=3)).num_qubits, 3)

if __name__ == '__main__':
    unittest.main()
