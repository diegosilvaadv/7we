/**
 * RFID Reader Android App
 * React Native implementation of the RFID Reader application
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  Alert,
  FlatList,
  Switch,
} from 'react-native';
import TcpSocket from 'react-native-tcp-socket';

interface EpcEntry {
  epc: string;
  timestamp: string;
  id: string;
}

interface ConnectionState {
  connected: boolean;
  connecting: boolean;
}

const App = (): JSX.Element => {
  // State management
  const [host, setHost] = useState('192.168.1.100');
  const [port, setPort] = useState('8080');
  const [connectionState, setConnectionState] = useState<ConnectionState>({
    connected: false,
    connecting: false,
  });
  const [reading, setReading] = useState(false);
  const [antennaPower, setAntennaPower] = useState(30);
  const [uniqueEpcs, setUniqueEpcs] = useState<Set<string>>(new Set());
  const [epcList, setEpcList] = useState<EpcEntry[]>([]);
  const [elapsedTime, setElapsedTime] = useState('00:00:00');
  const [startTime, setStartTime] = useState<Date | null>(null);

  // Refs
  const socketRef = useRef<TcpSocket.Socket | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const readingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Timer effect
  useEffect(() => {
    if (reading && startTime) {
      timerRef.current = setInterval(() => {
        const now = new Date();
        const elapsed = Math.floor((now.getTime() - startTime.getTime()) / 1000);
        const hours = Math.floor(elapsed / 3600);
        const minutes = Math.floor((elapsed % 3600) / 60);
        const seconds = elapsed % 60;
        setElapsedTime(
          `${hours.toString().padStart(2, '0')}:${minutes
            .toString()
            .padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
        );
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      if (!reading) {
        setElapsedTime('00:00:00');
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [reading, startTime]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (socketRef.current) {
        socketRef.current.destroy();
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (readingIntervalRef.current) {
        clearInterval(readingIntervalRef.current);
      }
    };
  }, []);

  const sendCommand = (command: any) => {
    if (socketRef.current && connectionState.connected) {
      try {
        const message = JSON.stringify(command) + '\n';
        socketRef.current.write(message);
      } catch (error) {
        console.error('Error sending command:', error);
        Alert.alert('Communication Error', 'Failed to send command');
      }
    }
  };

  const connect = () => {
    if (connectionState.connecting || connectionState.connected) return;

    setConnectionState({ connected: false, connecting: true });

    try {
      const socket = TcpSocket.createConnection(
        {
          port: parseInt(port, 10),
          host: host,
        },
        () => {
          console.log('Connected to RFID reader');
          setConnectionState({ connected: true, connecting: false });
          
          // Send initial antenna power setting
          sendCommand({ command: 'set_power', power: antennaPower });
          
          Alert.alert('Success', `Connected to RFID reader at ${host}:${port}`);
        }
      );

      socket.on('data', (data) => {
        // Handle incoming data from RFID reader
        const message = data.toString();
        console.log('Received:', message);
        // Parse and process EPC data here
      });

      socket.on('error', (error) => {
        console.error('Socket error:', error);
        setConnectionState({ connected: false, connecting: false });
        Alert.alert('Connection Error', `Failed to connect: ${error.message}`);
      });

      socket.on('close', () => {
        console.log('Connection closed');
        setConnectionState({ connected: false, connecting: false });
        if (reading) {
          stopReading();
        }
      });

      socketRef.current = socket;
    } catch (error) {
      console.error('Connection error:', error);
      setConnectionState({ connected: false, connecting: false });
      Alert.alert('Connection Error', 'Failed to create connection');
    }
  };

  const disconnect = () => {
    if (reading) {
      stopReading();
    }

    if (socketRef.current) {
      socketRef.current.destroy();
      socketRef.current = null;
    }

    setConnectionState({ connected: false, connecting: false });
  };

  const updateAntennaPower = (power: number) => {
    setAntennaPower(power);
    if (connectionState.connected) {
      sendCommand({ command: 'set_power', power });
    }
  };

  const startReading = () => {
    if (!connectionState.connected) {
      Alert.alert('Not Connected', 'Please connect to an RFID reader first.');
      return;
    }

    setReading(true);
    setStartTime(new Date());
    setUniqueEpcs(new Set());
    setEpcList([]);

    // Send start reading command
    sendCommand({ command: 'start_reading' });

    // Simulate reading EPCs for demo (in real app, receive from socket)
    readingIntervalRef.current = setInterval(() => {
      if (Math.random() < 0.3) { // 30% chance of new EPC
        const simulatedEpc = `E200${Math.floor(Math.random() * 9000 + 1000)}${Math.floor(Math.random() * 90000000 + 10000000)}`;
        processEpc(simulatedEpc);
      }
    }, 1000);
  };

  const stopReading = () => {
    setReading(false);

    if (readingIntervalRef.current) {
      clearInterval(readingIntervalRef.current);
      readingIntervalRef.current = null;
    }

    // Send stop reading command
    if (connectionState.connected) {
      sendCommand({ command: 'stop_reading' });
    }
  };

  const processEpc = (epc: string) => {
    setUniqueEpcs((prev) => {
      if (!prev.has(epc)) {
        const newSet = new Set(prev);
        newSet.add(epc);
        
        const timestamp = new Date().toLocaleTimeString();
        const newEntry: EpcEntry = {
          epc,
          timestamp,
          id: `${epc}_${Date.now()}`,
        };
        
        setEpcList((prevList) => [newEntry, ...prevList]);
        
        return newSet;
      }
      return prev;
    });
  };

  const renderEpcItem = ({ item }: { item: EpcEntry }) => (
    <View style={styles.epcItem}>
      <Text style={styles.epcText}>{item.epc}</Text>
      <Text style={styles.timestampText}>{item.timestamp}</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.backgroundStyle}>
      <StatusBar barStyle="dark-content" backgroundColor="#f8f9fa" />
      <ScrollView contentInsetAdjustmentBehavior="automatic" style={styles.container}>
        
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>RFID Reader</Text>
          <Text style={styles.headerSubtitle}>Android App</Text>
        </View>

        {/* Connection Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Connection Settings</Text>
          <View style={styles.row}>
            <Text style={styles.label}>Host:</Text>
            <TextInput
              style={styles.input}
              value={host}
              onChangeText={setHost}
              placeholder="192.168.1.100"
              editable={!connectionState.connected}
            />
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>Port:</Text>
            <TextInput
              style={styles.inputSmall}
              value={port}
              onChangeText={setPort}
              placeholder="8080"
              keyboardType="numeric"
              editable={!connectionState.connected}
            />
          </View>
          <TouchableOpacity
            style={[
              styles.button,
              connectionState.connected ? styles.buttonDisconnect : styles.buttonConnect,
              connectionState.connecting && styles.buttonDisabled,
            ]}
            onPress={connectionState.connected ? disconnect : connect}
            disabled={connectionState.connecting}>
            <Text style={styles.buttonText}>
              {connectionState.connecting
                ? 'Connecting...'
                : connectionState.connected
                ? 'Disconnect'
                : 'Connect'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Control Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Reader Controls</Text>
          <View style={styles.row}>
            <Text style={styles.label}>Antenna Power: {antennaPower} dBm</Text>
          </View>
          <View style={styles.sliderContainer}>
            <Text style={styles.sliderLabel}>10</Text>
            <View style={styles.sliderTrack}>
              <View 
                style={[
                  styles.sliderThumb, 
                  { left: `${((antennaPower - 10) / 20) * 100}%` }
                ]} 
              />
            </View>
            <Text style={styles.sliderLabel}>30</Text>
          </View>
          
          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={[
                styles.button,
                styles.buttonStart,
                (!connectionState.connected || reading) && styles.buttonDisabled,
              ]}
              onPress={startReading}
              disabled={!connectionState.connected || reading}>
              <Text style={styles.buttonText}>Start Reading</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[
                styles.button,
                styles.buttonStop,
                !reading && styles.buttonDisabled,
              ]}
              onPress={stopReading}
              disabled={!reading}>
              <Text style={styles.buttonText}>Stop Reading</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Status Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Status</Text>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Connection:</Text>
            <Text style={[
              styles.statusValue,
              connectionState.connected ? styles.connected : styles.disconnected
            ]}>
              {connectionState.connected ? 'Connected' : 'Disconnected'}
            </Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Timer:</Text>
            <Text style={styles.timerText}>{elapsedTime}</Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Unique EPCs:</Text>
            <Text style={styles.countText}>{uniqueEpcs.size}</Text>
          </View>
        </View>

        {/* EPCs List Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Detected EPCs</Text>
          <FlatList
            data={epcList}
            renderItem={renderEpcItem}
            keyExtractor={(item) => item.id}
            style={styles.epcList}
            showsVerticalScrollIndicator={true}
            nestedScrollEnabled={true}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  backgroundStyle: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  container: {
    flex: 1,
    padding: 16,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
    paddingVertical: 20,
    backgroundColor: '#ffffff',
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#7f8c8d',
    marginTop: 4,
  },
  section: {
    backgroundColor: '#ffffff',
    marginBottom: 16,
    padding: 16,
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 16,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  label: {
    fontSize: 16,
    color: '#34495e',
    marginRight: 12,
    minWidth: 80,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 4,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 16,
    backgroundColor: '#fff',
  },
  inputSmall: {
    width: 100,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 4,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 16,
    backgroundColor: '#fff',
  },
  button: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 6,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonConnect: {
    backgroundColor: '#27ae60',
  },
  buttonDisconnect: {
    backgroundColor: '#e74c3c',
  },
  buttonStart: {
    backgroundColor: '#3498db',
    flex: 1,
    marginRight: 8,
  },
  buttonStop: {
    backgroundColor: '#e67e22',
    flex: 1,
    marginLeft: 8,
  },
  buttonDisabled: {
    backgroundColor: '#bdc3c7',
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonRow: {
    flexDirection: 'row',
    marginTop: 16,
  },
  sliderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 12,
  },
  sliderTrack: {
    flex: 1,
    height: 4,
    backgroundColor: '#ecf0f1',
    marginHorizontal: 12,
    borderRadius: 2,
    position: 'relative',
  },
  sliderThumb: {
    position: 'absolute',
    width: 20,
    height: 20,
    backgroundColor: '#3498db',
    borderRadius: 10,
    top: -8,
    marginLeft: -10,
  },
  sliderLabel: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusLabel: {
    fontSize: 16,
    color: '#34495e',
    minWidth: 100,
  },
  statusValue: {
    fontSize: 16,
    fontWeight: '500',
  },
  connected: {
    color: '#27ae60',
  },
  disconnected: {
    color: '#e74c3c',
  },
  timerText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    fontFamily: 'monospace',
  },
  countText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#3498db',
  },
  epcList: {
    maxHeight: 300,
    borderWidth: 1,
    borderColor: '#ecf0f1',
    borderRadius: 4,
    padding: 8,
  },
  epcItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginVertical: 2,
    backgroundColor: '#f8f9fa',
    borderRadius: 4,
  },
  epcText: {
    fontSize: 14,
    fontFamily: 'monospace',
    color: '#2c3e50',
    flex: 1,
  },
  timestampText: {
    fontSize: 12,
    color: '#7f8c8d',
  },
});

export default App;