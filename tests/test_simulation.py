import unittest

from qiskit_aer import AerSimulator
from qiskit import transpile
from qiskit import QuantumCircuit
from qiskit_aer.noise import NoiseModel


class MyTestCase(unittest.TestCase):
    def test_simulation(self):
        qc = QuantumCircuit(1, 1)
        qc.measure(0, 0)

        sim = self.create_simulator()
        self.assertIsInstance(sim, AerSimulator)

        tc = self.transpile_circuit(qc, sim)
        self.assertIsNotNone(tc)

        result = self.execute_circuit(sim, tc, 1024)
        counts = self.get_counts(result)

        self.assertEqual(sum(counts.values()), 1024)

    def create_simulator(self, noise_model: NoiseModel = None) -> AerSimulator:
        # Create Circuit Simulator
        sim = AerSimulator(noise_model=noise_model)

        return sim

    def transpile_circuit(self, circuit: QuantumCircuit, sim: AerSimulator):
        # Transpile to simulator
        tc = transpile(circuit, sim)

        return tc

    def execute_circuit(self, sim_ideal: AerSimulator, tc, shots):
        # Execute
        result = sim_ideal.run(tc, shots=shots).result()

        return result

    def get_counts(self, result_ideal):
        counts = result_ideal.get_counts()

        return counts


    def run_simulation(self, circuit: QuantumCircuit, noise_model, shots) -> dict:
        simulator = self.create_simulator(noise_model)
        transpiled = self.transpile_circuit(circuit, simulator)
        result = self.execute_circuit(simulator, transpiled, shots)
        count = self.get_counts(result)

        return count

if __name__ == '__main__':
    unittest.main()
