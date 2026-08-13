import asyncio
from winrt.windows.devices.bluetooth import BluetoothDevice, BluetoothConnectionStatus

PHONE_ADDRESS = 0x28024443D815

async def main():
    device = await BluetoothDevice.from_bluetooth_address_async(PHONE_ADDRESS)
    if device is None:
        print("Device not found")
        return
    status = device.connection_status
    print("Connected" if status == BluetoothConnectionStatus.CONNECTED else "Disconnected")

asyncio.run(main())