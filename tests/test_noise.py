import unittest

from qiskit_aer.noise import NoiseModel, thermal_relaxation_error, depolarizing_error, ReadoutError

from dataclasses import dataclass

@dataclass
class BenchmarkConfig:
    num_qubits: int = 4
    shots: int = 8192
    reps: int = 2

    t1_us: float = 100.0  # T1 time in microseconds
    t2_us: float = 100.0  # T2 time in microseconds
    gate_time_ns: float = 50.0  # Gate time in nanoseconds

    depol_1q: float = 0.001  # Depolarizing error for 1-qubit gates
    depol_2q: float = 0.01  # Depolarizing error for 2-qubit gates
    readout_error_prob: float = 0.02  # Readout error probability

class MyTestCase(unittest.TestCase):
    def test_noise(self):
        self.assertEqual(self.create_thermal_error(100.0, 100.0, 50.0, port=1), thermal_relaxation_error(0.0001, 0.0001, 5e-08))
        self.assertEqual(self.create_depolarizing_error(0.001, 1), depolarizing_error(0.001, 1))
        self.assertEqual(self.create_readout_error(0.02), ReadoutError([[0.98, 0.02], [0.02, 0.98]]))
        noise_model = self.build_noise_model(BenchmarkConfig())
        self.assertIsNotNone(noise_model)

    def microseconds_to_seconds(self, microseconds: float) -> float:
        return microseconds * 1e-6

    def nanoseconds_to_seconds(self, nanoseconds: float) -> float:
        return nanoseconds * 1e-9

    def create_thermal_error(self, t1_us: float, t2_us: float, gate_time_ns: float, port: int):
        t1_s = self.microseconds_to_seconds(t1_us)
        t2_s = self.microseconds_to_seconds(t2_us)
        gate_time_s = self.nanoseconds_to_seconds(gate_time_ns)
        thermal_error = thermal_relaxation_error(t1_s, t2_s, gate_time_s)

        if port == 1:
            return thermal_error
        elif port == 2:
            return thermal_error.expand(thermal_error)

    def create_depolarizing_error(self, depol: float, qubits: int):

        return depolarizing_error(depol, qubits)

    def create_readout_error(self, readout: float) -> ReadoutError:
        prob = 1 - readout

        return ReadoutError([[prob, readout], [readout, prob]])

    def build_noise_model(self, config: BenchmarkConfig):
        noise_model = NoiseModel()

        # Error for 1-qubit gates
        thermal_error_1 = self.create_thermal_error(config.t1_us, config.t2_us, config.gate_time_ns, port=1)
        depol_error_1 = self.create_depolarizing_error(config.depol_1q, 1)
        error_1q = thermal_error_1.compose(depol_error_1)

        # Error for 2-qubit gates
        thermal_error_2 = self.create_thermal_error(config.t1_us, config.t2_us, config.gate_time_ns, port=2)
        depol_2q_error = self.create_depolarizing_error(config.depol_2q, 2)
        error_2q = thermal_error_2.compose(depol_2q_error)

        # Add errors to all ports that will be used or are important.
        single_qubit_gates = ['u1', 'u2', 'u3', 'rx', 'ry', 'rz', 'sx', 'x']
        two_qubit_gates = ['cx', 'cz']

        for q in range(config.num_qubits):
            noise_model.add_quantum_error(error_1q, single_qubit_gates, [q])

        for i in range(config.num_qubits - 1):
            noise_model.add_quantum_error(error_2q, two_qubit_gates, [i, i + 1])

        # Reading error (2x2 confusion matrix)
        readout_err = self.create_readout_error(config.readout_error_prob)
        noise_model.add_all_qubit_readout_error(readout_err)

        return noise_model


if __name__ == '__main__':
    unittest.main()
