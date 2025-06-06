import sensorbase
import spidev
import time

class Max6675(sensorbase.SensorBase):
    def __init__(self, bus=None, client=None, name="Sensor"):
        '''Initializes the sensor.
        bus: The SPI bus.
        client: The identifier of the client (CS pin).
        name: Friendly name for the sensor.
        '''
        assert(bus is not None)
        assert(client is not None)
        super(Max6675, self).__init__(self._update_sensor_data)
        self._bus = bus
        self._client = client
        self._name = name
        self._temperature = None
        self._handle = spidev.SpiDev(self._bus, self._client)
        # Configure SPI settings for MAX6675
        self._handle.max_speed_hz = 5000000  # 5MHz max for MAX6675
        self._handle.mode = 0b00  # SPI mode 0

    def __del__(self):
        if hasattr(self, '_handle'):
            self._handle.close()

    @property
    def temperature(self):
        '''Returns a temperature value. Returns None if no valid value is
        set yet.
        '''
        self._update()
        return self._temperature
    
    @property
    def name(self):
        '''Returns the sensor name.'''
        return self._name

    def _update_sensor_data(self):
        try:
            # Read 2 bytes from MAX6675
            vals = self._handle.readbytes(2)
            
            # Debug: Show raw data when temperature is 0
            raw_value = (vals[0] << 8) | vals[1]
            temp_value = (raw_value >> 3) * 0.25
            
            if temp_value == 0:
                print(f"Debug [{self._name}] - Raw bytes: 0x{vals[0]:02X} 0x{vals[1]:02X}, Combined: 0x{raw_value:04X}")
            
            # Check if thermocouple is connected (bit 2 of second byte)
            if vals[1] & 0x04:
                print(f"Warning [{self._name}]: Thermocouple not connected (TC bit set)!")
                self._temperature = None
                return
            
            # Check for all zeros (possible short circuit)
            if raw_value == 0:
                print(f"Warning [{self._name}]: Raw data is 0 - possible short circuit or connection issue")
                self._temperature = None
                return
            
            # Convert to temperature
            # Combine bytes and shift right by 3 bits, then multiply by 0.25
            self._temperature = temp_value
            
        except Exception as e:
            print(f"Error reading sensor [{self._name}]: {e}")
            self._temperature = None

class DualMax6675:
    '''Class to manage two MAX6675 sensors'''
    
    def __init__(self, sensor1_config, sensor2_config):
        '''
        Initialize dual MAX6675 sensors
        sensor1_config: dict with keys 'bus', 'client', 'name'
        sensor2_config: dict with keys 'bus', 'client', 'name'
        
        Example:
        sensor1_config = {'bus': 0, 'client': 0, 'name': 'Sensor 1'}
        sensor2_config = {'bus': 0, 'client': 1, 'name': 'Sensor 2'}
        '''
        self.sensor1 = Max6675(
            bus=sensor1_config['bus'], 
            client=sensor1_config['client'],
            name=sensor1_config['name']
        )
        self.sensor2 = Max6675(
            bus=sensor2_config['bus'], 
            client=sensor2_config['client'],
            name=sensor2_config['name']
        )
        
        # Set cache lifetime for both sensors
        self.sensor1.cache_lifetime = 0
        self.sensor2.cache_lifetime = 0
    
    def read_both(self):
        '''Read temperatures from both sensors'''
        temp1 = self.sensor1.temperature
        temp2 = self.sensor2.temperature
        return temp1, temp2
    
    def read_sensor1(self):
        '''Read temperature from sensor 1 only'''
        return self.sensor1.temperature
    
    def read_sensor2(self):
        '''Read temperature from sensor 2 only'''
        return self.sensor2.temperature
    
    def get_sensor_names(self):
        '''Get names of both sensors'''
        return self.sensor1.name, self.sensor2.name

if __name__ == '__main__':
    try:
        # Configuration for dual sensors
        # Sensor 1: SPI Bus 0, CS0 (GPIO 8, Pin 24)
        # Sensor 2: SPI Bus 0, CS1 (GPIO 7, Pin 26)
        sensor1_config = {'bus': 0, 'client': 0, 'name': 'Thermocouple 1'}
        sensor2_config = {'bus': 0, 'client': 1, 'name': 'Thermocouple 2'}
        
        # Initialize dual sensor system
        dual_sensors = DualMax6675(sensor1_config, sensor2_config)
        
        print("Dual MAX6675 Thermocouple Reader")
        print("Sensor 1: CS0 (GPIO 8, Pin 24)")
        print("Sensor 2: CS1 (GPIO 7, Pin 26)")
        print("Press Ctrl+C to exit")
        print("-" * 50)
        
        while True:
            # Read both temperatures
            temp1, temp2 = dual_sensors.read_both()
            
            # Display results
            print(f"{time.strftime('%H:%M:%S')} | ", end="")
            
            if temp1 is not None:
                temp1_f = temp1 * 9/5 + 32
                print(f"T1: {temp1:.2f}°C ({temp1_f:.1f}°F) | ", end="")
            else:
                print("T1: No reading | ", end="")
            
            if temp2 is not None:
                temp2_f = temp2 * 9/5 + 32
                print(f"T2: {temp2:.2f}°C ({temp2_f:.1f}°F)", end="")
            else:
                print("T2: No reading", end="")
            
            # Show temperature difference if both readings are valid
            if temp1 is not None and temp2 is not None:
                diff = abs(temp1 - temp2)
                print(f" | Diff: {diff:.2f}°C")
            else:
                print()
            
            time.sleep(1)  # Update every second
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        print("\nWiring for dual sensors:")
        print("Common connections:")
        print("  Both VCC → 3.3V or 5V")
        print("  Both GND → Ground")
        print("  Both SCK → GPIO 11 (Pin 23)")
        print("  Both SO → GPIO 9 (Pin 21)")
        print("Individual CS connections:")
        print("  Sensor 1 CS → GPIO 8 (Pin 24)")
        print("  Sensor 2 CS → GPIO 7 (Pin 26)")
