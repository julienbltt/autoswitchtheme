from configparser import ConfigParser
from pathlib import Path
from os import getenv

# === Constants === #
APPDATA_PATH = Path(getenv("APPDATA")) / "AutoSwitchTheme"
APPDATA_PATH.mkdir(parents=True, exist_ok=True)

# Load config
config = ConfigParser()
config.read(APPDATA_PATH / "config.ini")
