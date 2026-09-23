from qiskit import QuantumCircuit
from qiskit.circuit.library import efficient_su2
from qiskit_aer.noise import NoiseModel, thermal_relaxation_error, depolarizing_error, ReadoutError
from qiskit_aer import AerSimulator
from qiskit import transpile
import numpy as np

from dataclasses import dataclass

DEFAULT_T1_US = 100.0
DEFAULT_T2_US = 100.0
DEFAULT_GATE_TIME_NS = 50.0

@dataclass
class BenchmarkConfig:
    num_qubits: int = 4
    shots: int = 8192
    reps: int = 2

@dataclass
class BenchmarkResult:
    circuit_name: str
    shots: int
    ideal_counts: dict
    noisy_counts: dict

def microseconds_to_seconds(microseconds: float) -> float:
    return microseconds * 1e-6

def nanoseconds_to_seconds(nanoseconds: float) -> float:
    return nanoseconds * 1e-9

def create_ghz_circuit(num_qubits: int = 4) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(0)
    # Entangled the qubits
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc

def create_efficientsu2_circuit(num_qubits: int = 4, reps: int = 2) -> QuantumCircuit:
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

def create_thermal_error(t1_us: float, t2_us: float, gate_time_ns: float):
    t1_s = microseconds_to_seconds(t1_us)
    t2_s = microseconds_to_seconds(t2_us)
    gate_time_s = nanoseconds_to_seconds(gate_time_ns)

    return thermal_relaxation_error(t1_s, t2_s, gate_time_s)

def create_depolarizing_error(depol: float, qubits: int):

    return depolarizing_error(depol, qubits)

def create_readout_error(readout: float) -> ReadoutError:
    prob = 1 - readout

    return ReadoutError([[prob, readout], [readout, prob]])


def build_noise_model(
        num_qubits: int = BenchmarkConfig.num_qubits,
        t1_us: float=DEFAULT_T1_US,
        t2_us: float=DEFAULT_T2_US,
        gate_time_ns: float=DEFAULT_GATE_TIME_NS,
        depol_1q: float=0.001,
        depol_2q: float=0.01,
        readout_error_prob: float=0.02
):
    noise_model = NoiseModel()

    # Error for 1-qubit gates
    thermal_error_1 = create_thermal_error(t1_us, t2_us, gate_time_ns)
    depol_error_1 = create_depolarizing_error(depol_1q, 1)
    error_1q = thermal_error_1.compose(depol_error_1)

    # Error for 2-qubit gates
    thermal_error_2 = create_thermal_error(t1_us, t2_us, gate_time_ns)
    depol_2q_error = create_depolarizing_error(depol_2q, 2)
    error_2q = thermal_error_2.compose(depol_2q_error)

    # Add errors to all ports that will be used or are important.
    single_qubit_gates = ['u1', 'u2', 'u3', 'rx', 'ry', 'rz', 'sx', 'x']
    two_qubit_gates = ['cx', 'cz']

    for q in range(num_qubits):
        noise_model.add_quantum_error(error_1q, single_qubit_gates, [q])

    for i in range(num_qubits - 1):
        noise_model.add_quantum_error(error_2q, two_qubit_gates, [i , i + 1])

    # Reading error (2x2 confusion matrix)
    readout_err = create_readout_error(readout_error_prob)
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
    count = get_counts(execute_circuit(create_simulator(noise_model), transpile_circuit(circuit, create_simulator(noise_model)), shots))

    return count

def run_benchmark(circuit: QuantumCircuit, noise_model: NoiseModel = None, shots: int = BenchmarkConfig.shots) -> BenchmarkResult:
    ideal_result = run_simulation(circuit, None, shots)
    noisy_result = run_simulation(circuit, noise_model, shots)

    return BenchmarkResult(circuit.name, shots, ideal_result, noisy_result)

if __name__ == '__main__':
    config = BenchmarkConfig()
    noise_model = build_noise_model()
    ghz = create_ghz_circuit()
    efficientsu2 = create_efficientsu2_circuit()
    result_ghz = run_benchmark(ghz, noise_model=noise_model, shots=BenchmarkConfig.shots)
    result_efficientsu2 = run_benchmark(efficientsu2, noise_model=noise_model)
    print(result_ghz)
    print(result_efficientsu2)
