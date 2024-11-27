from dataclasses import dataclass, field
from typing import Dict, List


class Product:
    def __init__(self, name: str, config: 'ProductConfig'):
        self.name = name
        self.level = config.initial_level
        self.max_level = config.max_level
        self.price = config.price
        self.demand_sizes = config.demand_sizes
        self.demand_prob = config.demand_prob
        self.order_prices = config.order_prices
        
        self.history = {
            "level": [config.initial_level],
            "total_benefit": [0],
            "benefits": [],
            "loss_sales": [],
            "sin_inventario": [],
            "perdidas": 0
        }
    
    def update_level(self, change: int) -> None:
        """Update inventory level"""
        new_level = max(0, self.level + change)
        self.level = new_level
        
        # Only append if the level actually changed
        if not self.history["level"] or self.history["level"][-1] != new_level:
            self.history["level"].append(new_level)
        
    def calculate_order_quantity(self) -> int:
        """Calculate quantity needed to reach max level"""
        return self.max_level - self.level
        
    def get_order_price(self, quantity: int) -> float:
        """Get price per unit based on order quantity"""
        if quantity > self.order_prices["limit"]:
            return self.order_prices["above"]
        return self.order_prices["under"] 