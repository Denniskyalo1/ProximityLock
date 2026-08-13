import asyncio
import subprocess
import os
import datetime
from dotenv import load_dotenv
from winrt.windows.devices.bluetooth import BluetoothDevice, BluetoothConnectionStatus

load_dotenv()

PHONE_ADDRESS = int(os.getenv("PHONE_ADDRESS"), 16)
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 10))
LOCK_AFTER = int(os.getenv("LOCK_AFTER", 3))
SHUTDOWN_AFTER = int(os.getenv("SHUTDOWN_AFTER", 15))
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 2))

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proximity_lock.log")

missed = 0

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def lock_pc():
    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])

def shutdown_pc():
    subprocess.run(["shutdown", "/s", "/t", "0"])

async def is_connected():
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            device = await BluetoothDevice.from_bluetooth_address_async(PHONE_ADDRESS)
            if device is not None and device.connection_status == BluetoothConnectionStatus.CONNECTED:
                return True
        except Exception as e:
            log(f"Error checking connection (attempt {attempt}): {e}")
        if attempt < RETRY_ATTEMPTS:
            await asyncio.sleep(RETRY_DELAY)
    return False

async def main():
    global missed
    log("Proximity monitor started.")
    while True:
        connected = await is_connected()

        if connected:
            if missed > 0:
                log(f"Phone reconnected after {missed} missed check(s). Reset.")
            missed = 0
        else:
            missed += 1
            log(f"Missed check {missed}/{SHUTDOWN_AFTER}")

            if missed == LOCK_AFTER:
                log("Threshold reached — locking workstation.")
                lock_pc()
            if missed >= SHUTDOWN_AFTER:
                log("Threshold reached — shutting down.")
                shutdown_pc()
                break

        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())