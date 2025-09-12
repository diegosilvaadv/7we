# RFID Reader Web Application

A modern web-based RFID reader application that replaces the desktop tkinter version with a responsive, user-friendly web interface.

## Features

### Core Functionality
- **Connection Management**: Connect/disconnect to RFID reader
- **Antenna Power Control**: Adjustable power levels (0-100%)
- **Reading Control**: Start/stop RFID reading operations
- **Real-time EPC Display**: Shows unique Electronic Product Codes as they're detected
- **Timer**: Real-time elapsed time tracking during reading sessions
- **EPC Count**: Live count of unique EPCs detected

### Web Interface
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Clean, professional interface with gradient backgrounds
- **Real-time Updates**: Live status updates and EPC detection
- **Interactive Controls**: Intuitive buttons and sliders
- **Toast Notifications**: User-friendly success/error messages
- **Export Functionality**: Download EPCs as CSV file

## Technology Stack

### Backend
- **Flask**: Python web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Threading**: Concurrent EPC reading simulation
- **JSON API**: RESTful endpoints for frontend communication

### Frontend
- **HTML5**: Modern semantic markup
- **CSS3**: Advanced styling with gradients, animations, and responsive design
- **Vanilla JavaScript**: No framework dependencies, pure ES6+
- **Font Awesome**: Icon library (from CDN)

## Project Structure

```
7we/
├── app.py                 # Main Flask application
├── rfid_desktop_app.py    # Reference desktop tkinter version
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── css/
│   │   └── style.css     # Application styles
│   └── js/
│       └── app.js        # Frontend JavaScript
└── README.md             # This file
```

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/diegosilvaadv/7we.git
   cd 7we
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python3 app.py
   ```

4. **Access the web interface**:
   Open your browser and navigate to `http://localhost:5000`

## Usage

### Getting Started
1. **Connect**: Click the "Connect" button to establish connection with the RFID reader
2. **Adjust Power**: Use the slider to set antenna power level (0-100%)
3. **Start Reading**: Click "Start Reading" to begin EPC detection
4. **Monitor Results**: Watch the timer and EPC count update in real-time
5. **View EPCs**: See detected EPCs with timestamps in the scrollable list
6. **Export Data**: Use the "Export" button to download EPCs as CSV
7. **Stop/Clear**: Stop reading or clear all EPCs as needed

### API Endpoints

The application provides a RESTful API:

- `POST /api/connect` - Connect to RFID reader
- `POST /api/disconnect` - Disconnect from RFID reader  
- `POST /api/power` - Set antenna power level
- `POST /api/start` - Start reading EPCs
- `POST /api/stop` - Stop reading EPCs
- `POST /api/clear` - Clear all EPCs
- `GET /api/status` - Get application status
- `GET /api/epcs` - Get detected EPCs

## Mock RFID Implementation

The application includes a `MockRFIDReader` class that simulates real RFID hardware:
- Generates random EPCs with realistic format (E200XXXXXXXXXXXX)
- Simulates connection delays and reading intervals
- Thread-safe operations with proper locking
- Configurable detection probability for testing

## Desktop Reference Version

The `rfid_desktop_app.py` file contains a tkinter-based desktop version that demonstrates the same functionality. This serves as a reference for the core RFID operations that were migrated to the web version.

## Browser Compatibility

- Chrome/Chromium 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Development

### Running in Development Mode
The Flask application runs in debug mode by default, providing:
- Auto-reload on file changes
- Detailed error messages
- Debug toolbar

### Customization
- Modify `static/css/style.css` for styling changes
- Update `static/js/app.js` for frontend functionality
- Extend `app.py` for new API endpoints or RFID features

## Production Deployment

For production use:
1. Set `debug=False` in `app.py`
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure proper security headers
4. Set up HTTPS
5. Use a real RFID reader implementation

## License

This project is open source. Please refer to the repository license for details.