# RFID Reader Applications

This repository contains both desktop and Android implementations of an RFID Reader application for connecting to and controlling RFID readers over network connections.

## Applications

### 1. Desktop Application (`rfid_reader_app.py`)
A Python/Tkinter desktop application with full RFID reader functionality.

**Features:**
- Network connection to RFID readers via TCP/IP
- Antenna power control (10-30 dBm) with slider interface
- Start/stop reading functionality
- Real-time EPC (Electronic Product Code) display
- Session timer with elapsed time tracking
- Unique EPC count monitoring
- Status indicators for connection and reading state
- Scrollable EPC list with timestamps

**Requirements:**
- Python 3.6+
- tkinter (usually included with Python)

**Usage:**
```bash
python3 rfid_reader_app.py
```

### 2. Android Application (`android_rfid_app/`)
A React Native Android application with modern UI and the same core functionality as the desktop version.

**Features:**
- Modern Material Design inspired interface
- TCP/IP connectivity to RFID readers
- Antenna power control with visual slider
- Real-time EPC scanning and display
- Session timer and unique EPC counter
- Connection status monitoring
- Responsive touch interface optimized for mobile

**Requirements:**
- Node.js 16+
- React Native CLI
- Android Studio
- Android SDK

**Setup:**
```bash
cd android_rfid_app
npm install
npm run android
```

## RFID Reader Communication Protocol

Both applications communicate with RFID readers using JSON over TCP/IP:

### Commands Sent to Reader:
```json
{"command": "set_power", "power": 25}      # Set antenna power (10-30 dBm)
{"command": "start_reading"}               # Start RFID tag scanning
{"command": "stop_reading"}                # Stop RFID tag scanning
```

### Expected Data from Reader:
The applications expect to receive EPC data from the RFID reader. The current implementation includes simulation for testing purposes.

## Configuration

### Network Settings
- **Default Host**: 192.168.1.100
- **Default Port**: 8080
- **Protocol**: TCP/IP with JSON messages

### Antenna Power
- **Range**: 10-30 dBm
- **Default**: 30 dBm
- **Control**: Real-time adjustment with immediate transmission to reader

## Feature Comparison

| Feature | Desktop App | Android App |
|---------|-------------|-------------|
| Network Connectivity | ✅ | ✅ |
| Antenna Power Control | ✅ | ✅ |
| Start/Stop Reading | ✅ | ✅ |
| EPC Display | ✅ | ✅ |
| Session Timer | ✅ | ✅ |
| Unique EPC Counter | ✅ | ✅ |
| Connection Status | ✅ | ✅ |
| Touch Interface | ❌ | ✅ |
| Material Design | ❌ | ✅ |
| Cross-platform | Limited | Android |
| Deployment | Direct execution | APK package |

## Architecture

### Desktop Application Architecture
- **Framework**: Python + Tkinter
- **Networking**: Python socket library
- **Threading**: Background threads for non-blocking network I/O
- **State Management**: Class-based state with Tkinter variables

### Android Application Architecture
- **Framework**: React Native
- **Networking**: react-native-tcp-socket library
- **State Management**: React hooks (useState, useEffect)
- **UI**: Native Android components with React Native styling
- **Threading**: JavaScript event loop with intervals for timing

## Testing

Both applications include simulation modes for testing without actual RFID hardware:
- Simulated EPC generation for testing UI and data flow
- Network connection simulation
- Timer and counter validation

## Deployment

### Desktop Application
1. Ensure Python 3.6+ is installed
2. Install tkinter if not included: `sudo apt-get install python3-tk`
3. Run directly: `python3 rfid_reader_app.py`

### Android Application
1. Install development environment (Node.js, React Native, Android Studio)
2. Build and run: `cd android_rfid_app && npm run android`
3. For production: Build signed APK using React Native CLI

## Future Enhancements

- **iOS Support**: Extend React Native app to support iOS devices
- **Cloud Integration**: Add cloud-based EPC data storage and analytics
- **Multi-Reader Support**: Connect to multiple RFID readers simultaneously
- **Advanced Filtering**: Add EPC filtering and search capabilities
- **Batch Operations**: Support for bulk RFID operations
- **Export Functionality**: Export EPC data to CSV/JSON formats
- **Authentication**: Add user authentication and access control

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on both platforms
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.