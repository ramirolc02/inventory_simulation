import matplotlib.pyplot as plt
import numpy as np


class InventoryVisualizer:
    def __init__(self, inventory_system):
        self.system = inventory_system
        
    def plot_inventory_levels(self, time_limit=None, title=None, save_path=None):
        """Plot inventory levels for both products
        
        Args:
            time_limit (float, optional): Limit the plot to first X hours
            title (str, optional): Custom title for the plot
            save_path (str, optional): Path to save the plot
        """
        fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 7))
        
        # Get time points
        time_points = np.array(self.system.time_points)
        
        # Filter time points if limit is set
        if time_limit:
            time_mask = time_points <= time_limit
            time_points = time_points[time_mask]
        
        for ax, prod_name in zip([ax1, ax2], ["prod1", "prod2"]):
            product = self.system.products[prod_name]
            levels = np.array(product.history["level"])
            
            # Ensure lengths match
            min_len = min(len(time_points), len(levels))
            time_points_plot = time_points[:min_len]
            levels_plot = levels[:min_len]
            
            # Plot inventory levels
            ax.step(
                time_points_plot,
                levels_plot,
                where="post",
                label=f"Unidades de {prod_name}"
            )
            
            # Add order markers
            self._add_order_markers(ax, time_limit)
            
            # Customize appearance
            self._customize_axis(ax, prod_name)
        
        if title:
            fig.suptitle(title)
        
        # Adjust layout to prevent text overlap
        plt.tight_layout()
        
        # Save the plot if path is provided
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
        plt.show()
        
    def _add_order_markers(self, ax, time_limit):
        """Add order markers to plot"""
        for order_time in self.system.order_times:
            if order_time != 0 and (time_limit is None or order_time <= time_limit):
                self._plot_order_marker(ax, order_time)
                
    @staticmethod
    def _plot_order_marker(ax, order_time):
        ax.axvline(
            x=order_time,
            color="dodgerblue",
            linestyle="--",
            label=f"Pedido en {round(order_time,1)} h"
        )
        ax.text(
            x=order_time - (order_time / 100),
            y=200,
            s=f"t={round(order_time,2)} h",
            rotation="vertical",
            fontsize="x-small",
            bbox=dict(
                boxstyle="round,pad=0.3",
                edgecolor="dodgerblue",
                facecolor="white",
                alpha=0.8
            ),
            ha="left"
        )
                
    @staticmethod
    def _customize_axis(ax, prod_name):
        """Customize axis appearance"""
        ax.grid(True, alpha=0.4)
        ax.set_ylabel(f"Unidades de {prod_name}") 