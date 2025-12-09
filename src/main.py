"""Entry point for AutoSwitchTheme application"""
from datetime import datetime
from time import sleep
import threading

from requests import get, RequestException
import schedule
from astral import LocationInfo

from utils.config import configurator
from utils.logger import Logger
from utils.path import Paths
from core.tray import TrayApp
from core.switch import Switch


# Setup logger
logger = Logger(Paths.get_log_file(), configurator.getboolean("log", "debug", fallback=False)).setup_logger("app")


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

            #Save location in configuration file
            configurator.set("location", "city", data['city'])
            configurator.set("location", "region", data['region'])
            configurator.set("location", "timezone", data['timezone'])
            configurator.set("location", "latitude", latitude)
            configurator.set("location", "longitude", longitude)
            
            with open(Paths.get_config_file(), 'w') as configfile:
                configurator.write(configfile)

            logger.debug("Location saved into the configuration file.")

    latitude = configurator.getfloat("location", "latitude")
    longitude = configurator.getfloat("location", "longitude")
    if latitude == 0.0 and longitude == 0.0:
        #TODO: Use fixed hours, not a fixed city
        city = LocationInfo(
            name="Paris",
            region="France",
            timezone="Europe/Paris",
            latitude=48.8333,
            longitude=2.33333
        )

    else:
        city = LocationInfo(
            name=configurator.get("location", "city"),
            region=configurator.get("location", "region"),
            timezone=configurator.get("location", "timezone"),
            latitude=latitude,
            longitude=longitude
        )
    
    logger.debug("Location loaded.")

    # Initialize sun hours monitor
    theme_monitor = Switch(city)
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
