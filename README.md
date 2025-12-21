# DUCO Ventilation & Sun Control

[![CI/CD Pipeline](https://github.com/stuartp44/haduco/actions/workflows/release.yml/badge.svg)](https://github.com/stuartp44/haduco/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/stuartp44/haduco/branch/main/graph/badge.svg)](https://codecov.io/gh/stuartp44/haduco)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/stuartp44/haduco.svg)](https://github.com/stuartp44/haduco/releases)
[![License](https://img.shields.io/github/license/stuartp44/haduco.svg)](LICENSE)

Home Assistant Custom Component for DUCO Ventilation & Sun Control systems.

This integration allows you to monitor and control your DUCO ventilation and sun protection devices directly from Home Assistant through local network communication.

## Features

- **Local Control**: Direct communication with DUCO devices on your local network
- **Auto-Discovery**: Automatic discovery via Zeroconf
- **Sensor Platform**: Monitor ventilation status, air quality, and system parameters
- **Select Platform**: Control ventilation modes and sun protection settings
- **Configuration Flow**: Easy setup through the Home Assistant UI
- **Real-time Updates**: Automatic polling for device state changes

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/stuartp44/haduco`
6. Select category: "Integration"
7. Click "Add"
8. Find "DUCO Ventilation & Sun Control" in the integration list
9. Click "Download"
10. Restart Home Assistant

### Manual Installation

1. Download the latest release from [Releases](https://github.com/stuartp44/haduco/releases)
2. Extract the files
3. Copy the `custom_components/duco_ventilation_sun_control` directory to your Home Assistant `custom_components` directory
4. Restart Home Assistant

## Configuration

### Via UI (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "DUCO Ventilation & Sun Control"
4. Follow the configuration steps
5. Enter your DUCO device IP address and port (default: 80)

### Auto-Discovery

If your DUCO device supports Zeroconf, it will be automatically discovered. Simply click **Configure** when the integration appears in your notifications.

## Entities

After configuration, the integration will create entities for:

### Sensors
- System status
- Air quality metrics
- Temperature readings
- Fan speeds
- Operating modes

### Selects
- Ventilation modes (Auto, Manual, Sleep, etc.)
- Fan speed control
- Sun protection positions

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for setup instructions.

### Quick Start

```bash
# Clone the repository
git clone https://github.com/stuartp44/haduco.git
cd haduco

# Install dependencies
pip install -r requirements_test.txt

# Run tests
pytest tests/

# Run linting
ruff check .
ruff format .
mypy custom_components/duco_ventilation_sun_control
```

## Documentation

- [Release Pipeline](docs/RELEASE_PIPELINE.md) - Automated release process
- [Development Guide](docs/DEVELOPMENT.md) - Development setup and workflow
- [Commit Guide](docs/COMMIT_GUIDE.md) - Commit message conventions
- [Contributing](CONTRIBUTING.md) - How to contribute
- [Security Policy](SECURITY.md) - Security and vulnerability reporting

## Requirements

- Home Assistant 2024.1.0 or newer
- Python 3.11 or newer
- Network access to DUCO device
- ducopy==17
- retrying==1.3.4

## Troubleshooting

### Integration Not Discovered

1. Ensure your DUCO device is on the same network
2. Check if the device supports Zeroconf/mDNS
3. Try manual configuration with the device IP address

### Connection Issues

1. Verify the IP address and port
2. Check firewall settings
3. Ensure the DUCO device is powered on and accessible
4. Check Home Assistant logs for error messages

### Enable Debug Logging

Add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.duco_ventilation_sun_control: debug
```

## Credits

This project was originally created by [@Sikerdebaard](https://github.com/Sikerdebaard). We are grateful for the foundation and vision he provided for this integration.

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for a full list of contributors.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Issues](https://github.com/stuartp44/haduco/issues) - Report bugs or request features
- [Discussions](https://github.com/stuartp44/haduco/discussions) - Ask questions or share ideas

## Disclaimer

This is a custom integration and is not officially supported by DUCO. Use at your own risk.

---

**Made for the Home Assistant community**
