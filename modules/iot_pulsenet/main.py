# File: modules/iot_pulsenet/main.py

import uasyncio as asyncio
import time
import ujson
import network
import urequests
from machine import Pin, I2C, SPI

# ---------- USER CONFIGURATION (MUST BE SET BY USER) ----------
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
SENSOR_ID = "Iot_pulsenet-01"  # Give each device a unique name

# IMPORTANT: Replace this with your actual local IP address.
YOUR_IP = "192.xxx.x.xxx"
REFLEX_API_URL_NOTIFY = f"http://{YOUR_IP}:8001/api/actions/notify_admin"
REFLEX_API_URL_SECURITY = f"http://{YOUR_IP}:8001/api/actions/call_security"
INSIGHTCLOUD_API_URL = f"http://{YOUR_IP}:8002/health/ping/iot_pulsenet"


# ---------- HARDWARE & THRESHOLD CONFIGURATION ----------
I2C0_ID, I2C0_SDA, I2C0_SCL = 0, 4, 5
I2C1_ID, I2C1_SDA, I2C1_SCL = 1, 2, 3
SPI_ID, SPI_SCK, SPI_MOSI, SPI_MISO, SPI_CS = 1, 10, 11, 12, 13
NEOPIXEL_PIN = 16
OLED_ADDR, OLED_W, OLED_H = 0x3C, 128, 64
MQ2_ADC_CHANNEL = 0
EVENT_RETENTION_LIMIT = 50

# Critical Event Thresholds (Edge Intelligence)
TEMP_CRITICAL_THRESHOLD_C = 45.0
GAS_CRITICAL_THRESHOLD_ADC = 800
HEART_RATE_HIGH_BPM = 130
HEART_RATE_LOW_BPM = 45
ALERT_COOLDOWN_SECONDS = 60  # Wait 60s before re-sending the same type of alert

# ---------- DRIVER IMPORTS (Requires files in /lib) ----------
try: import ssd1306
except ImportError: ssd1306 = None
try: import bme280
except ImportError: bme280 = None
try: from max30102 import MAX30102
except ImportError: MAX30102 = None
try: from neopixel import NeoPixel
except ImportError: NeoPixel = None

# ---------- GLOBAL HARDWARE OBJECTS ----------
# Defined globally so the final cleanup block can access them.
i2c0 = I2C(I2C0_ID, scl=Pin(I2C0_SCL), sda=Pin(I2C0_SDA), freq=400000)
i2c1 = I2C(I2C1_ID, scl=Pin(I2C1_SCL), sda=Pin(I2C1_SDA), freq=100000)
spi = SPI(SPI_ID, baudrate=1_000_000, sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))
cs = Pin(SPI_CS, Pin.OUT, value=1)
oled, bme, max_sensor, _np = None, None, None, None

def initialize_hardware():
    """Initializes all hardware peripherals safely."""
    global oled, bme, max_sensor, _np
    if ssd1306:
        try: oled = ssd1306.SSD1306_I2C(OLED_W, OLED_H, i2c0, addr=OLED_ADDR, external_vcc=False)
        except Exception as e: print(f"OLED init error: {e}")
    if bme280:
        try:
            addr = next((a for a in i2c0.scan() if a in [0x76, 0x77]), None)
            if addr: bme = bme280.BME280(i2c=i2c0, address=addr)
            else: print("BME280 not found.")
        except Exception as e: print(f"BME280 init error: {e}")
    if MAX30102:
        try: max_sensor = MAX30102(i2c=i2c1)
        except Exception as e: print(f"MAX30102 init error: {e}")
    if NeoPixel:
        try: _np = NeoPixel(Pin(NEOPIXEL_PIN), 1)
        except Exception as e: print(f"NeoPixel init error: {e}")

# ---------- MCP3008 ADC Driver ----------
class MCP3008:
    def __init__(self, spi_bus, cs_pin):
        self.spi, self.cs, self._out, self._in = spi_bus, cs_pin, bytearray(3), bytearray(3)
        self._out[0] = 0x01
    def read(self, channel):
        if not (0 <= channel <= 7): raise ValueError("Channel must be 0-7")
        self._out[1] = (8 | channel) << 4
        self.cs.value(0)
        self.spi.write_readinto(self._out, self._in)
        self.cs.value(1)
        return ((self._in[1] & 3) << 8) | self._in[2]

mcp = MCP3008(spi, cs)

