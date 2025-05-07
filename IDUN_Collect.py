import asyncio
from pylsl import StreamInfo, StreamOutlet, local_clock
from idun_guardian_sdk import GuardianClient
import os
import time

'''
This script is used to collect EEG data from the IDUN Guardian and send it to a Lab Streaming Layer (LSL) outlet.
Note you will need to have a local .txt file with your API key in the same directory as this script.
The file should be named API_Key.txt and contain only the API key.
The script will also search for a stop_signal.txt file when the EEG data collection is complete, include writing this file in your experiment to terminate recording when needed.
'''

RECORDING_TIMER: int = (60 * 120)  # = 60 seconds * n minutes
directory = os.getcwd()  
api_path = os.path.join(directory, "API_Key.txt")
with open(api_path, 'r') as file:
    my_api_token = file.read().strip()  # Strip removes any whitespace or newline characters

print(f"API Key: {my_api_token}")

# Map timing to Unix epoch
unix_offset = time.time() - local_clock()

# Function to stop a task gracefully
async def stop_task(task):
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

def check_stop_signal():
    """Check if the stop signal file exists."""
    return os.path.exists("stop_signal.txt")

# Connect to the IDUN and stream data to LSL
async def main():
    client = GuardianClient(api_token=my_api_token, debug=True)
    client.address = await client.search_device()

    info = StreamInfo("IDUN", "EEG", 1, 250, "float32", client.address)
    lsl_outlet = StreamOutlet(info, 20, 360)

    # --- Add channel metadata ---
    chns = info.desc().append_child("channels")
    ch = chns.append_child("channel")
    ch.append_child_value("label", "IDUN_0")
    ch.append_child_value("unit", "microvolts")
    ch.append_child_value("type", "EEG")

    lsl_outlet = StreamOutlet(info, 20, 360)

    def lsl_stream_handler(event):
        message = event.message
        eeg = message["raw_eeg"]
        most_recent_ts = eeg[-1]["timestamp"] - unix_offset
        data = [sample["ch1"] for sample in eeg]
        lsl_outlet.push_chunk(data, most_recent_ts)

    client.subscribe_live_insights(
        raw_eeg=True,
        handler=lsl_stream_handler,
    )

    recording_task = asyncio.create_task(client.start_recording(recording_timer=RECORDING_TIMER))

    # Wait for the recording to finish or for a stop signal
    while not check_stop_signal():
        await asyncio.sleep(5)  # Non-blocking check for stop signal

    print("Stop signal received. Stopping tasks...")
    await stop_task(recording_task)

#clear previous stop signal file if it exists
if os.path.exists("stop_signal.txt"):
    os.remove("stop_signal.txt")

if __name__ == "__main__":
    asyncio.run(main())
