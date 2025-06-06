import sensorbase
import spidev
import time

class Max6675(sensorbase.SensorBase):
    def __init__(self, bus=None, client=None):
        '''Initializes the sensor.
        bus: The SPI bus.
        client: The identifier of the client.
        '''
        assert(bus is not None)
        assert(client is not None)
        super(Max6675, self).__init__(self._update_sensor_data)
        self._bus = bus
        self._client = client
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

    def _update_sensor_data(self):
        try:
            # Read 2 bytes from MAX6675
            vals = self._handle.readbytes(2)
            
            # Check if thermocouple is connected (bit 2 of second byte)
            if vals[1] & 0x04:
                print("Warning: Thermocouple not connected!")
                self._temperature = None
                return
            
            # Convert to temperature
            # Combine bytes and shift right by 3 bits, then multiply by 0.25
            raw_value = (vals[0] << 8) | vals[1]
            temp_value = (raw_value >> 3) * 0.25
            self._temperature = temp_value
            
        except Exception as e:
            print(f"Error reading sensor: {e}")
            self._temperature = None

if __name__ == '__main__':
    try:
        sensor = Max6675(0, 0)
        sensor.cache_lifetime = 0  # Set cache to 0 for real-time readings
        
        print("MAX6675 Thermocouple Reader")
        print("Press Ctrl+C to exit")
        print("-" * 30)
        
        while True:
            temp = sensor.temperature
            if temp is not None:
                # Display temperature in both Celsius and Fahrenheit
                temp_f = temp * 9/5 + 32
                print(f"Temperature: {temp:.2f}°C ({temp_f:.2f}°F)")
            else:
                print("Temperature: No reading")
            
            time.sleep(1)  # Update every second
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure SPI is enabled and wiring is correct.")
