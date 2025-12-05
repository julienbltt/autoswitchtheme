from datetime import datetime
from json import dump as json_dump, load as json_load
# Natif Windows registeries manager.
from winreg import OpenKey
from winreg import SetValueEx
from winreg import HKEY_CURRENT_USER, KEY_SET_VALUE
from winreg import REG_DWORD

from requests import get
import schedule

from utils.config import APPDATA_PATH
from utils.logger import Logger


logger = Logger.get_logger("app")


class AppMonitor:
    def __init__(self, api_token: str, insee: str):
        self.api_token = api_token
        self.insee = insee
        self.sun_hours = {
            "timestamp": None,
            "sunrise": None,
            "sunset": None,
        }
        self.theme = None
        self.sunrise_job = None
        self.sunset_job = None

    def update_sun_hours(self):
        """Update sun hours"""
        if schedule.get_jobs("switch-task"):
            schedule.clear("switch-task")

        self.get_sun_hours()

        if self.sun_hours["sunrise"] and self.sun_hours["sunset"]:
            schedule.every().day.at(self.sun_hours["sunrise"]).do(self.switch_to_light_theme).tag("switch-task")
            schedule.every().day.at(self.sun_hours["sunset"]).do(self.switch_to_dark_theme).tag("switch-task")

    def get_sun_hours(self):

        # Check if sun hours are cached
        cache_path = APPDATA_PATH / "sun_hours.json"
        if cache_path.exists():
            with cache_path.open("r") as f:
                file_data = json_load(f)
                if file_data["timestamp"] == datetime.today().strftime("%Y-%m-%d"):
                    logger.info("Sun hours fetched from cache")
                    self.sun_hours["timestamp"] = file_data["timestamp"]
                    self.sun_hours["sunrise"] = file_data["sunrise"][:5]
                    self.sun_hours["sunset"] = file_data["sunset"][:5]

                    logger.info(f"Sun hours: {self.sun_hours}")
                    return self.sun_hours

        # Fetch sun hours from API
        url = f"https://api.meteo-concept.com/api/ephemeride/0?token={self.api_token}&insee={self.insee}"
        response = get(url)
        if response.status_code != 200:
            logger.error(f"Error fetching sun hours: {response.status_code}")
            return response.status_code

        ephemeride = response.json()

        logger.info("Sun hours fetched from API")

        # Update sun hours
        self.sun_hours["timestamp"] = datetime.today().strftime("%Y-%m-%d")
        self.sun_hours["sunrise"] = ephemeride["ephemeride"]["sunrise"][:5]
        self.sun_hours["sunset"] = ephemeride["ephemeride"]["sunset"][:5]

        # Save sun hours to cache
        with cache_path.open("w") as f:
            file_data = self.sun_hours
            json_dump(file_data, f)

        logger.info(f"Sun hours: {self.sun_hours}")
        return self.sun_hours

    def set_windows_theme(self, theme: str):
        """
        Change Windows theme in a simple and reliable way
        Args:
            theme: 'light' or 'dark'
        """
        key = OpenKey(
            HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            0,
            KEY_SET_VALUE
        )
        
        try:
            if theme.lower() == "light":
                # Enable light theme
                SetValueEx(key, "AppsUseLightTheme", 0, REG_DWORD, 1)
                SetValueEx(key, "SystemUsesLightTheme", 0, REG_DWORD, 1)
            elif theme.lower() == "dark":
                # Enable dark theme
                SetValueEx(key, "AppsUseLightTheme", 0, REG_DWORD, 0)
                SetValueEx(key, "SystemUsesLightTheme", 0, REG_DWORD, 0)
            else:
                raise ValueError("Theme must be 'light' or 'dark'")
            
        except Exception as e:
            logger.error(f"Error changing theme: {e}")

        else:
            logger.info(f"Theme changed to {theme}")
            
        finally:
            key.Close()

    def switch_to_light_theme(self):
        if self.theme != "light":
            self.set_windows_theme("light")
            self.theme = "light"
        else:
            logger.info("Theme already set to light")

    def switch_to_dark_theme(self):
        if self.theme != "dark":
            self.set_windows_theme("dark")
            self.theme = "dark"
        else:
            logger.info("Theme already set to dark")
