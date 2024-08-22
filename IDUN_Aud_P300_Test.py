#!/usr/bin/env python
# coding: utf-8

import asyncio
import numpy as np
import random
import os
from threading import Thread
from idun_guardian_sdk import GuardianClient
from psychopy import visual, sound, core, event as psychopy_event
from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream

# Global Configurations
subj = "001"  # UPDATE WITH EACH PARTICIPANT
directory = 'C:/Users/Students/source/repos/IDUN_Test/'  # CHANGE DEPENDING ON COMPUTER
subdir = os.path.join(directory, 'data')
eeg_path = os.path.join(subdir, f'eeg_data_{subj}A.csv')
timestamp_path = os.path.join(subdir, f'timestamps_{subj}A.csv')
marker_path = os.path.join(subdir, f'markers_{subj}A.csv')
marker_timestamps_path = os.path.join(subdir, f'marker_timestamps_{subj}A.csv')


# Load the sound from the WAV file
sound_440Hz = sound.Sound("440Hz_tone.wav")
sound_587Hz = sound.Sound("587Hz_tone.wav")

# Initialize IDUN Guardian
device_address = 'E5:1E:FD:F5:15:26'
api_token = "idun_GAtJDPZJ1bbs47Mf4KEBA3-v35iudqE3NSGSLD3OE8zE8KN2CHcN809-"
client = GuardianClient(address=device_address, api_token=api_token)
MAINS_FREQUENCY_60Hz = True
RECORDING_TIMER: int = (60 * 60 * 0.25)  # 15 min

# Create lists to store the data
eeg_data = []
timestamps = []
markers = []
marker_timestamps = []


async def start_recording():
    print("Starting recording...")
    await client.start_recording(recording_timer=RECORDING_TIMER)
    print("Recording finished.")



def collect_eeg_data(inlet, data_list, timestamp_list):
    while True:
        sample, timestamp = inlet.pull_sample()
        data_list.append(sample)
        timestamp_list.append(timestamp)


async def main():   
    # Initialize LSL stream for EEG
    info = StreamInfo("IDUN", "EEG", 1, 250, "float32", client.address)
    lsl_outlet = StreamOutlet(info, 20, 360)

    # LSL stream handler
    def lsl_stream_handler(event):
        message = event.message
        eeg = message["raw_eeg"]
        most_recent_ts = eeg[-1]["timestamp"]
        data = [sample["ch1"] for sample in eeg]
        lsl_outlet.push_chunk(data, most_recent_ts)

    client.subscribe_live_insights(raw_eeg=True, handler=lsl_stream_handler)

    # Set up the LSL stream for markers
    marker_info = StreamInfo('MarkerStream', 'Markers', 1, 2, 'int32', 'myuidw43536')
    marker_outlet = StreamOutlet(marker_info)

    battery_level = await client.check_battery()
    print(f"Battery Level: {battery_level}%")

    # Start recording in the background
    recording_task = asyncio.create_task(start_recording())

    # Setup PsychoPy window
    win = visual.Window([800, 600], color='black')
    fixation = visual.TextStim(win, text='+', color='white', height=0.1)
    block_text = visual.TextStim(win, text='', color='white', height=0.1, pos=(0, 0))

    # Resolve EEG and Marker streams
    print("Looking for an EEG stream...")
    eeg_streams = resolve_stream('type', 'EEG')
    eeg_inlet = StreamInlet(eeg_streams[0])

    print("Looking for a Marker stream...")
    marker_streams = resolve_stream('type', 'Markers')
    marker_inlet = StreamInlet(marker_streams[0])

    # Start EEG data collection in a separate thread
    eeg_thread = Thread(target=collect_eeg_data, args=(eeg_inlet, eeg_data, timestamps))
    eeg_thread.daemon = True  # Ensure the thread will close when the main program exits
    eeg_thread.start()

    # Experimental blocks
    num_blocks = 2
    target_sound_count_per_block = 30

    for block in range(num_blocks):
        # Display block start message
        block_text.text = f"Starting Block {block + 1}. Press Enter to start."
        block_text.draw()
        win.flip()

        # Wait for Enter key to start the block
        while True:
            keys = psychopy_event.waitKeys()
            if 'return' in keys:
                break
            elif 'escape' in keys:
                win.close()
                core.quit()

        fixation.draw()
        win.flip()

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
                marker_outlet.push_sample([1])
                markers.append(1)
                marker_timestamps.append(core.getTime())

                core.wait(0.75)

                if 'escape' in psychopy_event.getKeys():
                    win.close()
                    core.quit()

            # Play target sound
            sound_587Hz.play()
            marker_outlet.push_sample([2])
            target_sound_count += 1
            markers.append(2)
            marker_timestamps.append(core.getTime())

            core.wait(0.75)

        print(f"Block {block + 1} completed")

    win.close()
    core.quit()

    print("Data collection finished.")
    await recording_task



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Experiment interrupted by User")
    finally:
        # Save collected data
        eeg_data = np.array(eeg_data)
        timestamps = np.array(timestamps)
        markers = np.array(markers)
        marker_timestamps = np.array(marker_timestamps)

        np.savetxt(eeg_path, eeg_data, delimiter=',')
        np.savetxt(timestamp_path, timestamps, delimiter=',')
        np.savetxt(marker_path, markers, delimiter=',')
        np.savetxt(marker_timestamps_path, marker_timestamps, delimiter=',')