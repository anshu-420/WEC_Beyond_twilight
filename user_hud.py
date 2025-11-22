import pygame

# Default sizes if you want to reuse this HUD in other projects
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_GUI_HEIGHT = 100

# Default legend entries (you can override from main)
DEFAULT_LEGEND_ITEMS = [
    {"color": (255, 255, 255), "label": "Selected cell"},
    {"color": (0, 150, 255),   "label": "Water"},
    {"color": (0, 255, 100),   "label": "Safe zone"},
    {"color": (255, 100, 0),   "label": "Hazard"},
]

# Colors
GUI_BG     = (20, 20, 20)
WHITE      = (255, 255, 255)
RED        = (200, 50, 50)
YELLOW     = (230, 210, 50)
DARK_GREY  = (40, 40, 40)


class HUD:
    """
    HUD / GUI bar that sits below the playing area.

    Usage:
        hud = HUD(grid_height=800, window_width=800)
        hud.hull_health = 75
        hud.fuel = 40
        hud.depth_m = 120
        hud.draw(screen)
    """

    def __init__(
        self,
        grid_height: int,
        window_width: int = DEFAULT_WINDOW_WIDTH,
        gui_height: int = DEFAULT_GUI_HEIGHT,
        legend_items=None,
    ):
        self.grid_height = grid_height       # top of GUI (e.g. 800)
        self.window_width = window_width     # e.g. 800
        self.gui_height = gui_height         # e.g. 100

        # HUD values
        self.hull_health = 100   # 0–100
        self.fuel = 100          # 0–100
        self.depth_m = 0         # depth in meters (int or float)

        # Legend entries
        self.legend_items = legend_items if legend_items is not None else DEFAULT_LEGEND_ITEMS

        # Fonts (initialize once)
        self.font_small = pygame.font.SysFont(None, 20)
        self.font_medium = pygame.font.SysFont(None, 28)

    def draw(self, surface: pygame.Surface):
        """Draw the HUD onto the given surface."""

        gui_y = self.grid_height  # starting y of GUI region
        gui_height = self.gui_height

        # Background panel
        pygame.draw.rect(surface, GUI_BG, (0, gui_y, self.window_width, gui_height))

        # -------- Legend --------
        legend_x = 10
        legend_y = gui_y + 10
        box_size = 18
        spacing_y = 22

        for i, item in enumerate(self.legend_items):
            color = item["color"]
            label = item["label"]

            # Color box
            box_rect = pygame.Rect(legend_x, legend_y + i * spacing_y, box_size, box_size)
            pygame.draw.rect(surface, color, box_rect)
            pygame.draw.rect(surface, WHITE, box_rect, 1)

            # Text
            text_surf = self.font_small.render(label, True, WHITE)
            surface.blit(text_surf, (legend_x + box_size + 8, legend_y + i * spacing_y + 2))

        # -------- Bars (Hull / Fuel) --------
        bars_x = 350
        bars_y = gui_y + 10
        bar_width = 200
        bar_height = 18
        bar_spacing = 8

        # Clamp ratios between 0 and 1
        health_ratio = max(0.0, min(1.0, self.hull_health / 100.0))
        fuel_ratio = max(0.0, min(1.0, self.fuel / 100.0))

        # Hull Health Bar (red)
        pygame.draw.rect(surface, DARK_GREY,
                         (bars_x, bars_y, bar_width, bar_height))
        pygame.draw.rect(surface, RED,
                         (bars_x, bars_y, int(bar_width * health_ratio), bar_height))
        pygame.draw.rect(surface, WHITE,
                         (bars_x, bars_y, bar_width, bar_height), 1)
        health_text = self.font_small.render(f"Hull: {int(self.hull_health)}%", True, WHITE)
        surface.blit(health_text, (bars_x + bar_width + 10, bars_y))

        # Fuel Bar (yellow)
        fuel_y = bars_y + bar_height + bar_spacing
        pygame.draw.rect(surface, DARK_GREY,
                         (bars_x, fuel_y, bar_width, bar_height))
        pygame.draw.rect(surface, YELLOW,
                         (bars_x, fuel_y, int(bar_width * fuel_ratio), bar_height))
        pygame.draw.rect(surface, WHITE,
                         (bars_x, fuel_y, bar_width, bar_height), 1)
        fuel_text = self.font_small.render(f"Fuel: {int(self.fuel)}%", True, WHITE)
        surface.blit(fuel_text, (bars_x + bar_width + 10, fuel_y))

        # -------- Depth Text --------
        depth_text = self.font_medium.render(f"Depth: {self.depth_m} m", True, WHITE)
        surface.blit(depth_text, (bars_x, fuel_y + bar_height + 10))
