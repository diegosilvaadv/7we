# RFID Reader Android App

A React Native Android application for reading RFID tags over network connections.

## Features

- **Network Connectivity**: Connect to RFID readers via TCP/IP
- **Antenna Control**: Adjustable antenna power (10-30 dBm)
- **Real-time Reading**: Start/stop RFID tag reading with live updates
- **EPC Display**: Shows unique Electronic Product Codes with timestamps
- **Timer Function**: Tracks reading session duration
- **Modern UI**: Material Design inspired interface
- **Status Monitoring**: Connection status and reading statistics

## Prerequisites

- Node.js 16 or higher
- React Native CLI
- Android Studio with Android SDK
- Java Development Kit (JDK) 11 or higher

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd android_rfid_app
```

2. Install dependencies:
```bash
npm install
```

3. For Android development:
```bash
# Install Android dependencies
cd android
./gradlew build
cd ..
```

## Running the App

### Android

1. Start the Metro bundler:
```bash
npm start
```

2. In a separate terminal, run on Android:
```bash
npm run android
```

Or using React Native CLI:
```bash
react-native run-android
```

## Configuration

### RFID Reader Connection

The app connects to RFID readers via TCP/IP. Configure the connection in the app:

1. **Host**: IP address of the RFID reader (default: 192.168.1.100)
2. **Port**: TCP port of the RFID reader (default: 8080)

### Network Protocol

The app communicates with RFID readers using JSON commands:

```json
// Set antenna power
{"command": "set_power", "power": 25}

// Start reading
{"command": "start_reading"}

// Stop reading  
{"command": "stop_reading"}
```

## Usage

1. **Connect**: Enter the RFID reader's IP address and port, then tap "Connect"
2. **Configure**: Adjust antenna power using the slider (10-30 dBm)
3. **Read Tags**: Tap "Start Reading" to begin scanning for RFID tags
4. **Monitor**: View real-time EPC data, unique count, and session timer
5. **Stop**: Tap "Stop Reading" when finished

## Architecture

### Components

- `App.tsx`: Main application component with UI and logic
- `android/`: Native Android project files
- `index.js`: React Native entry point

### Key Features Implementation

- **TCP Socket Communication**: Uses `react-native-tcp-socket` for network connectivity
- **State Management**: React hooks for managing app state
- **Timer**: JavaScript intervals for session timing
- **EPC Processing**: Real-time processing and deduplication of RFID data

### Network Communication

The app establishes TCP connections to RFID readers and exchanges JSON messages. EPCs are processed in real-time with automatic deduplication to maintain unique tag counts.

## Customization

### UI Styling

The app uses React Native StyleSheet with Material Design principles. Colors and layout can be customized in the `styles` object in `App.tsx`.

### RFID Protocol

To integrate with different RFID reader models, modify the command format and parsing logic in the `sendCommand` and socket data handler functions.

### Performance Optimization

- EPC list is limited to prevent memory issues with large tag populations
- Network timeouts and error handling ensure robust connectivity
- State updates are optimized to prevent unnecessary re-renders

## Troubleshooting

### Connection Issues
- Verify RFID reader IP address and port
- Check network connectivity and firewall settings
- Ensure RFID reader supports TCP/IP communication

### Build Issues
- Ensure all dependencies are installed: `npm install`
- Clear Metro cache: `npm start --reset-cache`
- Clean Android build: `cd android && ./gradlew clean`

### Performance Issues
- Monitor device performance with large EPC datasets
- Consider implementing pagination for EPC display
- Check network latency and reader response times

## License

This project is licensed under the MIT License - see the LICENSE file for details.