import unittest

from benchmark import BenchmarkConfig
from benchmark import create_thermal_error
from benchmark import create_readout_error
from benchmark import create_depolarizing_error
from benchmark import build_noise_model

from qiskit_aer.noise import thermal_relaxation_error, depolarizing_error, ReadoutError

class TestNoise(unittest.TestCase):
    def test_noise(self):
        self.assertEqual(create_thermal_error(100.0, 100.0, 50.0, port=1), thermal_relaxation_error(0.0001, 0.0001, 5e-08))
        self.assertEqual(create_depolarizing_error(0.001, 1), depolarizing_error(0.001, 1))
        self.assertEqual(create_readout_error(0.02), ReadoutError([[0.98, 0.02], [0.02, 0.98]]))
        noise_model = build_noise_model(BenchmarkConfig())
        self.assertIsNotNone(noise_model)


if __name__ == '__main__':
    unittest.main()
