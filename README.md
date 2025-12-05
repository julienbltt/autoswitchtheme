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

1. **Create the configuration file** (optional):

   The application will automatically detect your location on first run. However, you can manually create a `config.ini` file in `%APPDATA%\AutoSwitchTheme\`:

   ```ini
   [location]
   city = YourCity
   region = YourRegion
   timezone = Your/Timezone
   latitude = 43.7
   longitude = 7.25

   [log]
   path = logs
   debug = false
   ```

   > **Note**: Location will be auto-detected and saved on first run if you have an internet connection.

2. **Add the application icon**:

   Place an `app.ico` file in `%APPDATA%\AutoSwitchTheme\` (or the application will log an error)

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
   - Modifies Windows Registry keys:
     - `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize\AppsUseLightTheme`
     - `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize\SystemUsesLightTheme`
   - Changes take effect immediately across the system

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
└── src/
    ├── __init__.py             # Package initialization
    ├── main.py                 # Entry point
    ├── utils/                  # Utility modules
    │   ├── __init__.py
    │   ├── config.py           # Configuration loader
    │   └── logger.py           # Logging setup
    └── core/                   # Core components
        ├── __init__.py
        ├── app_monitor.py      # Theme & solar data manager
        └── tray_app.py         # System tray interface
```

### Key Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **AppMonitor** | `src/core/app_monitor.py` | Manages local solar calculations and theme switching via Windows Registry |
| **TrayApp** | `src/core/tray_app.py` | Provides system tray UI, manual controls, and log file access |
| **Logger** | `src/utils/logger.py` | Configures logging with timed rotation |
| **Config** | `src/utils/config.py` | Loads configuration and defines constants |
| **Builder** | `builder.ps1` | PowerShell script to generate Nuitka build commands automatically |

### Data Storage

All runtime data is stored in `%APPDATA%\AutoSwitchTheme\`:

| File/Directory | Purpose |
|----------------|---------|
| `config.ini` | User configuration (location coordinates, timezone, logging settings) - auto-generated on first run |
| `app.ico` | System tray icon |
| `logs/app.log` | Application logs with 30-day rotation |
| `sun_hours.json` | Cached sunrise/sunset times (recalculated daily) |

## Configuration Reference

### Configuration File (`config.ini`)

The configuration file is automatically created on first run. You can manually edit it if needed:

```ini
[location]
city = Nice                      # City name (auto-detected)
region = Provence-Alpes-Côte d'Azur  # Region name (auto-detected)
timezone = Europe/Paris          # Timezone (auto-detected)
latitude = 43.7                  # Latitude coordinate (auto-detected)
longitude = 7.25                 # Longitude coordinate (auto-detected)

[log]
path = logs                      # Log directory name (relative to APPDATA)
debug = false                    # Enable debug logging (true/false)
```

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
| **Location not detected** | Check internet connection, or manually add location to `config.ini` |
| **Theme not changing** | Restart Windows Explorer: `taskkill /F /IM explorer.exe && start explorer.exe` |
| **Application won't start** | Check logs at `%APPDATA%\AutoSwitchTheme\logs\app.log` (use "Show Status" menu item) |
| **Icon not showing** | Ensure `app.ico` exists in `%APPDATA%\AutoSwitchTheme\` |
| **Wrong sun times** | Verify location coordinates in `config.ini` or delete config to re-detect |

### Debug Mode

Enable detailed logging by editing `config.ini`:

```ini
[log]
debug = true
```

View logs at: `%APPDATA%\AutoSwitchTheme\logs\app.log`

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
