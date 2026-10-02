from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    circuit_name: str
    shots: int
    ideal_counts: dict[str, int]
    noisy_counts: dict[str, int]