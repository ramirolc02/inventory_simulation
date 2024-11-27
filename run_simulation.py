from inventory_system.config import ProductConfig, SimulationConfig
from inventory_system.main import InventorySystem


def main():
    # Create configuration for 5 months simulation
    sim_config = SimulationConfig(
        max_time=24 * 30 * 5,  # 5 months in hours
        reorder_time=168,      # weekly
        lambda_exp=1.5,
        mu_order=48,
        sigma_order=3.5,
        holding_cost=0.0002,
        order_base_cost=100,
        order_penalty={"percentage": 0.03, "time_base": 48}
    )
    
    products_config = {
        "prod1": ProductConfig(
            initial_level=70,
            max_level=1000,
            price=2.5,
            demand_sizes=[1, 2, 3, 4],
            demand_prob=[0.3, 0.4, 0.2, 0.1],
            order_prices={"under": 1, "above": 0.75, "limit": 600}
        ),
        "prod2": ProductConfig(
            initial_level=70,
            max_level=1500,
            price=3.5,
            demand_sizes=[1, 2, 3, 4],
            demand_prob=[0.2, 0.2, 0.4, 0.2],
            order_prices={"under": 1.5, "above": 1.25, "limit": 800}
        )
    }
    
    # Create and run simulation
    inventory_system = InventorySystem(sim_config, products_config)
    benefit = inventory_system.run_simulation(display_chart=True)
    
    # Get and display statistics
    stats = inventory_system.get_statistics()
    print("\nSimulation Results:")
    print(f"Total Profit: {stats['total_profit']:.2f}")
    print(f"Customer Satisfaction Rate: {stats['satisfied_customers_ratio']*100:.1f}%")
    print("\nStock-out Time Percentage:")
    for prod, percentage in stats['stockout_time'].items():
        print(f"{prod}: {percentage:.1f}%")

if __name__ == "__main__":
    main() 