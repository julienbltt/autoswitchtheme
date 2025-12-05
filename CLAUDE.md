# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoSwitchTheme is a Windows system tray application that automatically switches between light and dark themes based on sunrise/sunset times. It auto-detects user location via IP geolocation, calculates sunrise/sunset times locally using the Astral library, and modifies Windows registry settings to change the theme.

## Development Commands

### Running the Application
```bash
python -m src
```

Or:
```bash
python -m src.main
```

### Installing Dependencies
```bash
pip install -r requirement.txt
```

### Building Executable

#### Automated Build (Recommended)
```powershell
.\builder.ps1 -MainFile "src\main.py" -OutputName "AutoSwitchTheme.exe" -IconFile "app.ico" -DisableConsole -Execute
```

#### Manual PyInstaller Build
```bash
pyinstaller -F -w --optimize=2 --icon app.ico -n AutoSwitchTheme src/main.py
```

#### Manual Nuitka Build
```bash
python -m nuitka --mingw64 --onefile --assume-yes-for-downloads --remove-output --enable-plugin=pylint-warnings --enable-plugin=anti-bloat --windows-console-mode=disable --include-package=requests --include-package=schedule --include-package=pystray --include-package=PIL --include-package=astral --output-filename=AutoSwitchTheme.exe src/main.py
```

## Architecture

The application follows a modular structure with three main layers:

### 1. Entry Point Flow
- Execute with `python src/main.py`
- `src/main.py` → Starts two concurrent processes:
  - Main thread: Scheduler loop for theme switching
  - Tray thread: System tray UI (blocking)

### 2. Core Components (`src/core/`)
- **AppMonitor**: Orchestrates theme switching logic
  - Calculates sunrise/sunset times locally using Astral library with LocationInfo
  - Caches ephemeris data daily in `%APPDATA%/AutoSwitchTheme/sun_hours.json`
  - Manages Windows registry modifications for theme changes
  - Schedules daily solar time recalculation at 00:01 and sunrise/sunset theme switches

- **TrayApp**: System tray interface
  - Provides manual theme override controls
  - Displays current status (theme + sun hours) and opens log file automatically
  - Uses Windows registry to determine default text editor for `.log` files
  - Controls application lifecycle (quit)

### 3. Utilities (`src/utils/`)
- **Logger**: Centralized logging with TimedRotatingFileHandler (30-day rotation)
- **config**: Loads configuration from `%APPDATA%/AutoSwitchTheme/config.ini`

### Threading Model
The application uses two threads:
1. **Main thread** (daemon): Runs `schedule` loop every 1 second to check for pending theme switches
2. **Tray thread** (main): Blocks on `pystray.Icon.run()` - keeps app alive until user quits

### Theme Switching Mechanism
Theme changes are applied via Windows Registry:
- Registry keys: `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize`
- Values modified: `AppsUseLightTheme` and `SystemUsesLightTheme` (DWORD: 0=dark, 1=light)
- Uses `os.system()` with `reg add` commands

### Startup Behavior
On startup, the application:
1. Checks internet connectivity using `http://www.msftconnecttest.com/connecttest.txt`
2. If connected, auto-detects location via ipinfo.io API (latitude, longitude, city, region, timezone)
3. Saves location data to `config.ini` (creates section if missing)
4. Loads LocationInfo from config (city, region, timezone, coordinates)
5. Calculates sunrise/sunset times locally using Astral
6. Checks current time against sun hours
7. Immediately switches to appropriate theme (light if between sunrise-sunset, dark otherwise)
8. Schedules daily tasks for theme switching

## Configuration

Configuration is stored in `%APPDATA%/AutoSwitchTheme/config.ini`:
- `[location]` - Auto-generated on first run with internet connection:
  - `city` - City name (from ipinfo.io)
  - `region` - Region/state name
  - `timezone` - Timezone identifier (e.g., "Europe/Paris")
  - `latitude` - Latitude coordinate (float)
  - `longitude` - Longitude coordinate (float)
- `[log]` - Logging path and debug mode

The application requires:
- Icon file at `%APPDATA%/AutoSwitchTheme/app.ico`
- Internet connection (only for initial location detection)

## Important Notes

- **Package Structure**: This project uses a package-based structure. The application must be run as a module: `python -m src`
- **Import Style**: All modules within `src/` use relative imports (e.g., `from .utils.config import APPDATA_PATH`)
- **Registry Modifications**: The app modifies Windows registry - changes take effect immediately but may require Windows Explorer refresh for full UI update
- **Ephemeris Cache**: Cache expires daily (compared by timestamp in `%Y-%m-%d` format)
- **Logging**: All logs go to `%APPDATA%/AutoSwitchTheme/logs/app.log`
- **Scheduler**: The `schedule` library is used for time-based task execution (not cron or Windows Task Scheduler)
- **Internet Connectivity**: Only required on first run for location detection. Subsequent runs work offline using cached location data
- **Location Detection**: Uses ipinfo.io free API for IP-based geolocation
- **Solar Calculations**: Uses Astral library with LocationInfo for local sunrise/sunset computation (no external API needed)

## Build Automation

The `builder.ps1` PowerShell script automates Nuitka compilation:
- **Auto-detects dependencies** from `requirement.txt`
- **Replaces Pillow with PIL** for Nuitka compatibility (line 49-54)
- **Generates optimized Nuitka command** with all necessary flags
- **Saves command** to `build.bat` for reproducibility
- **Optionally executes build** with `-Execute` flag
- **Supports metadata** (company name, product name, version, icon)
- **Console control** via `-DisableConsole` flag for GUI mode

Usage:
```powershell
.\builder.ps1 -MainFile "src\main.py" -OutputName "AutoSwitchTheme.exe" -IconFile "app.ico" -DisableConsole -Execute
```
