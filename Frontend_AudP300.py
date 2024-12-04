from pylsl import StreamInfo, StreamOutlet, local_clock
from psychopy import visual, sound, core, event as psychopy_event
import random
import time

# Initialize PsychoPy experiment parameters
sound_440Hz = sound.Sound("440Hz_tone.wav")
sound_523Hz = sound.Sound("523Hz_tone.wav")  # High note
sound_349Hz = sound.Sound("349Hz_tone.wav")  # Low note

num_blocks = 2  # UPDATE to alter data collection length
num_trials_per_block = 3
distractor_sound_count = 12

# Map timing to Unix epoch
unix_offset = time.time() - local_clock()

marker_info = StreamInfo(name='MarkerStream',
                         type='Markers',
                         channel_count=1,
                         nominal_srate=250,
                         channel_format='int32',
                         source_id='Marker_Outlet')
marker_outlet = StreamOutlet(marker_info, 20, 360)

# Setup PsychoPy window
while True:
    win = visual.Window([800, 600], color='black')
    fixation = visual.TextStim(win, text='+', color='white', height=0.1)
    block_text = visual.TextStim(win, text='', color='white', height=0.1, pos=(0, 0))

    for block in range(num_blocks):
        # Set target instructions based on block number
        if block % 2 == 0:  # Odd block
            target_instruction = "Listen for the high note."
            high_note_marker = 2
            low_note_marker = 3
        else:  # Even block
            target_instruction = "Listen for the low note."
            high_note_marker = 3
            low_note_marker = 2

        # Display block start message
        block_text.text = f"Starting Block {block + 1}. {target_instruction} Press Enter to start."
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

        # Perform the trials for the block
        for trial in range(num_trials_per_block):
            print(f"Starting Trial {trial + 1} of Block {block + 1}")

            # Prepare a list of 12 distractor sounds with targets randomly inserted
            sounds = ['440Hz'] * distractor_sound_count
            target_indices = random.sample(range(4, distractor_sound_count), 2)
            sounds[target_indices[0]] = '349Hz'
            sounds[target_indices[1]] = '523Hz'

            # Shuffle target placement independently
            random.shuffle(target_indices)

            # Play sounds in sequence
            for i, sound_type in enumerate(sounds):
                if sound_type == '440Hz':
                    sound_440Hz.play()
                    marker = [1]
                elif sound_type == '523Hz':
                    sound_523Hz.play()
                    marker = [high_note_marker]
                elif sound_type == '349Hz':
                    sound_349Hz.play()
                    marker = [low_note_marker]

                # Send LSL marker with timestamp
                timestamp = local_clock() + unix_offset
                marker_outlet.push_sample(marker, timestamp)

                core.wait(random.uniform(0.5, 0.75))

                if 'escape' in psychopy_event.getKeys():
                    win.close()
                    core.quit()

        print(f"Block {block + 1} completed")

    # After all blocks are complete, send the stop signal
    with open("stop_signal.txt", "w") as stop_file:
        stop_file.write("STOP")
    print("Stop signal sent.")

    win.close()
    core.quit()