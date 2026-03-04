from configparser import ConfigParser

import pytest


class TestConfiguratorImport:
    """Tests sur le module config déjà chargé (import-time execution)."""

    def test_configurator_is_configparser_instance(self):
        from src.utils.config import configurator

        assert isinstance(configurator, ConfigParser)

    def test_has_location_section(self):
        from src.utils.config import configurator

        assert configurator.has_section("location")

    def test_has_logs_section(self):
        from src.utils.config import configurator

        # Le fichier peut avoir 'logs' (v2.0) ou être vide si créé par défaut
        assert configurator.has_section("logs") or configurator.has_section("log")

    def test_location_has_latitude_key(self):
        from src.utils.config import configurator

        assert configurator.has_option("location", "latitude")

    def test_location_has_longitude_key(self):
        from src.utils.config import configurator

        assert configurator.has_option("location", "longitude")

    def test_location_has_timezone_key(self):
        from src.utils.config import configurator

        assert configurator.has_option("location", "timezone")

    def test_location_has_city_key(self):
        from src.utils.config import configurator

        assert configurator.has_option("location", "city")

    def test_location_has_region_key(self):
        from src.utils.config import configurator

        assert configurator.has_option("location", "region")


class TestConfiguratorDefaultValues:
    """Tests sur la logique de création des valeurs par défaut."""

    def test_default_config_creates_logs_section(self, tmp_path):
        """Simule la création d'un nouveau fichier de config."""
        config_file = tmp_path / "settings.ini"

        cfg = ConfigParser()
        cfg.add_section("logs")
        cfg.set("logs", "debug", "false")
        cfg.add_section("location")
        cfg.set("location", "city", "")
        cfg.set("location", "region", "")
        cfg.set("location", "timezone", "")
        cfg.set("location", "latitude", "0.0")
        cfg.set("location", "longitude", "0.0")

        with open(config_file, "x") as f:
            cfg.write(f)

        loaded = ConfigParser()
        loaded.read(config_file)

        assert loaded.has_section("logs")
        assert loaded.has_section("location")

    def test_default_debug_is_false(self, tmp_path):
        config_file = tmp_path / "settings.ini"

        cfg = ConfigParser()
        cfg.add_section("logs")
        cfg.set("logs", "debug", "false")

        with open(config_file, "x") as f:
            cfg.write(f)

        loaded = ConfigParser()
        loaded.read(config_file)

        assert loaded.getboolean("logs", "debug") is False

    def test_default_coordinates_are_zero(self, tmp_path):
        config_file = tmp_path / "settings.ini"

        cfg = ConfigParser()
        cfg.add_section("location")
        cfg.set("location", "latitude", "0.0")
        cfg.set("location", "longitude", "0.0")

        with open(config_file, "x") as f:
            cfg.write(f)

        loaded = ConfigParser()
        loaded.read(config_file)

        assert loaded.getfloat("location", "latitude") == 0.0
        assert loaded.getfloat("location", "longitude") == 0.0
