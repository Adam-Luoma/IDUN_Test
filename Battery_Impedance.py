
import asyncio
from idun_guardian_sdk import GuardianClient

def print_impedance(data):
    print(f"{data}\tOhm")

if __name__ == "__main__":
    client = GuardianClient(debug=True)
    battery_level = asyncio.run(client.check_battery())
    print("Battery Level: %s%%" % battery_level)
    asyncio.run(client.stream_impedance(handler=print_impedance))