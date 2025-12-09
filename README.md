# AutoSwitchTheme

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)](https://www.microsoft.com/windows)

> Automatically switch between light and dark Windows themes based on sunrise and sunset times.

AutoSwitchTheme is a lightweight system tray application that synchronizes your Windows theme with natural daylight hours. Using real-time solar data from the Meteo-Concept API, it seamlessly transitions between light mode during the day and dark mode at night.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [System Tray Menu](#system-tray-menu)
  - [Building an Executable](#building-an-executable)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Configuration Reference](#configuration-reference)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

- **Automatic Theme Switching** - Seamlessly toggles between light and dark themes based on sunrise/sunset times
- **Automatic Location Detection** - Detects your location automatically via IP geolocation (ipinfo.io)
- **Local Solar Calculations** - Computes sunrise/sunset times locally using the Astral library
- **Internet Connectivity Check** - Validates internet connection before making external API calls
- **System Tray Integration** - Minimal interface that runs quietly in the background
- **Manual Override** - Force light or dark theme at any time via the tray menu
- **Enhanced Status Display** - View current status and automatically open log file with one click
- **Smart Caching** - Stores location data in configuration file to minimize API calls
- **Comprehensive Logging** - Built-in logging with automatic rotation (30-day retention)

## What's New in v2.0

### Architecture Improvements
- **Modular Refactoring** - Reorganized codebase into `src/core/` and `src/utils/` for better maintainability
- **Path Manager** - New centralized path management system ([src/utils/path.py](src/utils/path.py)) separating assets, data, and configuration
- **Improved Data Organization** - Moved from `%APPDATA%` to `%PROGRAMDATA%` for better multi-user support
- **Package Structure** - Proper Python package with relative imports and `__init__.py` files

### Bug Fixes & Enhancements
- **Fixed Registry Access** ([#3](../../issues/3)) - Replaced unreliable `os.system()` calls with native `winreg` library for direct registry manipulation
- **Fixed Show Status** ([#4](../../issues/4)) - System tray "Show Status" button now properly displays info and opens log file automatically
- **Smart File Opening** - Log files now open with system default editor (detected via registry) with Notepad fallback
- **Enhanced Configuration** - Auto-creation of configuration file with proper defaults if missing
- **Better Error Handling** - Improved logging and error messages throughout the application

### Build & Deployment
- **Builder Script v2.0** - Enhanced PowerShell script for automated Nuitka compilation with dependency auto-detection
- **Better Assets Management** - Icon moved to `assets/` folder for cleaner project structure
- **Renamed Cache File** - `sun_hours.json` → `ephemeris.json` for more accurate terminology

## Getting Started

### Prerequisites

- **Operating System**: Windows 10 or Windows 11
- **Python**: Version 3.8 or higher
- **Internet Connection**: Required for initial location detection (optional after first run)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/autoswitchtheme.git
   cd autoswitchtheme
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirement.txt
   ```

### Configuration

The application automatically configures itself on first run:

1. **Automatic Configuration** (recommended):

   On first run with an internet connection, the application will:
   - Auto-detect your location via IP geolocation (ipinfo.io)
   - Create `settings.ini` in `%PROGRAMDATA%\AutoSwitchTheme\config\`
   - Save location data (city, region, timezone, coordinates)
   - Calculate local sunrise/sunset times
   - Apply the appropriate theme immediately

2. **Manual Configuration** (optional):

   If you prefer to configure manually or don't have internet access, create `%PROGRAMDATA%\AutoSwitchTheme\config\settings.ini`:

   ```ini
   [location]
   city = YourCity
   region = YourRegion
   timezone = Your/Timezone
   latitude = 43.7
   longitude = 7.25

   [logs]
   debug = false
   ```

   > **Note**: If `latitude` and `longitude` are both `0.0`, the application defaults to Paris coordinates as a fallback.

## Usage

### Running the Application

Start the application in development mode:

```bash
python -m src/main.py
```

The application will:
1. Check internet connectivity
2. Automatically detect your location (if connected to internet)
3. Calculate sunrise/sunset times for your location
4. Apply the appropriate theme based on current time
5. Minimize to the system tray

### System Tray Menu

Right-click the system tray icon to access:

| Menu Item | Description |
|-----------|-------------|
| **Show Status** | Display current theme and solar hours in logs, then open log file automatically |
| **Force Light Theme** | Manually switch to light theme |
| **Force Dark Theme** | Manually switch to dark theme |
| **Quit** | Exit the application |

### Building an Executable

#### Automated Nuitka Build (Recommended)

Use the PowerShell builder script for automatic command generation:

```powershell
.\builder.ps1 -MainFile "src\main.py" -OutputName "AutoSwitchTheme.exe" -IconFile "app.ico" -CompanyName "YourCompany" -ProductName "AutoSwitchTheme" -Version "1.0.0.0" -DisableConsole -Execute
```

**Parameters:**
- `-MainFile`: Main Python file (required)
- `-OutputName`: Output executable name
- `-IconFile`: Icon file path
- `-CompanyName`: Company name for metadata
- `-ProductName`: Product name for metadata
- `-Version`: Version number
- `-DisableConsole`: Hide console window (GUI mode)
- `-Execute`: Automatically execute the build after generating the command
- `-Standalone`: Use standalone mode instead of onefile

The script will:
1. Auto-detect dependencies from `requirement.txt`
2. Generate optimized Nuitka command
3. Save command to `build.bat`
4. Execute compilation (if `-Execute` flag is used)

#### Manual PyInstaller Build

Create a standalone executable with PyInstaller:

```bash
pyinstaller -F -w --optimize=2 --icon app.ico -n AutoSwitchTheme src/main.py
```

The executable will be created in the `dist/` directory.

#### Manual Nuitka Build

```bash
python -m nuitka --mingw64 --standalone --lto=yes --prefer-source-code --assume-yes-for-downloads --remove-output --enable-plugin=pylint-warnings --enable-plugin=anti-bloat --windows-console-mode=disable --include-package=requests 
--include-package=schedule --include-package=pystray --include-package=PIL --include-package=astral --include-data-dir=assets --output-filename=autoswitchtheme.exe src/main.py
```

## How It Works

AutoSwitchTheme uses a multi-threaded architecture to manage theme switching:

1. **Startup Phase**:
   - Checks internet connectivity using Microsoft's connectivity test endpoint
   - Auto-detects location via IP geolocation (ipinfo.io API)
   - Saves location data to `%APPDATA%\AutoSwitchTheme\config.ini`
   - Calculates sunrise/sunset times locally using Astral library with detected coordinates
   - Immediately applies appropriate theme based on current time

2. **Scheduling Phase**:
   - Schedules daily solar time recalculation at 00:01 AM
   - Schedules theme switches at sunrise (→ light) and sunset (→ dark)
   - Runs scheduler loop in daemon thread (checks every second)

3. **Theme Switching**:
   - Modifies Windows Registry using native `winreg` library (Python standard library):
     - `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize\AppsUseLightTheme`
     - `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize\SystemUsesLightTheme`
   - Sets DWORD values: `0` for dark theme, `1` for light theme
   - Changes take effect immediately across the system
   - More reliable than command-line `reg add` approach

4. **System Tray**:
   - Runs on main thread (blocking)
   - Provides manual override controls
   - Displays status and opens log file automatically

## Project Structure

```
autoswitchtheme/
├── requirement.txt             # Python dependencies
├── builder.ps1                 # PowerShell build automation script
├── README.md                   # Project documentation
├── CLAUDE.md                   # Claude Code guidance
├── assets/                     # Application assets
│   └── icon.ico                # System tray icon
└── src/
    ├── __init__.py             # Package initialization
    ├── main.py                 # Entry point
    ├── utils/                  # Utility modules
    │   ├── __init__.py
    │   ├── config.py           # Configuration loader
    │   ├── logger.py           # Logging setup with rotation
    │   └── path.py             # Path management (NEW)
    └── core/                   # Core components
        ├── __init__.py
        ├── switch.py           # Theme & solar data manager
        └── tray.py             # System tray interface
```

### Key Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **Switch** | [src/core/switch.py](src/core/switch.py) | Manages local solar calculations and theme switching via Windows Registry using `winreg` |
| **TrayApp** | [src/core/tray.py](src/core/tray.py) | Provides system tray UI, manual controls, and automatic log file opening |
| **Logger** | [src/utils/logger.py](src/utils/logger.py) | Configures logging with timed rotation (30-day retention) |
| **Config** | [src/utils/config.py](src/utils/config.py) | Loads/creates configuration with automatic initialization |
| **Paths** | [src/utils/path.py](src/utils/path.py) | Centralized path management for data, assets, config, and logs |
| **Builder** | [builder.ps1](builder.ps1) | PowerShell script to generate Nuitka build commands automatically |

### Data Storage

Application data is now organized across multiple locations for better system integration:

**Program Installation Directory:**
| File/Directory | Purpose |
|----------------|---------|
| `assets/icon.ico` | System tray icon (bundled with application) |

**Program Data (`%PROGRAMDATA%\AutoSwitchTheme\`):**
| File/Directory | Purpose |
|----------------|---------|
| `config/settings.ini` | User configuration (location coordinates, timezone, logging settings) - auto-generated on first run |
| `logs/app.log` | Application logs with 30-day rotation (12 backup files) |
| `ephemeris.json` | Cached sunrise/sunset times (recalculated daily at 00:01) |

> **Note:** The path structure was improved in v2.0 to separate read-only assets from runtime data, enabling better multi-user support and following Windows best practices.

## Configuration Reference

### Configuration File (`settings.ini`)

Located at `%PROGRAMDATA%\AutoSwitchTheme\config\settings.ini`, the configuration file is automatically created on first run. You can manually edit it if needed:

```ini
[location]
city = Nice                      # City name (auto-detected via ipinfo.io)
region = Provence-Alpes-Côte d'Azur  # Region name (auto-detected)
timezone = Europe/Paris          # Timezone (auto-detected)
latitude = 43.7                  # Latitude coordinate (auto-detected)
longitude = 7.25                 # Longitude coordinate (auto-detected)

[logs]
debug = false                    # Enable debug logging (true/false)
```

> **Changes in v2.0:** File renamed from `config.ini` to `settings.ini` and moved to `%PROGRAMDATA%\AutoSwitchTheme\config\` directory. The `[log]` section was renamed to `[logs]` for consistency.

### Update Frequencies

| Component | Frequency | Details |
|-----------|-----------|---------|
| Location detection | Once on first run (or when config missing) | Fetches location via IP geolocation API |
| Solar calculation | Daily at 00:01 | Recalculates sunrise/sunset times locally |
| Theme check | Every 1 second | Scheduler loop checks for pending tasks |
| Log rotation | Every 30 days | Keeps 12 backup files (1 year retention) |

### Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | HTTP API calls for location detection |
| `schedule` | Task scheduling for theme switches |
| `pystray` | System tray icon and menu |
| `Pillow` | Icon image handling |
| `astral` | Astronomical calculations for sunrise/sunset times |

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Location not detected** | Check internet connection, or manually add location to `settings.ini` in `%PROGRAMDATA%\AutoSwitchTheme\config\` |
| **Theme not changing** | Restart Windows Explorer: `taskkill /F /IM explorer.exe && start explorer.exe` or check if registry keys are writable |
| **Application won't start** | Check logs at `%PROGRAMDATA%\AutoSwitchTheme\logs\app.log` (use "Show Status" menu item or open directly) |
| **Icon not showing** | Ensure `icon.ico` exists in `assets/` folder within installation directory |
| **Wrong sun times** | Verify location coordinates in `settings.ini` or delete config to trigger re-detection on next run |
| **Permission errors** | Run as administrator or check write permissions for `%PROGRAMDATA%\AutoSwitchTheme\` |

### Debug Mode

Enable detailed logging by editing `%PROGRAMDATA%\AutoSwitchTheme\config\settings.ini`:

```ini
[logs]
debug = true
```

View logs at: `%PROGRAMDATA%\AutoSwitchTheme\logs\app.log`

Or use the **Show Status** tray menu item to automatically open the log file.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Important Notes

- **Registry Modifications**: This application modifies Windows registry settings to change themes. While designed to be safe, it's recommended to back up your registry before intensive use.
- **Internet Connection**: Required only for initial location detection. Once configured, the app works offline using local solar calculations.
- **Location Privacy**: Your location is detected via IP geolocation and stored locally in the config file. No data is sent to external servers after initial detection.
- **Windows Compatibility**: Tested on Windows 10 and Windows 11. May not work on older versions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes (if available).

---

<div align="center">

**Made with Python**

If you find this project helpful, please consider starring the repository!

</div>
