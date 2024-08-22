import asyncio
from pylsl import StreamInfo, StreamOutlet

from idun_guardian_sdk import GuardianClient

from psychopy import visual, sound, core, event as psychopy_event
import random

#initialize IDUN System
RECORDING_TIMER: int = (60 * 1)  # 60 sec * 1 min
my_api_token = "idun_GAtJDPZJ1bbs47Mf4KEBA3-v35iudqE3NSGSLD3OE8zE8KN2CHcN809-"
my_address = "E5-1E-FD-F5-15-26"

#initialize PsycoPy experiment parameters
sound_440Hz = sound.Sound("440Hz_tone.wav")
sound_587Hz = sound.Sound("587Hz_tone.wav")
num_blocks = 1                      #UPDATE to alter data collection length
target_sound_count_per_block = 2


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


async def run_experiment():
    await asyncio.sleep(15)
    # Setup PsychoPy window
    win = visual.Window([800, 600], color='black')
    fixation = visual.TextStim(win, text='+', color='white', height=0.1)
    block_text = visual.TextStim(win, text='', color='white', height=0.1, pos=(0, 0))

    for block in range(num_blocks):
        # Display block start message
        block_text.text = f"Starting Block {block + 1}. Press Enter to start."
        block_text.draw()
        win.flip()

       # Non-blocking key wait with asyncio loop
        start_block = False
        while not start_block:
            keys = psychopy_event.getKeys()
            if 'return' in keys:
                start_block = True
            elif 'escape' in keys:
                win.close()
                core.quit()

            await asyncio.sleep(0.01)  # Yield control to the asyncio event loop


        # Wait for Enter key to start the block
        #while True:
        #     keys = psychopy_event.waitKeys()
        #     if 'return' in keys:
        #         break
        #     elif 'escape' in keys:
        #         win.close()
        #         core.quit()

        # fixation.draw()
        # win.flip()

        # Block-specific task
        target_sound_count = 0
        while target_sound_count < target_sound_count_per_block:
            if 'escape' in psychopy_event.getKeys():
                win.close()
                core.quit()

            # Play standard sound
            standard_sound_count = random.randint(7, 12)
            for _ in range(standard_sound_count):
                sound_440Hz.play()
                #marker_outlet.push_sample([1])
                #markers.append(1)
                #marker_timestamps.append(core.getTime())

                core.wait(0.75)

                if 'escape' in psychopy_event.getKeys():
                    win.close()
                    core.quit()

            # Play target sound
            sound_587Hz.play()
            #marker_outlet.push_sample([2])
            target_sound_count += 1
            #markers.append(2)
            #marker_timestamps.append(core.getTime())

            core.wait(0.75)

            await asyncio.sleep(0.01)  # Yield control to the asyncio event loop

        print(f"Block {block + 1} completed")

    win.close()
    #core.quit()

async def collect_EEG(client):
    await client.start_recording(recording_timer=RECORDING_TIMER)

async def main():
    client = GuardianClient(api_token=my_api_token, address = my_address, debug=True)
    
    info = StreamInfo("IDUN", "EEG", 1, 250, "float32", client.address)
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

    #recording_task = asyncio.create_task(client.start_recording(recording_timer=RECORDING_TIMER))
    #battery_task = asyncio.create_task(read_battery_30s(client))
    #experiment_task = asyncio.create_task(run_experiment())
    #await recording_task
    #await stop_task(battery_task)
    #await stop_task(experiment_task)

    await asyncio.gather(
        collect_EEG(client),
        #run_experiment(),
        #read_battery_30s(client),
    )

if __name__ == "__main__":
    asyncio.run(main())