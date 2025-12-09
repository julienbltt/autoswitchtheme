# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoSwitchTheme is a Windows system tray application that automatically switches between light and dark themes based on sunrise/sunset times. It auto-detects user location via IP geolocation, calculates sunrise/sunset times locally using the Astral library, and modifies Windows registry settings using the native `winreg` library.

**Version:** 2.0
**Python:** 3.8+
**Platform:** Windows 10/11

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
- **Switch** (`switch.py`): Theme and solar data manager
  - Calculates sunrise/sunset times locally using Astral library with LocationInfo
  - Caches ephemeris data daily in `%PROGRAMDATA%\AutoSwitchTheme\ephemeris.json`
  - **CRITICAL:** Uses native `winreg` library (OpenKey, SetValueEx) for direct registry manipulation
  - Sets DWORD registry values: 0=dark, 1=light
  - Registry keys: `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize`
  - Schedules daily solar time recalculation at 00:01 and sunrise/sunset theme switches
  - Clears previous scheduled tasks before creating new ones (prevents duplicates)

- **TrayApp** (`tray.py`): System tray interface
  - Provides manual theme override controls
  - Displays current status (theme + sun hours) and opens log file automatically
  - **Smart file opening:** Uses Windows registry to detect default `.log` file handler, fallback to Notepad
  - Registry detection: `HKEY_CLASSES_ROOT\{extension}` → ProgID → `shell\open\command`
  - Controls application lifecycle (quit)

### 3. Utilities (`src/utils/`)
- **Logger** (`logger.py`): Centralized logging with TimedRotatingFileHandler (30-day rotation, 12 backups)
- **config** (`config.py`): Configuration management
  - Auto-creates `settings.ini` if missing with default sections
  - Loads from `%PROGRAMDATA%\AutoSwitchTheme\config\settings.ini`
- **path** (`path.py`): **NEW - Centralized path management**
  - `get_app_dir()`: Installation directory (where Python files are)
  - `get_assets_dir()`: Assets directory (installation/assets)
  - `get_data_dir()`: Program data (`%PROGRAMDATA%\AutoSwitchTheme`)
  - `get_user_data_dir()`: User data (`%APPDATA%\AutoSwitchTheme`)
  - `get_config_file()`: Returns config file path
  - `get_log_file()`: Returns log file path

### Threading Model
The application uses two threads:
1. **Main thread** (daemon): Runs `schedule` loop every 1 second to check for pending theme switches
2. **Tray thread** (main): Blocks on `pystray.Icon.run()` - keeps app alive until user quits

### Theme Switching Mechanism
**IMPORTANT:** Theme changes use native Python `winreg` library (NOT `os.system()`):

```python
from winreg import OpenKey, SetValueEx, HKEY_CURRENT_USER, KEY_SET_VALUE, REG_DWORD

key = OpenKey(
    HKEY_CURRENT_USER,
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
    0,
    KEY_SET_VALUE
)
SetValueEx(key, "AppsUseLightTheme", 0, REG_DWORD, 1)  # 1=light, 0=dark
SetValueEx(key, "SystemUsesLightTheme", 0, REG_DWORD, 1)
key.Close()
```

- **Registry keys:** `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize`
- **Values modified:** `AppsUseLightTheme` and `SystemUsesLightTheme` (DWORD: 0=dark, 1=light)
- **Method:** Direct registry manipulation via `winreg` (more reliable than shell commands)
- **Error handling:** Try-except-finally block with proper key cleanup

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

Configuration is stored in `%PROGRAMDATA%\AutoSwitchTheme\config\settings.ini`:
- `[location]` - Auto-generated on first run with internet connection:
  - `city` - City name (from ipinfo.io)
  - `region` - Region/state name
  - `timezone` - Timezone identifier (e.g., "Europe/Paris")
  - `latitude` - Latitude coordinate (float)
  - `longitude` - Longitude coordinate (float)
  - **Fallback:** If latitude/longitude are both 0.0, defaults to Paris coordinates
- `[logs]` - Debug mode setting (note: renamed from `[log]` in v2.0)
  - `debug` - Boolean (true/false)

The application requires:
- Icon file at `assets/icon.ico` (relative to installation directory)
- Internet connection (only for initial location detection)

