from qiskit import QuantumCircuit
from qiskit.circuit.library import efficient_su2
from qiskit_aer.noise import NoiseModel, thermal_relaxation_error, depolarizing_error, ReadoutError
from qiskit_aer import AerSimulator
from qiskit import transpile
import numpy as np


def create_ghz_circuit(num_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(0)
    # Entangled the qubits
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc

def create_efficientsu2_circuit(num_qubits: int, reps: int = 2) -> QuantumCircuit:
    ansatz = efficient_su2(
        num_qubits=num_qubits,
        su2_gates=['ry', 'rz'],
        entanglement='linear',
        reps=reps
    )
    # Assign parameters (e.g., zeros or random numbers)
    params = np.zeros(ansatz.num_parameters)
    qc = ansatz.assign_parameters(params)
    qc.measure_all()
    return qc

def build_noise_model(
        num_qubits: int,
        t1_us: float=100.0,
        t2_us: float=100.0,
        gate_time_ns: float=50.0,
        depol_1q: float=0.001,
        depol_2q: float=0.01,
        readout_error_prob: float=0.02
):
    noise_model = NoiseModel()
    gate_time_s = gate_time_ns * 1e-9
    t1_s = t1_us * 1e-6
    t2_s = t2_us * 1e-6

    # Error for 1-qubit gates
    thermal_1q = thermal_relaxation_error(t1_s, t2_s, gate_time_s)
    depol_1q_error = depolarizing_error(depol_1q, 1)
    error_1q = thermal_1q.compose(depol_1q_error)

    # Error for 2-qubit gates
    thermal_2q = thermal_relaxation_error(t1_s, t2_s, gate_time_s)
    depol_2q_error = depolarizing_error(depol_2q, 2)
    error_2q = thermal_2q.compose(depol_2q_error)

    # Add errors to all ports that will be used or are important.
    single_qubit_gates = ['u1', 'u2', 'u3', 'rx', 'ry', 'rz', 'sx', 'x']
    two_qubit_gates = ['cx', 'cz']

    for q in range(num_qubits):
        noise_model.add_quantum_error(error_1q, single_qubit_gates, [q])

    for i in range(num_qubits - 1):
        noise_model.add_quantum_error(error_2q, two_qubit_gates, [i , i + 1])

    # Reading error (2x2 confusion matrix)
    prob_0_given_0 = 1 - readout_error_prob
    prob_1_given_1 = 1 - readout_error_prob
    readout_err = ReadoutError([[prob_0_given_0, readout_error_prob], [readout_error_prob, prob_1_given_1]])
    noise_model.add_all_qubit_readout_error(readout_err)

    return noise_model

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

def run_ideal_simulation(circuit: QuantumCircuit, shots):
    ideal_circuit = get_counts(execute_circuit(create_simulator(), transpile_circuit(circuit, create_simulator()), shots))

    return ideal_circuit

def run_noisy_simulation(circuit: QuantumCircuit, noise_model, shots):
    noisy_circuit = get_counts(execute_circuit(create_simulator(noise_model), transpile_circuit(circuit, create_simulator(noise_model)), shots))

    return noisy_circuit

def run_benchmark(circuit: QuantumCircuit, noise_model: NoiseModel = None, shots: int = 8192):
    ideal_result = run_ideal_simulation(circuit, shots)
    noisy_result = run_noisy_simulation(circuit, noise_model, shots)

    return ideal_result, noisy_result

if __name__ == '__main__':
    num_qubits = 4
    noise_model = build_noise_model(num_qubits)
    ghz = create_ghz_circuit(num_qubits)
    efficientsu2 = create_efficientsu2_circuit(num_qubits)
    counts_ideal_ghz, counts_noisy_ghz = run_benchmark(ghz, noise_model=noise_model)
    counts_ideal_efficientsu2, counts_noisy_efficientsu2 = run_benchmark(efficientsu2, noise_model=noise_model)
