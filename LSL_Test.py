import asyncio
from pylsl import StreamInfo, StreamOutlet

from idun_guardian_sdk import GuardianClient

#initialize IDUN System
RECORDING_TIMER: int = (60 * 2)  # 60 sec * 2 min
my_api_token = "idun_GAtJDPZJ1bbs47Mf4KEBA3-v35iudqE3NSGSLD3OE8zE8KN2CHcN809-"
my_address = "E5-1E-FD-F5-15-26"


async def stop_task(task):
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def read_battery_30s(client):             # Every 30 seconds give an updated battery reading while running
    while True:
        battery = await client.check_battery()
        print("Battery Level: %s%%" % battery)
        await asyncio.sleep(30)
   

async def start_recording(client):
    print("Starting recording...")
    await client.start_recording(recording_timer=RECORDING_TIMER)
    print("Recording finished.")

async def main():
    client = GuardianClient(api_token=my_api_token, debug=True)
    client.address = asyncio.run(client.search_device())

    info = StreamInfo(name ="IDUN", 
                      type = "EEG", 
                      channel_count = 1,
                      nominal_srate = 250, 
                      channel_format = "float32", 
                      source_id = client.address)
    lsl_outlet = StreamOutlet(info, 20, 360)

    def lsl_stream_handler(event):
        message = event.message
        eeg = message["raw_eeg"]
        most_recent_ts = eeg[-1]["timestamp"]
        data = [sample["ch1"] for sample in eeg]
        lsl_outlet.push_chunk(data, most_recent_ts)

    client.subscribe_live_insights(
        raw_eeg=True,
        handler=lsl_stream_handler,
    )

    recording_task = asyncio.create_task(client.start_recording(recording_timer=RECORDING_TIMER))
    battery_task = asyncio.create_task(read_battery_30s(client))
    await recording_task
    await stop_task(battery_task)

if __name__ == "__main__":
    asyncio.run(main())


## OLD ##
    
    #experiment_task = asyncio.create_task(run_experiment())
    #await recording_task
    #await stop_task(battery_task)
    #await stop_task(experiment_task)