# Inventory Management System Simulation

## Problem Description

This simulation analyzes a warehouse management system over a 5-month period to estimate:

- Expected profit
- Proportion of customers with fully satisfied demand
- Percentage of time inventory levels remain at zero

The system manages two products with an initial inventory level of 70 units each, implementing periodic reordering policies and handling variable customer demand.

## Project Structure
```
inventory_simulation/                   # Root project directory
    ├── inventory_system/               # Core package containing main logic
    │   ├── __init__.py                 # Package initialization
    │   ├── config.py                   # Configuration management
    │   ├── events.py                   # Event handling system
    │   ├── main.py                     # Primary simulation engine
    │   ├── models.py                   # Product and inventory models
    │   └── visualization.py            # Data visualization utilities
    ├── inventory-evolution/            # Directory for generated plot images
    ├── run_simulation.py               # Main script to launch simulation
    └── requirements.txt                # Project dependencies list
```
## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ramirolc02/inventory-simulation.git
   cd inventory-simulation
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the simulation:

   ```bash
   python run_simulation.py
   ```

2. Check the generated plots in the `inventory-evolution/` directory:

   - `inventory_5months.png`: Complete 5-month simulation
   - `inventory_5days.png`: Detailed view of first 5 days

3. Review simulation logs in `inventory_system/inventory_simulation.log`

## Configuration

Key simulation parameters can be adjusted in `run_simulation.py`:

- Simulation duration (default: 5 months)
- Reorder frequency (default: weekly)
- Initial inventory levels
- Product prices and demand distributions
- Order costs and penalties

See `SimulationConfig` and `ProductConfig` in `config.py` for all available options.
