from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ProductConfig:
    initial_level: int
    max_level: int
    price: float
    demand_sizes: List[int]
    demand_prob: List[float]
    order_prices: Dict[str, float]

@dataclass
class SimulationConfig:
    max_time: float
    reorder_time: float
    lambda_exp: float
    mu_order: float
    sigma_order: float
    holding_cost: float
    order_base_cost: float
    order_penalty: Dict[str, float]
    
    @classmethod
    def default(cls):
        return cls(
            max_time=24 * 30 * 2,  # 2 months
            reorder_time=168,      # weekly
            lambda_exp=1.5,
            mu_order=48,
            sigma_order=3.5,
            holding_cost=0.0002,
            order_base_cost=100,
            order_penalty={"percentage": 0.03, "time_base": 48}
        ) 