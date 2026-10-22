import unittest

from benchmark.config import BenchmarkConfig
from benchmark.noise import create_thermal_error, create_depolarizing_error, create_readout_error, build_noise_model

class TestNoise(unittest.TestCase):
    def test_noise(self):
        self.assertEqual(create_thermal_error(100.0, 100.0, 50.0, port=1).num_qubits, 1)
        self.assertEqual(create_thermal_error(100.0, 100.0, 50.0, port=2).num_qubits, 2)
        self.assertEqual(create_depolarizing_error(0.001, 1).num_qubits, 1)
        self.assertEqual(create_readout_error(0.02).num_qubits, 1)
        noise_model = build_noise_model(BenchmarkConfig())
        self.assertIsNotNone(noise_model)


if __name__ == '__main__':
    unittest.main()