# ---------- SHARED STATE & EVENT HANDLING ----------
state = { "bme": None, "max301": None, "mq2": None, "heart_rate": 0 }
critical_event_queue = []
last_alert_times = {}

def push_critical_event(event_type, data):
    """Adds a high-priority event to the queue to be sent to the NeuraCity backend."""
    current_time = time.time()
    if (current_time - last_alert_times.get(event_type, 0)) > ALERT_COOLDOWN_SECONDS:
        last_alert_times[event_type] = current_time
        event = {"type": event_type, "data": data}
        critical_event_queue.append(event)
        print(f"CRITICAL EVENT QUEUED >> {ujson.dumps(event)}")

# ---------- WIFI & BPM LOGIC ----------
wlan = network.WLAN(network.STA_IF)

async def connect_to_wifi():
    """Connects the Pico W to the configured WiFi network."""
    if wlan.isconnected(): return True
    print(f"Connecting to WiFi: {WIFI_SSID}...")
    if oled: oled.fill(0); oled.text("Connecting WiFi", 0, 28); oled.show()
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(15):
        if wlan.status() >= 3:
            ip = wlan.ifconfig()[0]
            print(f"Connected! IP: {ip}")
            if oled: oled.fill(0); oled.text("WiFi OK", 0, 28); oled.text(ip, 0, 40); oled.show()
            if _np: _np[0] = (0, 15, 0); _np.write()
            return True
        await asyncio.sleep(1)
    print("WiFi connection failed!")
    if oled: oled.fill(0); oled.text("WiFi FAILED!", 0, 28); oled.show()
    if _np: _np[0] = (20, 0, 0); _np.write()
    return False

ir_history = []
last_beat_time_ms = 0

def calculate_bpm_from_ir(ir_value):
    """A simple peak-detection algorithm to estimate BPM from IR readings."""
    global ir_history, last_beat_time_ms
    ir_history.append(ir_value)
    if len(ir_history) > 50: ir_history.pop(0)
    if len(ir_history) < 20: return state.get('heart_rate', 0)
    
    avg = sum(ir_history) / len(ir_history)
    threshold = avg * 1.05 # A peak is 5% above the rolling average
    current_time_ms = time.ticks_ms()

    if ir_value > threshold and time.ticks_diff(current_time_ms, last_beat_time_ms) > 300: # 300ms debounce
        bpm = 60000.0 / time.ticks_diff(current_time_ms, last_beat_time_ms)
        last_beat_time_ms = current_time_ms
        return int(bpm) if 30 < bpm < 220 else state.get('heart_rate', 0)
    return state.get('heart_rate', 0)

# ---------- ASYNCHRONOUS TASKS (WITH EDGE INTELLIGENCE) ----------
async def task_bme():
    if not bme: return
    while True:
        try:
            temp_str, _, _ = bme.values
            temp_c = float(temp_str[:-1])
            state['bme'] = bme.values
            if temp_c > TEMP_CRITICAL_THRESHOLD_C:
                push_critical_event("overheat_alert", {"temperature_c": temp_c})
        except Exception as e: print(f"BME Err: {e}")
        await asyncio.sleep(5)

async def task_max30102():
    if not max_sensor: return
    await asyncio.sleep(2) # Allow settling time
    while True:
        try:
            r, ir = max_sensor.read_sequential(1)[0]
            state['max301'] = {"red": r, "ir": ir}
            bpm = calculate_bpm_from_ir(ir)
            state['heart_rate'] = bpm
            if bpm > HEART_RATE_HIGH_BPM:
                push_critical_event("heart_rate_high", {"bpm": bpm})
            elif bpm > 10 and bpm < HEART_RATE_LOW_BPM:
                push_critical_event("heart_rate_low", {"bpm": bpm})
        except Exception as e: print(f"MAX301 Err: {e}")
        await asyncio.sleep(0.1)

async def task_mq2():
    if not mcp: return
    while True:
        try:
            val = mcp.read(MQ2_ADC_CHANNEL)
            state['mq2'] = val
            if val > GAS_CRITICAL_THRESHOLD_ADC:
                push_critical_event("gas_alert",{"adc": val})
        except Exception as e: print(f"MQ2 Err: {e}")
        await asyncio.sleep(1)

