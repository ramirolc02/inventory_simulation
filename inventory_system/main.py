import logging
import os
from datetime import datetime
from typing import Dict

import numpy as np

from .config import ProductConfig, SimulationConfig
from .events import Event, EventQueue, EventType
from .models import Product
from .visualization import InventoryVisualizer


class InventorySystem:
    def __init__(self, config: SimulationConfig, products_config: Dict[str, ProductConfig]):
        # Setup logging
        self._setup_logging()
        
        self.config = config
        self.products = {
            name: Product(name, prod_config)
            for name, prod_config in products_config.items()
        }
        
        self.event_queue = EventQueue()
        self.time = 0
        self.beneficio = 0
        self.time_points = [0]
        self.order_times = []
        self.last_order_time = 0
        
        self.client_satisfied = 0
        self.client_not_satisfied = 0
        self.holding_total = 0
        
        self.visualizer = InventoryVisualizer(self)
        
        logging.info("Initialized InventorySystem")
        
    def _setup_logging(self):
        """Setup logging configuration"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(current_dir, "inventory_simulation.log")
        
        logging.basicConfig(
            filename=log_file,
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.INFO,
            filemode='w'
        )
        
        # Log simulation start
        logging.info(f"Starting new simulation at {datetime.now()}")
        
    def get_statistics(self):
        """Calculate and return simulation statistics"""
        stats = {
            'total_profit': self.beneficio,
            'satisfied_customers_ratio': self.client_satisfied / (self.client_satisfied + self.client_not_satisfied),
            'stockout_time': {}
        }
        
        for name, product in self.products.items():
            total_stockout_time = sum(1 for level in product.history['level'] if level == 0)
            stockout_percentage = (total_stockout_time / len(product.history['level'])) * 100
            stats['stockout_time'][name] = stockout_percentage
            
        logging.info(f"Final statistics: {stats}")
        return stats
        
    def run_simulation(self, display_chart=True):
        """Run the complete simulation"""
        if not self._initialize_simulation():
            return -1
            
        while self._simulation_active():
            self._process_next_event()
            
        if display_chart:
            # Create directory if it doesn't exist
            os.makedirs('inventory-evolution', exist_ok=True)
            
            # Plot and save full 5 months
            self.visualizer.plot_inventory_levels(
                title="Inventory Levels - 5 Months",
                save_path="inventory-evolution/inventory_5months.png"
            )
            
            # Plot and save first 5 days
            self.visualizer.plot_inventory_levels(
                time_limit=5*24,  # 5 days in hours
                title="Inventory Levels - First 5 Days",
                save_path="inventory-evolution/inventory_5days.png"
            )
            
        # Calculate and log final statistics
        stats = self.get_statistics()
        logging.info("Simulation completed")
        
        return self.beneficio
    
    def _initialize_simulation(self):
        """Initialize simulation state"""
        # Generate first customer arrival
        first_arrival = np.random.exponential(self.config.lambda_exp)
        if first_arrival > self.config.max_time:
            logging.error("Initial demand exceeds simulation time")
            return False
            
        self.event_queue.add_event(Event(
            time=first_arrival,
            type=EventType.CUSTOMER_ARRIVAL,
            data={}
        ))
        return True
    
    def _simulation_active(self):
        """Check if simulation should continue"""
        next_event = self.event_queue.peek_next_time()
        return next_event != float('inf') and next_event < self.config.max_time
    
    def _process_next_event(self):
        """Process the next event"""
        event = self.event_queue.get_next_event()
        self.time = event.time
        
        if event.type == EventType.CUSTOMER_ARRIVAL:
            self._handle_customer_arrival()
        else:
            self._handle_order_arrival(event.data)
            
        # Check for periodic order
        if self.time - self.last_order_time >= self.config.reorder_time:
            self._place_periodic_order()
    
    def _handle_customer_arrival(self):
        """Handle customer arrival event"""
        # Add time point before processing demands
        self.time_points.append(self.time)
        
        for prod_name, product in self.products.items():
            demand = np.random.choice(
                product.demand_sizes,
                p=product.demand_prob
            )
            
            if demand <= product.level:
                self._satisfy_demand(product, demand)
            else:
                self._handle_shortage(product, demand)
                
        # Schedule next arrival
        next_arrival = self.time + np.random.exponential(self.config.lambda_exp)
        if next_arrival < self.config.max_time:
            self.event_queue.add_event(Event(
                time=next_arrival,
                type=EventType.CUSTOMER_ARRIVAL,
                data={}
            ))
    
    def _satisfy_demand(self, product: Product, demand: int) -> None:
        """Handle satisfied demand
        
        Args:
            product: Product instance
            demand: Quantity demanded
        """
        # Update product level
        product.update_level(-demand)
        
        # Update benefit
        benefit = demand * product.price
        product.history["total_benefit"].append(
            product.history["total_benefit"][-1] + benefit
        )
        product.history["benefits"].append(benefit)
        self.beneficio += benefit
        
        self.client_satisfied += 1
        logging.info(f"Satisfied demand of {demand} units for {product.name}")
    
    def _handle_shortage(self, product: Product, demand: int) -> None:
        """Handle demand when there's not enough inventory
        
        Args:
            product: Product instance
            demand: Quantity demanded
        """
        current_level = product.level
        
        # Can only sell what's available
        if current_level > 0:
            benefit = current_level * product.price
            product.history["total_benefit"].append(
                product.history["total_benefit"][-1] + benefit
            )
            product.history["benefits"].append(benefit)
            self.beneficio += benefit
            
            # Calculate lost sales
            lost_amount = (demand - current_level) * product.price
            product.history["perdidas"] += lost_amount
            product.history["loss_sales"].append(product.history["perdidas"])
            
            # Update level to 0
            product.update_level(-current_level)
        
        # Record stockout time
        product.history["sin_inventario"].append(self.time)
        
        self.client_not_satisfied += 1
        logging.info(f"Stockout: Could not satisfy demand of {demand} units for {product.name}")
    
    def _place_periodic_order(self) -> None:
        """Place periodic order for both products"""
        self.last_order_time = self.time
        
        # Calculate holding cost since last event
        self.holding_total += (self.time - self.time_points[-1]) * self.config.holding_cost * sum(
            product.level for product in self.products.values()
        )
        
        # Generate lead time
        lead_time = np.random.normal(self.config.mu_order, self.config.sigma_order)
        delivery_time = self.time + lead_time
        
        order_data = {"quantities": {}}
        total_order_cost = self.config.order_base_cost
        
        # Calculate order quantities and costs for each product
        for name, product in self.products.items():
            order_quantity = product.calculate_order_quantity()
            order_data["quantities"][name] = order_quantity
            
            # Calculate cost based on quantity
            unit_price = product.get_order_price(order_quantity)
            total_order_cost += order_quantity * unit_price
        
        # Apply time penalty if applicable
        if abs(lead_time - self.config.mu_order) > 3:
            penalty_factor = (
                1 - self.config.order_penalty["percentage"]
                if lead_time > self.config.mu_order
                else 1 + self.config.order_penalty["percentage"]
            )
            total_order_cost *= penalty_factor
        
        order_data["cost"] = total_order_cost
        
        # Schedule order arrival
        self.event_queue.add_event(Event(
            time=delivery_time,
            type=EventType.ORDER_ARRIVAL,
            data=order_data
        ))
        
        self.order_times.append(self.time)
        logging.info(f"Placed periodic order at {self.time}, arriving at {delivery_time}")
    
    def _handle_order_arrival(self, order_data: dict) -> None:
        """Handle arrival of ordered products
        
        Args:
            order_data: Dictionary containing order information
        """
        # Update inventory levels
        for name, quantity in order_data["quantities"].items():
            product = self.products[name]
            product.update_level(quantity)
        
        # Record time point for visualization
        self.time_points.append(self.time)
        
        logging.info(f"Order arrived at {self.time}")
        