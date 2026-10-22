from qiskit import QuantumCircuit
from benchmark.config import BenchmarkConfig
from benchmark.models import BenchmarkResult
from benchmark.simulation import run_simulation


def run_benchmark(name: str, circuit: QuantumCircuit, noise_model: NoiseModel = None, config: BenchmarkConfig = None) -> BenchmarkResult:

    if config is None:
        config = BenchmarkConfig()

    ideal_result = run_simulation(circuit, None, config.shots)
    noisy_result = run_simulation(circuit, noise_model, config.shots)

    return BenchmarkResult(name, config.shots, ideal_result, noisy_result)
