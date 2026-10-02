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