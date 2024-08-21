#!/usr/bin/env python
# coding: utf-8

import asyncio
import numpy as np
import random
from threading import Thread
from idun_guardian_sdk import GuardianClient
from psychopy import visual, sound, core, event as psychopy_event
from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream

# Create Subject ID
subj = "001"

# Load the sound from the WAV file
sound_440Hz = sound.Sound("440Hz_tone.wav")
sound_587Hz = sound.Sound("587Hz_tone.wav")

# Initialize IDUN Guardian
device_address = 'E5:1E:FD:F5:15:26'
api_token = "idun_GAtJDPZJ1bbs47Mf4KEBA3-v35iudqE3NSGSLD3OE8zE8KN2CHcN809-"
client = GuardianClient(address=device_address, api_token=api_token)
MAINS_FREQUENCY_60Hz = True
RECORDING_TIMER: int = 60 * 60 * 1  # 1 hour

# # Create lists to store the data
eeg_data = []
timestamps = []
markers = []
marker_timestamps = []


def print_impedance(data):
    print(f"{data}\tOhm")


def collect_eeg_data(inlet, data_list, timestamp_list):
    while True:
        sample, timestamp = inlet.pull_sample()
        data_list.append(sample)
        timestamp_list.append(timestamp)


if __name__ == "__main__":

    try:
        # Initialize LSL stream
        info = StreamInfo("IDUN", "EEG", 1, 250, "float32", client.address)
        lsl_outlet = StreamOutlet(info, 20, 360)

        battery_level = asyncio.run(client.check_battery())
        print("Battery Level: %s%%" % battery_level)
    
        try:
            # Run the stream_impedance function, limiting it to 20 seconds
            asyncio.wait_for(client.stream_impedance(handler=print_impedance), timeout=20.0)
        except asyncio.TimeoutError:
            print("Task took longer than 20 seconds and was cancelled.")


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

        asyncio.run(client.start_recording(recording_timer=RECORDING_TIMER))

        # # Set up the LSL stream for markers
        info = StreamInfo('MarkerStream', 'Markers', 1, 2, 'int32', 'myuidw43536')
        outlet = StreamOutlet(info)

        # Set up the window and fixation cross
        win = visual.Window([800, 600], color='black')
        fixation = visual.TextStim(win, text='+', color='white', height=0.1)
        block_text = visual.TextStim(win, text='', color='white', height=0.1, pos=(0, 0))

        # Resolve the EEG stream
        print("Looking for an EEG stream...")
        eeg_streams = resolve_stream('type', 'EEG')
        eeg_inlet = StreamInlet(eeg_streams[0])

        # # Resolve the Marker stream
        print("Looking for a Marker stream...")
        marker_streams = resolve_stream('type', 'Markers')
        marker_inlet = StreamInlet(marker_streams[0])

        # Start the EEG data collection in a separate thread
        eeg_thread = Thread(target=collect_eeg_data, args=(eeg_inlet, eeg_data, timestamps))
        eeg_thread.daemon = True  # Ensures the thread will close when the main program exits
        eeg_thread.start()

        # Number of blocks and target sounds per block
        num_blocks = 2
        target_sound_count_per_block = 30

        for block in range(num_blocks):
            # Display the block number
            block_text.text = f"Starting Block {block + 1}. Press Enter to start."
            block_text.draw()
            win.flip()

            # Wait for Enter key press to start the block
            while True:
                keys = psychopy_event.waitKeys()
                if 'return' in keys:  # Check if Enter key (Return) is pressed
                    break
                elif 'escape' in keys:  # Allow escape to quit before starting the block
                    win.close()
                    core.quit()

            fixation.draw()
            win.flip()

            # Counter for the target sound in each block
            target_sound_count = 0
            while target_sound_count < target_sound_count_per_block:
                # Check for escape key press
                if 'escape' in psychopy_event.getKeys():
                    win.close()
                    core.quit()

                # Play the standard sound
                standard_sound_count = random.randint(7, 12)
                for _ in range(standard_sound_count):
                    sound_440Hz.play()
                    outlet.push_sample([1])  # Send LSL marker for 440 Hz sound
                    markers.append(1)
                    marker_timestamps.append(core.getTime())  # Store the time when the marker was sent

                    core.wait(0.75)  # Wait for 0.75 second between sounds

                    # Check for escape key press
                    if 'escape' in psychopy_event.getKeys():
                        win.close()
                        core.quit()

                # Play the target sound
                sound_587Hz.play()
                outlet.push_sample([2])  # Send LSL marker for 587 Hz sound
                target_sound_count += 1
                markers.append(2)
                marker_timestamps.append(core.getTime())  # Store the time when the marker was sent

                core.wait(0.75)  # Wait for 0.75 second before the next sound

            # Block completed
            print(f"Block {block + 1} completed")

        win.close()
        core.quit()

        print("Data collection finished.")

    except KeyboardInterrupt:
        print("Experiment interrupted by User")
    finally:
        # Convert the lists to numpy arrays for further processing
        eeg_data = np.array(eeg_data)  # Shape: (num_samples, num_channels)
        timestamps = np.array(timestamps)  # Shape: (num_samples,)
        markers = np.array(markers)  # Shape: (num_markers,)
        marker_timestamps = np.array(marker_timestamps)  # Shape: (num_markers,)

        # Save the arrays as CSV files
        np.savetxt(f'BCI4Kids/data/IDUN_Pilot/eeg_data_{subj}A.csv', eeg_data, delimiter=',')
        np.savetxt(f'BCI4Kids/data/IDUN_Pilot/timestamps_{subj}A.csv', timestamps, delimiter=',')
        np.savetxt(f'BCI4Kids/data/IDUN_Pilot/markers_{subj}A.csv', markers, delimiter=',')
        np.savetxt(f'BCI4Kids/data/IDUN_Pilot/marker_timestamps_{subj}A.csv', marker_timestamps, delimiter=',')
