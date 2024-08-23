from pylsl import StreamInfo, StreamOutlet
from psychopy import visual, sound, core, event as psychopy_event
import random


#initialize PsycoPy experiment parameters
sound_440Hz = sound.Sound("440Hz_tone.wav")
sound_587Hz = sound.Sound("587Hz_tone.wav")
num_blocks = 2                      #UPDATE to alter data collection length
target_sound_count_per_block = 3


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
                marker_outlet.push_sample([1])

                core.wait(0.75)

                if 'escape' in psychopy_event.getKeys():
                    win.close()
                    core.quit()

            # Play target sound
            sound_587Hz.play()
            marker_outlet.push_sample([2])
            target_sound_count += 1

            core.wait(0.75)

        print(f"Block {block + 1} completed")

    win.close()
    core.quit()