from qiskit import QuantumCircuit
from qiskit.circuit.library import efficient_su2
from qiskit_aer.noise import NoiseModel, thermal_relaxation_error, depolarizing_error, ReadoutError
from qiskit_aer import AerSimulator
from qiskit import transpile
import numpy as np

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

@dataclass
class BenchmarkResult:
    circuit_name: str
    shots: int
    ideal_counts: dict[str, int]
    noisy_counts: dict[str, int]

def microseconds_to_seconds(microseconds: float) -> float:
    return microseconds * 1e-6

def nanoseconds_to_seconds(nanoseconds: float) -> float:
    return nanoseconds * 1e-9

def create_ghz_circuit(config: BenchmarkConfig) -> QuantumCircuit:
    qc = QuantumCircuit(config.num_qubits, name='GHZ')
    qc.h(0)
    # Entangled the qubits
    for i in range(config.num_qubits - 1):
        qc.cx(i, i + 1)
    qc.measure_all(add_bits=True)
    return qc

def create_efficientsu2_circuit(config: BenchmarkConfig) -> QuantumCircuit:
    ansatz = efficient_su2(
        num_qubits=config.num_qubits,
        su2_gates=['ry', 'rz'],
        entanglement='linear',
        reps=config.reps
    )
    # Assign parameters (e.g., zeros or random numbers)
    params = np.zeros(ansatz.num_parameters)
    qc = ansatz.assign_parameters(params)
    qc.measure_all(add_bits=True)
    return qc

def create_thermal_error(t1_us: float, t2_us: float, gate_time_ns: float, port: int):
    t1_s = microseconds_to_seconds(t1_us)
    t2_s = microseconds_to_seconds(t2_us)
    gate_time_s = nanoseconds_to_seconds(gate_time_ns)
    thermal_error = thermal_relaxation_error(t1_s, t2_s, gate_time_s)

    if port == 1:
        return thermal_error
    elif port == 2:
        return thermal_error.expand(thermal_error)

def create_depolarizing_error(depol: float, qubits: int):

    return depolarizing_error(depol, qubits)

def create_readout_error(readout: float) -> ReadoutError:
    prob = 1 - readout

    return ReadoutError([[prob, readout], [readout, prob]])

def build_noise_model(config: BenchmarkConfig):
    noise_model = NoiseModel()

    # Error for 1-qubit gates
    thermal_error_1 = create_thermal_error(config.t1_us, config.t2_us, config.gate_time_ns, port=1)
    depol_error_1 = create_depolarizing_error(config.depol_1q, 1)
    error_1q = thermal_error_1.compose(depol_error_1)

    # Error for 2-qubit gates
    thermal_error_2 = create_thermal_error(config.t1_us, config.t2_us, config.gate_time_ns, port=2)
    depol_2q_error = create_depolarizing_error(config.depol_2q, 2)
    error_2q = thermal_error_2.compose(depol_2q_error)

    # Add errors to all ports that will be used or are important.
    single_qubit_gates = ['u1', 'u2', 'u3', 'rx', 'ry', 'rz', 'sx', 'x']
    two_qubit_gates = ['cx', 'cz']

    for q in range(config.num_qubits):
        noise_model.add_quantum_error(error_1q, single_qubit_gates, [q])

    for i in range(config.num_qubits - 1):
        noise_model.add_quantum_error(error_2q, two_qubit_gates, [i , i + 1])

    # Reading error (2x2 confusion matrix)
    readout_err = create_readout_error(config.readout_error_prob)
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

def run_simulation(circuit: QuantumCircuit, noise_model, shots) -> dict:
    simulator = create_simulator(noise_model)
    transpiled = transpile_circuit(circuit, simulator)
    result = execute_circuit(simulator, transpiled, shots)
    count = get_counts(result)

    return count

def run_benchmark(name: str, circuit: QuantumCircuit, noise_model: NoiseModel = None, config: BenchmarkConfig = None) -> BenchmarkResult:

    if config is None:
        config = BenchmarkConfig()

    ideal_result = run_simulation(circuit, None, config.shots)
    noisy_result = run_simulation(circuit, noise_model, config.shots)

    return BenchmarkResult(name, config.shots, ideal_result, noisy_result)

if __name__ == '__main__':
    config = BenchmarkConfig()
    noise_model = build_noise_model(config)
    ghz = create_ghz_circuit(config)
    efficientsu2 = create_efficientsu2_circuit(config)
    result_ghz = run_benchmark("GHZ", ghz, noise_model=noise_model, config=config)
    result_efficientsu2 = run_benchmark("EfficientSU2", efficientsu2, noise_model=noise_model, config=config)
    print(result_ghz)
    print(result_efficientsu2)
