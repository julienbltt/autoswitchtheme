import sys
from os import name as os_name, environ
from pathlib import Path


class Paths:
    """Gestion des chemins de l'application"""
    
    @staticmethod
    def get_app_dir():
        """Répertoire d'installation (Program Files)"""
        return Path(__file__).parent.parent
    
    @staticmethod
    def get_assets_dir():
        """Répertoire des assets (dans Program Files)"""
        return Paths.get_app_dir() / "assets"
    
    @staticmethod
    def get_data_dir():
        """Répertoire des données (ProgramData)"""
        if os_name == 'nt':
            base = Path(environ.get('PROGRAMDATA', 'C:/ProgramData'))
        else:
            base = Path('/var/lib')
        
        data_dir = base / "AutoSwitchTheme"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    @staticmethod
    def get_user_data_dir():
        """Répertoire des données utilisateur (AppData)"""
        if os_name == 'nt':
            base = Path(environ.get('APPDATA'))
        else:
            base = Path.home() / ".config"
        
        user_dir = base / "AutoSwitchTheme"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    @staticmethod
    def get_config_file():
        """Fichier de configuration partagé"""
        base = Paths.get_data_dir() / "config"
        base.mkdir(parents=True, exist_ok=True)
        return  base / "settings.ini"
    
    @staticmethod
    def get_log_file():
        """Fichier de log"""
        log_dir = Paths.get_data_dir() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / "app.log"

# Utilisation
if __name__ == "__main__":
    paths = Paths()
    
    # Lire une image (asset statique)
    logo = paths.get_assets_dir() / "images" / "logo.png"
    
    # Écrire dans un fichier de config
    config_file = paths.get_config_file()
    
    # Écrire des logs
    log_file = paths.get_log_file()
    
    print(f"Assets: {paths.get_assets_dir()}")
    print(f"Data: {paths.get_data_dir()}")
    print(f"User Data: {paths.get_user_data_dir()}")