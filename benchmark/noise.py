from qiskit_aer.noise import NoiseModel, thermal_relaxation_error, depolarizing_error, ReadoutError
from benchmark.config import BenchmarkConfig
from benchmark.conversions import *

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
