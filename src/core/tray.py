from subprocess import run
from winreg import OpenKey, QueryValue
from winreg import HKEY_CLASSES_ROOT
from os.path import splitext

import pystray
from PIL import Image

from utils.logger import Logger
from utils.path import Paths



logger = Logger.get_logger("app")


class TrayApp:
    def __init__(self):
        self.icon = None
        self.theme_monitor = None
        self.running = True

    def load_icon(self):
        """Load a simple icon for the tray"""
        icon_path = Paths.get_assets_dir() / "icon.ico"
        if icon_path.exists():
            return Image.open(icon_path)
        else:
            logger.error(f"Icon not found (Path:{icon_path})")
            return None


    def on_show_status(self, icon, item):
        """Show current status"""
        if self.theme_monitor:
            logger.info(f"Current theme: {self.theme_monitor.theme}")
            logger.info(f"Sun hours: {self.theme_monitor.sun_hours}")

            # Open the file with the default application for the specific extension.
            filepath = Paths.get_log_file()
            _, extension = splitext(filepath)
            try:
                if not extension:
                    raise ValueError("No extension")
                # Look for the association for this extension in the registry
                with OpenKey(HKEY_CLASSES_ROOT, extension) as key:
                    progid = QueryValue(key, None)
                # Get the open command
                with OpenKey(HKEY_CLASSES_ROOT, rf'{progid}\shell\open\command') as key:
                    command = QueryValue(key, None)
                # Replace %1 with the file path
                command = command.replace('%1', f'"{filepath}"').replace('"%1"', f'"{filepath}"')
                # Execute the command
                run(command, shell=True)
            except Exception:
                # No extension or no association found, use Notepad
                run(['notepad.exe', filepath])

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
        logger.debug("Tray app running.")
        logger.info("Application minimized to system tray")
        self.icon.run()
