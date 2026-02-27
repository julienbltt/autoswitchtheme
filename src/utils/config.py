from configparser import ConfigParser

from src.utils.path import Paths


# Load config
configurator = ConfigParser()
if Paths.get_config_file().exists():
    configurator.read(Paths.get_config_file())
else:
    configurator.add_section("logs")
    configurator.set("logs", "debug", "false")

    configurator.add_section("location")
    configurator.set("location", "city", "")
    configurator.set("location", "region", "")
    configurator.set("location", "timezone", "")
    configurator.set("location", "latitude", "0.0")
    configurator.set("location", "longitude", "0.0")

    with open(Paths.get_config_file(), "x") as configfile:
        configurator.write(configfile)
