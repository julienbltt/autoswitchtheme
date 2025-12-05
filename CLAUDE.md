# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoSwitchTheme is a Windows system tray application that automatically switches between light and dark themes based on sunrise/sunset times. It fetches ephemeris data from the Meteo-Concept API and modifies Windows registry settings to change the theme.

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
pip install -r requierement.txt
```

### Building Executable
```bash
pyinstaller -F -w --optimize=2 --icon app.ico -n AutoSwitchTheme src/main.py
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
  - Fetches sunrise/sunset times from Meteo-Concept API
  - Caches ephemeris data daily in `%APPDATA%/AutoSwitchTheme/sun_hours.json`
  - Manages Windows registry modifications for theme changes
  - Schedules daily updates at 00:01 and sunrise/sunset theme switches

- **TrayApp**: System tray interface
  - Provides manual theme override controls
  - Displays current status (theme + sun hours)
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
1. Loads configuration from `config.ini`
2. Fetches/caches sunrise/sunset times
3. Checks current time against sun hours
4. Immediately switches to appropriate theme (light if between sunrise-sunset, dark otherwise)
5. Schedules daily tasks for theme switching

## Configuration

Configuration is stored in `%APPDATA%/AutoSwitchTheme/config.ini`:
- `[api]` - Meteo-Concept API token (required)
- `[location]` - INSEE code for French city (default: 06088)
- `[log]` - Logging path and debug mode

The application requires:
- Icon file at `%APPDATA%/AutoSwitchTheme/app.ico`
- Meteo-Concept API token (free tier available)

## Important Notes

- **Package Structure**: This project uses a package-based structure. The application must be run as a module: `python -m src`
- **Import Style**: All modules within `src/` use relative imports (e.g., `from .utils.config import APPDATA_PATH`)
- **Registry Modifications**: The app modifies Windows registry - changes take effect immediately but may require Windows Explorer refresh for full UI update
- **Ephemeris Cache**: Cache expires daily (compared by timestamp in `%Y-%m-%d` format)
- **Logging**: All logs go to `%APPDATA%/AutoSwitchTheme/logs/app.log`
- **Scheduler**: The `schedule` library is used for time-based task execution (not cron or Windows Task Scheduler)
