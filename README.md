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
- **Location-Based Solar Data** - Fetches accurate sunrise/sunset times using the Meteo-Concept API
- **System Tray Integration** - Minimal interface that runs quietly in the background
- **Manual Override** - Force light or dark theme at any time via the tray menu
- **Smart Caching** - Reduces API calls by caching solar data for 24 hours
- **Comprehensive Logging** - Built-in logging with automatic rotation (30-day retention)

## Getting Started

### Prerequisites

- **Operating System**: Windows 10 or Windows 11
- **Python**: Version 3.8 or higher
- **API Key**: Free Meteo-Concept API key ([Get one here](https://api.meteo-concept.com/))

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/autoswitchtheme.git
   cd autoswitchtheme
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requierement.txt
   ```

### Configuration

1. **Obtain a Meteo-Concept API key**:
   - Visit [https://api.meteo-concept.com/](https://api.meteo-concept.com/)
   - Create a free account
   - Copy your API token

2. **Create the configuration file**:

   Navigate to `%APPDATA%\AutoSwitchTheme\` and create a `config.ini` file:

   ```ini
   [api]
   token = YOUR_API_TOKEN_HERE

   [location]
   insee = 06033  # INSEE code for your city (e.g., 06033 for Nice, France)

   [log]
   path = logs
   debug = false
   ```

   > **Finding your INSEE code**: Use this [INSEE code lookup tool](https://www.insee.fr/fr/information/2560452)

3. **Add the application icon**:

   Place an `app.ico` file in `%APPDATA%\AutoSwitchTheme\` (or the application will log an error)

## Usage

### Running the Application

Start the application in development mode:

```bash
python main.py
```

The application will:
1. Load configuration from `%APPDATA%\AutoSwitchTheme\config.ini`
2. Fetch sunrise/sunset times for your location
3. Apply the appropriate theme based on current time
4. Minimize to the system tray

### System Tray Menu

Right-click the system tray icon to access:

| Menu Item | Description |
|-----------|-------------|
| **Show Status** | Display current theme and solar hours in logs |
| **Force Light Theme** | Manually switch to light theme |
| **Force Dark Theme** | Manually switch to dark theme |
| **Quit** | Exit the application |

### Building an Executable

Create a standalone executable with PyInstaller:

```bash
pyinstaller -F -w --optimize=2 --icon app.ico -n AutoSwitchTheme main.py
```

The executable will be created in the `dist/` directory.

## How It Works

AutoSwitchTheme uses a multi-threaded architecture to manage theme switching:

1. **Startup Phase**:
   - Loads configuration from `%APPDATA%\AutoSwitchTheme\config.ini`
   - Fetches sunrise/sunset times from Meteo-Concept API
   - Caches solar data locally to minimize API calls
   - Immediately applies appropriate theme based on current time

2. **Scheduling Phase**:
   - Schedules daily API refresh at 00:01 AM
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
   - Displays status on demand

## Project Structure

```
autoswitchtheme/
├── main.py                     # Entry point
├── requierement.txt            # Python dependencies
├── README.md                   # Project documentation
├── CLAUDE.md                   # Claude Code guidance
└── src/
    ├── main.py                 # Application logic
    ├── utils/                  # Utility modules
    │   ├── config.py           # Configuration loader
    │   └── logger.py           # Logging setup
    └── core/                   # Core components
        ├── app_monitor.py      # Theme & solar data manager
        └── tray_app.py         # System tray interface
```

### Key Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **AppMonitor** | `src/core/app_monitor.py` | Manages solar data fetching, caching, and theme switching via Windows Registry |
| **TrayApp** | `src/core/tray_app.py` | Provides system tray UI and manual controls |
| **Logger** | `src/utils/logger.py` | Configures logging with timed rotation |
| **Config** | `src/utils/config.py` | Loads configuration and defines constants |

### Data Storage

All runtime data is stored in `%APPDATA%\AutoSwitchTheme\`:

| File/Directory | Purpose |
|----------------|---------|
| `config.ini` | User configuration (API key, location, logging settings) |
| `app.ico` | System tray icon |
| `logs/` | Application logs with 30-day rotation |
| `sun_hours.json` | Cached sunrise/sunset times (refreshed daily) |

## Configuration Reference

### Configuration File (`config.ini`)

```ini
[api]
token = YOUR_TOKEN_HERE          # Meteo-Concept API token (required)

[location]
insee = 06033                    # INSEE code for your city (default: Nice)

[log]
path = logs                      # Log directory name (relative to APPDATA)
debug = false                    # Enable debug logging (true/false)
```

### Update Frequencies

| Component | Frequency | Details |
|-----------|-----------|---------|
| Solar data | Daily at 00:01 | Fetches fresh sunrise/sunset times from API |
| Theme check | Every 1 second | Scheduler loop checks for pending tasks |
| Log rotation | Every 30 days | Keeps 12 backup files (1 year retention) |

### Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | HTTP API calls to Meteo-Concept |
| `schedule` | Task scheduling for theme switches |
| `pystray` | System tray icon and menu |
| `Pillow` | Icon image handling |
| `astral` | Optional astronomical calculations |

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **API Error** | Verify API token and INSEE code in `config.ini` |
| **Theme not changing** | Restart Windows Explorer: `taskkill /F /IM explorer.exe && start explorer.exe` |
| **Application won't start** | Check logs at `%APPDATA%\AutoSwitchTheme\logs\app.log` |
| **Icon not showing** | Ensure `app.ico` exists in `%APPDATA%\AutoSwitchTheme\` |
| **Wrong theme at startup** | Verify your INSEE code matches your actual location |

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
- **API Usage**: The free tier of Meteo-Concept API has rate limits. This application caches data daily to stay within limits.
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
