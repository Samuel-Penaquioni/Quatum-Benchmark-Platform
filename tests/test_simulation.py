import unittest

from benchmark.config import BenchmarkConfig
from benchmark.models import BenchmarkResult
from benchmark.simulation import create_simulator, transpile_circuit, execute_circuit, get_counts

from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit


class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.config = BenchmarkConfig(
            num_qubits=1,
            shots=1024
        )



    def test_simulator_creation(self):
        sim = create_simulator()
        self.assertIsInstance(sim, AerSimulator)


    def test_simulation_respects_config(self):

        qc = QuantumCircuit(
            self.config.num_qubits,
            self.config.num_qubits
        )

        qc.measure(0, 0)

        sim = create_simulator()

        tc = transpile_circuit(qc, sim)
        result = execute_circuit(
            sim,
            tc,
            self.config.shots
        )

        counts = get_counts(result)

        self.assertEqual(
            sum(counts.values()),
            self.config.shots
        )


    def test_benchmark_result(self):

        ideal_counts = {"0": self.config.shots}
        noisy_counts = {"0": self.config.shots}

        benchmark_result = BenchmarkResult(
            circuit_name="TestCircuit",
            shots=self.config.shots,
            ideal_counts=ideal_counts,
            noisy_counts=noisy_counts,
        )

        self.assertEqual(
            benchmark_result.shots,
            self.config.shots
        )

        self.assertEqual(
            benchmark_result.ideal_counts,
            ideal_counts
        )

        self.assertEqual(
            benchmark_result.noisy_counts,
            noisy_counts
        )

if __name__ == '__main__':
    unittest.main()