**Path Structure (v2.0):**
- **Installation:** Application code and assets (`assets/icon.ico`)
- **Program Data:** `%PROGRAMDATA%\AutoSwitchTheme\` (config, logs, cache)
  - `config/settings.ini` - Configuration file
  - `logs/app.log` - Application logs
  - `ephemeris.json` - Cached sun hours

## Important Notes

### Code Structure
- **Package Structure**: This project uses a package-based structure. The application must be run as a module: `python -m src`
- **Import Style**: All modules within `src/` use relative imports (e.g., `from utils.config import configurator`)
- **Path Management**: Always use `Paths` class from `utils.path` for all file/directory paths
- **Module Organization**:
  - `src/main.py` - Entry point, orchestration
  - `src/core/` - Business logic (Switch, TrayApp)
  - `src/utils/` - Infrastructure (config, logger, paths)

### Registry & System Integration
- **Registry Modifications**: Uses native `winreg` library (NOT `os.system()`) - more reliable and secure
- **Registry Keys**: Always close registry keys in finally block to prevent resource leaks
- **Changes Effect**: Registry changes take effect immediately but may require Windows Explorer refresh for full UI update
- **File Opening**: Uses registry to detect default file handler (HKEY_CLASSES_ROOT) with Notepad fallback

### Data Management
- **Ephemeris Cache**: `ephemeris.json` expires daily (timestamp format: `%Y-%m-%d`)
- **Cache Location**: `%PROGRAMDATA%\AutoSwitchTheme\ephemeris.json` (renamed from `sun_hours.json`)
- **Logging**: All logs go to `%PROGRAMDATA%\AutoSwitchTheme\logs\app.log` (changed from `%APPDATA%`)
- **Config Auto-Creation**: Config file auto-created with default sections if missing
- **Section Name**: `[logs]` not `[log]` (renamed in v2.0)

### Scheduling & Connectivity
- **Scheduler**: The `schedule` library is used for time-based task execution (not cron or Windows Task Scheduler)
- **Schedule Clearing**: Always clear existing "switch-task" tags before creating new schedules
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
.\builder.ps1 -MainFile "src\main.py" -OutputName "AutoSwitchTheme.exe" -IconFile "assets\icon.ico" -DisableConsole -Execute
```

## Recent Changes & Bug Fixes (v2.0)

### Major Refactoring (#12, #11, #10)
- **File Architecture**: Reorganized from single `main.py` to modular structure with `src/core/` and `src/utils/`
- **Path Manager**: Created `utils/path.py` for centralized path management
- **Configuration Handler**: Improved with automatic creation and proper defaults
- **File Renaming**:
  - `main.py` → `src/main.py`
  - `app_monitor.py` → `src/core/switch.py`
  - `tray_app.py` → `src/core/tray.py`
  - `config.ini` → `settings.ini`
  - `sun_hours.json` → `ephemeris.json`

### Bug Fixes
- **#3 - Registry Access Method**: Replaced unreliable `os.system("reg add ...")` with native `winreg` library
  - **Why:** Shell commands can fail silently, have security issues, and are slower
  - **Fix:** Direct Windows API access through `winreg.OpenKey()` and `winreg.SetValueEx()`
  - **Impact:** More reliable theme switching, better error handling

- **#4 - Show Status Button**: Fixed system tray "Show Status" menu item
  - **Problem:** Button didn't open log file, only printed to console
  - **Fix:** Added automatic file opening after logging status
  - **Enhancement:** Smart detection of default `.log` file handler via registry, fallback to Notepad

- **#7 - Location & Ephemeris**: Implemented IP-based location detection and local solar calculations
  - **Location API**: Uses ipinfo.io for IP geolocation (city, region, timezone, coordinates)
  - **Solar Calculation**: Uses Astral library for local sunrise/sunset computation (no external API)
  - **Caching**: Saves location to config, saves ephemeris to daily cache file

- **#8 - Logging Enhancement**: Improved log messages for sun hours info
  - Added detailed logging of sunrise/sunset times after fetch
  - Better debug messages for troubleshooting

### Architecture Changes
- **Paths Migration**: Moved from `%APPDATA%` to `%PROGRAMDATA%` for better multi-user support
- **Assets Management**: Icon moved from user data to installation directory (`assets/icon.ico`)
- **Module Imports**: Updated to use relative imports within package structure
- **Threading Model**: Clarified daemon thread (scheduler) vs main thread (tray)

### Build System
- **Builder Script**: Created automated PowerShell script for Nuitka compilation
- **Dependency Detection**: Auto-reads `requirement.txt` and converts Pillow→PIL
- **Metadata Support**: Company name, product name, version embedding
- **Output Control**: Saves command to `build.bat` for reproducibility
