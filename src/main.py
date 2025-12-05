"""Entry point for AutoSwitchTheme application"""
from datetime import datetime
from time import sleep
import schedule
import threading

from utils.config import APPDATA_PATH, config
from utils.logger import Logger
from core.tray_app import TrayApp
from core.app_monitor import AppMonitor

# Setup logger
logger = Logger(APPDATA_PATH / config.get("log", "path", fallback="logs"), config.getboolean("log", "debug", fallback=False)).setup_logger("app")

# === Main thread === #
def main_thread(tray_app: TrayApp):
    """Main application logic running in separate thread"""
    logger.info("Starting main application thread")

    # Load config
    api_token = config.get("api", "token")
    insee = config.get("location", "insee", fallback="06088")

    # Initialize sun hours monitor
    theme_monitor = AppMonitor(api_token, insee)
    schedule.every().day.at("00:01").do(theme_monitor.update_sun_hours)

    # Connect monitors to tray app
    tray_app.theme_monitor = theme_monitor

    # Get sun hours at startup
    tray_app.theme_monitor.update_sun_hours()
    logger.debug(f"Sun hours data: {tray_app.theme_monitor.sun_hours}")

    # Update theme at startup
    datetime_now = datetime.now().time()
    datetime_sunrise =  datetime.strptime(tray_app.theme_monitor.sun_hours["sunrise"], "%H:%M").time()
    datetime_sunset = datetime.strptime(tray_app.theme_monitor.sun_hours["sunset"], "%H:%M").time()
    logger.debug(f"DateTime now: {datetime_now}, DateTime sunrise: {datetime_sunrise}, DateTime sunset: {datetime_sunset}")

    logger.debug(f"Test(datetime_sunrise <= datetime_now <= datetime_sunset): {datetime_sunrise <= datetime_now <= datetime_sunset}")
    if datetime_sunrise <= datetime_now <= datetime_sunset:
        logger.debug("Switching to light theme...")
        tray_app.theme_monitor.switch_to_light_theme()
    else:
        logger.debug("Switching to dark theme...")
        tray_app.theme_monitor.switch_to_dark_theme()

    # Run scheduler
    while tray_app.running:
        schedule.run_pending()
        sleep(1)

    logger.info("Main application thread stopped")

# === Main function === #
def main():
    """Main entry point - setup tray and start threads"""
    logger.info("AutoSwitchTheme starting...")

    # Create tray app
    logger.debug("Creating tray app...")
    tray_app = TrayApp()
    logger.debug("Tray app created.")
    logger.debug("Setting up tray app...")
    tray_app.setup_tray()
    logger.debug("Tray app setup.")

    # Start main logic in separate thread
    logger.debug("Starting main logic in separate thread...")
    main_thread_obj = threading.Thread(
        target=main_thread,
        args=(tray_app,),
        daemon=True
    )
    main_thread_obj.start()
    logger.debug("Main logic in separate thread started.")

    # Run tray icon (blocking - this keeps the app running)
    logger.debug("Running tray app...")
    tray_app.run_tray()
    logger.debug("Tray app running.")
    logger.info("Application minimized to system tray")

    logger.info("Application stopped")


# === Entry point === #
if __name__ == "__main__":
    raise SystemExit(main())