# ---------- SYSTEM TASKS (INTEGRATION & DISPLAY) ----------
async def task_health_pinger():
    """
    Periodically sends a heartbeat to InsightCloud to report that this
    IoT device is alive and operational. Runs in the background.
    """

    # Wait for WiFi to connect before starting
    while not wlan.isconnected():
        await asyncio.sleep(5)
        
    while True:
        try:
            print("Sending health ping to InsightCloud...")
            response = urequests.post(INSIGHTCLOUD_API_URL, timeout=5)
            if response.status_code == 200:
                print("Health ping ACK.")
            else:
                print(f"Health ping failed. Status: {response.status_code}")
            response.close()
        except Exception as e:
            print(f"Health ping failed. Exception: {e}")
        
        # Send a ping every 30 seconds
        await asyncio.sleep(30)

async def task_event_consumer():
    """Consumes critical events and sends them to the NeuraCity backend."""
    while True:
        if wlan.isconnected() and critical_event_queue:
            event_to_send = critical_event_queue.pop(0)
            event_type = event_to_send.get('type')
            event_data = event_to_send.get('data', {})
            
            is_security_alert = event_type in ['gas_alert', 'heart_rate_low']
            api_url = REFLEX_API_URL_SECURITY if is_security_alert else REFLEX_API_URL_NOTIFY
            
            message_summary = f"Alert from {SENSOR_ID}: {event_type} - {ujson.dumps(event_data)}"
            payload = {
                "department": "HealthAndSafety", "message": message_summary, "source_module": "iot_pulsenet"
            }
            if is_security_alert:
                payload = {"location": f"IoT Device '{SENSOR_ID}' reports {event_type}", "source_module": "iot_pulsenet"}

            try:
                print(f"SENDING TO BACKEND: {payload}")
                response = urequests.post(
                    api_url,
                    headers={'content-type': 'application/json'},
                    data=ujson.dumps(payload)
                )
                if response.status_code == 200: print("Backend ACK.")
                else: print(f"Backend Err: {response.status_code} - {response.text}")
                response.close()
            except Exception as e:
                print(f"Failed to send event: {e}")
                critical_event_queue.insert(0, event_to_send) # Re-queue on failure
                await asyncio.sleep(10)
        
        await asyncio.sleep(1)

async def task_oled_dashboard():
    """Displays real-time, local sensor data on the OLED."""
    await asyncio.sleep(3) # Initial delay to let sensors populate
    while True:
        try:
            if oled:
                oled.fill(0)
                oled.text("IoT PulseNet", 0, 0)
                
                # 1. Safely get all data at the beginning.
                bme_data = state.get('bme')
                max301_data = state.get('max301', {})
                mq2_data = state.get('mq2')
                bpm_data = state.get('heart_rate')

                # 2. Define default values for all variables.
                t, h, p, gas, ir, bpm = "--", "--", "--", "--", "--", "--"
                
                # 3. Use a robust try-except block to parse the sensor tuple.
                if bme_data and isinstance(bme_data, (list, tuple)) and len(bme_data) == 3:
                    try:
                        t = bme_data[0].replace("C","")
                        p = bme_data[1].replace("hPa","")
                        h = bme_data[2].replace("%","")
                    except Exception:
                        pass # Keep defaults if parsing fails
                
                if mq2_data is not None: gas = str(mq2_data)
                if bpm_data is not None: bpm = str(bpm_data)
                
                # 4. Display the guaranteed values.
                oled.text(f"T:{t}C H:{h}%", 0, 16)
                oled.text(f"Gas:{gas}  BPM:{bpm}", 0, 32)
                oled.text(f"Pressure:{p}", 0, 48)

                oled.show()
        except Exception as e: print(f"OLED Dashboard err: {e}")
        await asyncio.sleep(1)
        
# ---------- MAIN EXECUTION ----------
async def main():
    initialize_hardware() # Initialize all hardware objects
    
    if oled: oled.fill(0); oled.text("Booting...", 0, 28); oled.show()
    await connect_to_wifi()
    
    tasks = [ task_event_consumer(), task_mq2(), task_oled_dashboard(), task_health_pinger() ]
    if bme: tasks.append(task_bme())
    if max_sensor: tasks.append(task_max30102())
    
    print("Starting all sensor tasks...")
    await asyncio.gather(*(asyncio.create_task(task) for task in tasks))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    finally:
        if _np: _np[0] = (0,0,0); _np.write()
        if oled: oled.fill(0); oled.show()
        asyncio.new_event_loop() 
        print("IoT_PulseNet service terminated.")
