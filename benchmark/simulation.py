from qiskit_aer.noise import NoiseModel
from qiskit_aer import AerSimulator
from qiskit import transpile, QuantumCircuit

def create_simulator(noise_model: NoiseModel = None) -> AerSimulator:
    # Create Circuit Simulator
    sim = AerSimulator(noise_model=noise_model)

    return sim

def transpile_circuit(circuit: QuantumCircuit, sim: AerSimulator):
    # Transpile to simulator
    tc = transpile(circuit, sim)

    return tc

def execute_circuit(sim_ideal: AerSimulator, tc, shots):
    # Execute
    result = sim_ideal.run(tc, shots=shots).result()

    return result

def get_counts(result_ideal):
    counts = result_ideal.get_counts()

    return counts

def run_simulation(circuit: QuantumCircuit, noise_model, shots) -> dict:
    simulator = create_simulator(noise_model)
    transpiled = transpile_circuit(circuit, simulator)
    result = execute_circuit(simulator, transpiled, shots)
    count = get_counts(result)

    return count