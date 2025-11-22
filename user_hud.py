#Team Name: Anything Works

import pygame

# Default sizes if you want to reuse this HUD in other projects
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_GUI_HEIGHT = 100

# Shared colors for each object type from layers.py
OBJECT_COLORS = {
    "life":      (255, 255, 255),  # Marine Life
    "poi":       (0, 150, 255),    # Point of Interest
    "corals":    (155, 155, 0),    # Coral Reef
    "hazards":   (255, 100, 0),    # Hazard
    "food_web":  (180, 0, 255),    # Food Web (pick any distinct color you like)
    "resources": (0, 200, 120),    # Resources (pick any distinct color you like)
}

OBJECT_LABELS = {
    "life":      "Marine Life",
    "poi":       "Point of Interest",
    "corals":    "Coral Reef",
    "hazards":   "Hazard",
    "food_web":  "Food Web",
    "resources": "Resources",
}

# Default legend entries (you can override from main)
DEFAULT_LEGEND_ITEMS = [
    {"color": OBJECT_COLORS["life"],      "label": OBJECT_LABELS["life"]},
    {"color": OBJECT_COLORS["poi"],       "label": OBJECT_LABELS["poi"]},
    {"color": OBJECT_COLORS["corals"],    "label": OBJECT_LABELS["corals"]},
    {"color": OBJECT_COLORS["hazards"],   "label": OBJECT_LABELS["hazards"]},
    {"color": OBJECT_COLORS["food_web"],  "label": OBJECT_LABELS["food_web"]},
    {"color": OBJECT_COLORS["resources"], "label": OBJECT_LABELS["resources"]},
]

GUI_BG    = (20, 20, 20)
WHITE     = (255, 255, 255)
RED       = (200, 50, 50)
YELLOW    = (230, 210, 50)
DARK_GREY = (40, 40, 40)

class HUD:
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
        bars_x = 500
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
