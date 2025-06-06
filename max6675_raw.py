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
        self._handle.max_speed_hz = 4300000  # Slower speed for better reliability
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
            # Wait a bit before reading (MAX6675 needs time between conversions)
            time.sleep(0.25)
            
            # Read 2 bytes from MAX6675
            vals = self._handle.readbytes(2)
            
            # Debug: Print raw bytes
            print(f"Raw bytes: {vals[0]:02X} {vals[1]:02X} (decimal: {vals[0]} {vals[1]})")
            
            # Combine bytes
            raw_value = (vals[0] << 8) | vals[1]
            print(f"Combined raw value: {raw_value:04X} (decimal: {raw_value})")
            
            # Check if thermocouple is connected (bit 2 of LSB)
            if vals[1] & 0x04:
                print("Warning: Thermocouple not connected (TC bit set)!")
                self._temperature = None
                return
            
            # Check for other error conditions
            if raw_value == 0:
                print("Warning: Raw value is 0 - possible wiring issue")
            
            # Extract temperature (shift right by 3 bits to remove status bits)
            temp_raw = raw_value >> 3
            print(f"Temperature raw value: {temp_raw} (0x{temp_raw:03X})")
            
            # Convert to temperature (each LSB = 0.25°C)
            temp_value = temp_raw * 0.25
            print(f"Calculated temperature: {temp_value}°C")
            
            self._temperature = temp_value
            
        except Exception as e:
            print(f"Error reading sensor: {e}")
            self._temperature = None

    def read_raw_debug(self):
        """Debug function to check raw SPI communication"""
        try:
            print("=== Debug SPI Communication ===")
            
            # Try multiple reads
            for i in range(3):
                print(f"\nRead #{i+1}:")
                time.sleep(0.25)  # Wait between reads
                vals = self._handle.readbytes(2)
                raw_value = (vals[0] << 8) | vals[1]
                
                print(f"  Raw bytes: 0x{vals[0]:02X} 0x{vals[1]:02X}")
                print(f"  Combined: 0x{raw_value:04X} ({raw_value})")
                print(f"  TC bit (should be 0): {(vals[1] & 0x04) >> 2}")
                print(f"  Temperature bits: {raw_value >> 3}")
                print(f"  Temperature: {(raw_value >> 3) * 0.25}°C")
                
        except Exception as e:
            print(f"Debug read error: {e}")

if __name__ == '__main__':
    try:
        print("MAX6675 Debug Test")
        print("==================")
        
        sensor = Max6675(0, 0)
        
        # First, do a raw debug read
        sensor.read_raw_debug()
        
        print("\n=== Normal Reading Test ===")
        for i in range(5):
            print(f"\nReading #{i+1}:")
            temp = sensor.temperature
            if temp is not None:
                print(f"Temperature: {temp}°C ({temp * 9/5 + 32:.1f}°F)")
            else:
                print("Temperature: No reading")
            time.sleep(2)
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting checklist:")
        print("1. Is SPI enabled? (sudo raspi-config)")
        print("2. Wiring connections:")
        print("   VCC → 3.3V or 5V")
        print("   GND → Ground") 
        print("   SCK → GPIO 11 (Pin 23)")
        print("   CS  → GPIO 8 (Pin 24)")
        print("   SO  → GPIO 9 (Pin 21)")
        print("3. Is thermocouple properly connected to MAX6675?")
        print("4. Try touching thermocouple with finger to see if reading changes")
