import pystray
from PIL import Image

from ..utils.config import APPDATA_PATH
from ..utils.logger import Logger


logger = Logger.get_logger("app")


class TrayApp:
    def __init__(self):
        self.icon = None
        self.theme_monitor = None
        self.sun_hours_monitor = None
        self.running = True

    def load_icon(self):
        """Load a simple icon for the tray"""
        icon_path = APPDATA_PATH / "app.ico"
        if icon_path.exists():
            return Image.open(icon_path)
        else:
            logger.error("Icon not found")
            return None


    def on_show_status(self, icon, item):
        """Show current status"""
        if self.theme_monitor and self.sun_hours_monitor:
            current_theme = self.theme_monitor.theme
            sun_hours = self.sun_hours_monitor.sun_hours
            logger.info(f"Current theme: {current_theme}")
            logger.info(f"Sun hours: {sun_hours}")

    def on_force_light(self, icon, item):
        """Force light theme"""
        if self.theme_monitor:
            self.theme_monitor.switch_to_light_theme()
            logger.info("Forced light theme")

    def on_force_dark(self, icon, item):
        """Force dark theme"""
        if self.theme_monitor:
            self.theme_monitor.switch_to_dark_theme()
            logger.info("Forced dark theme")

    def on_quit(self, icon, item):
        """Quit the application"""
        self.running = False
        logger.info("Application quit from tray")
        icon.stop()

    def setup_tray(self):
        """Setup the system tray icon and menu"""
        # Load the icon
        icon_image = self.load_icon()

        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("Show Status", self.on_show_status),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Force Light Theme", self.on_force_light),
            pystray.MenuItem("Force Dark Theme", self.on_force_dark),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.on_quit)
        )

        # Create the icon
        self.icon = pystray.Icon(
            "AutoSwitchTheme",
            icon_image,
            "Auto Switch Theme",
            menu
        )

        return self.icon

    def run_tray(self):
        """Run the tray icon (blocking)"""
        self.icon.run()
