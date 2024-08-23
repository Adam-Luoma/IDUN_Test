"""""
Sample script for using the Guardian Earbud Client

- Start recording data from the Guardian Earbuds
"""

import asyncio
from idun_guardian_sdk import GuardianClient

RECORDING_TIMER: int = (60 * 1)  # 1 min

my_api_token = "idun_GAtJDPZJ1bbs47Mf4KEBA3-v35iudqE3NSGSLD3OE8zE8KN2CHcN809-"


# Example callback function
def print_data(event):
    print("CB Func:", event.message)


if __name__ == "__main__":
    client = GuardianClient(api_token=my_api_token, debug=True)

    # Subscribe to live insights and/or realtime predictions
    client.subscribe_live_insights(raw_eeg=True, filtered_eeg=True, handler=print_data)
    client.subscribe_realtime_predictions(fft=True, jaw_clench=False, handler=print_data)

    # start a recording session
    asyncio.run(
        client.start_recording(
            recording_timer=RECORDING_TIMER,calc_latency=False
        )
    )