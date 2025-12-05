"""Entry point for AutoSwitchTheme application"""
from datetime import datetime
from time import sleep
import threading

from requests import get, RequestException
import schedule
from astral import LocationInfo

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

    # Check internet connexion
    is_connected = None
    try:
        get("http://www.msftconnecttest.com/connecttest.txt", timeout=3)
    except:
        is_connected = False
        logger.warning("Internet connection unavailable")
    else:
        is_connected = True
        logger.info("Connected to the internet")
        

    # Get localisation from IP API
    if is_connected:
        try:
            response = get('https://ipinfo.io/json', timeout=3)
        except RequestException as e:
            logger.error(f"Error fetching location: {response.status_code}")
        else:
            data = response.json()
            latitude, longitude = (e for e in data['loc'].split(','))

            logger.debug("Location fetch from API.")

            #Save location in config file
            if not config.has_section("location"):
                config.add_section("location")
            
            config.set("location", "city", data['city'])
            config.set("location", "region", data['region'])
            config.set("location", "timezone", data['timezone'])
            config.set("location", "latitude", latitude)
            config.set("location", "longitude", longitude)
            
            with open(APPDATA_PATH / "config.ini", 'w') as configfile:
                config.write(configfile)

            logger.debug("Location saved into the configuration file.")

    # Load localisation:
    city = LocationInfo(
        name=config.get("location", "city"),
        region=config.get("location", "region"),
        timezone=config.get("location", "timezone"),
        latitude=config.getfloat("location", "latitude"),
        longitude=config.getfloat("location", "longitude")
    )
    logger.debug("Location loaded.")

    # Initialize sun hours monitor
    theme_monitor = AppMonitor(city)
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
    logger.info("Application stopped")


# === Entry point === #
if __name__ == "__main__":
    raise SystemExit(main())
