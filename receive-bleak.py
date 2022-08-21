import asyncio
from bleak import BleakClient, BleakScanner


async def discover():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)

async def main():
    address = "6B:62:70:1F:F9:72"
    count_id = "19C20000-E8F2-537E-4F6C-D104768A1214"
    async with BleakClient(address) as client:
        print("connected to "+address)

        # print("Model Number: {0}".format("".join(map(chr, model_number))))
        while(True):
            count = await client.read_gatt_char(count_id)
            count_int = bytes(count).hex()
            print(int(count_int))


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    print('\nReceived Keyboard Interrupt')
finally:
    print('Program finished')
