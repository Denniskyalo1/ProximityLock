import asyncio
from bleak import BleakScanner

async def main():
    devices = await BleakScanner.discover(timeout=20.0, return_adv=True)
    for d, adv in devices.values():
        print(d.address, d.name, adv.rssi)

asyncio.run(main())