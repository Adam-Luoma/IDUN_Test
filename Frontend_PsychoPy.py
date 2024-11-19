from pylsl import StreamInfo, StreamOutlet, local_clock
from psychopy import visual, sound, core, event as psychopy_event
import random
import time

#initialize PsycoPy experiment parameters
sound_440Hz = sound.Sound("440Hz_tone.wav")
sound_587Hz = sound.Sound("587Hz_tone.wav")
num_blocks = 2                     #UPDATE to alter data collection length
target_sound_count_per_block = 2

#Map timing to Unix epoch
unix_offset = time.time() - local_clock()

marker_info = StreamInfo(name = 'MarkerStream', 
                         type = 'Markers', 
                         channel_count = 1, 
                         nominal_srate = 250,
                         channel_format='int32', 
                         source_id = 'Marker_Outlet')
marker_outlet = StreamOutlet(marker_info, 20, 360)

# Setup PsychoPy window
while True:
    win = visual.Window([800, 600], color='black')
    fixation = visual.TextStim(win, text='+', color='white', height=0.1)
    block_text = visual.TextStim(win, text='', color='white', height=0.1, pos=(0, 0))

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
                marker_1 = [1]
                timestamp = local_clock() + unix_offset
                marker_outlet.push_sample(marker_1, timestamp)

                core.wait(random.uniform(0.75,1.0))

                if 'escape' in psychopy_event.getKeys():
                    win.close()
                    core.quit()

            # Play target sound
            sound_587Hz.play()
            marker_2 = [2]
            timestamp = local_clock() + unix_offset
            marker_outlet.push_sample(marker_2, timestamp)
            target_sound_count += 1

            core.wait(random.uniform(0.75,1.0))

        print(f"Block {block + 1} completed")

    # After all blocks are complete, send the stop signal
    with open("stop_signal.txt", "w") as stop_file:
        stop_file.write("STOP")
    print("Stop signal sent.")

    win.close()
    core.quit()