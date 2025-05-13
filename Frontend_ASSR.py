from pylsl import StreamInfo, StreamOutlet, local_clock
from psychopy import visual, sound, core, event as psychopy_event
import random

from psychopy import prefs
prefs.hardware['audioLib'] = ['Speakers (Realtek(R) Audio)']

# Initialize sounds
PL_SR = sound.Sound("Audio/PL_SR_cut.wav")
PR_SL = sound.Sound("Audio/PR_SL_cut.wav")

marker_info = StreamInfo(name='MarkerStream',
                         type='Markers',
                         channel_count=1,
                         nominal_srate=250,
                         channel_format='int32',
                         source_id='Marker_Outlet')
marker_outlet = StreamOutlet(marker_info, 20, 360)

# Trial parameters
num_blocks = 4 
num_trials = 10


# Setup PsychoPy window
while True:
    win = visual.Window([800, 600], color='black')
    fixation = visual.TextStim(win, text='+', color='white', height=0.1)
    block_text = visual.TextStim(win, text='', color='white', height=0.1, pos=(0, 0))

    for block in range(num_blocks):
        # Set target instructions based on block number, marker 1 = 38Hz target and 2 = 42Hz target
        if block % 2 == 0:  # Odd block
            target_instruction = "Listen for the melody in your left ear, ignore the melody in your right ear."
            PL_SR_marker = 1
            PR_SL_marker = 2
            
        else:  # Even block
            target_instruction = "Listen for the melody in your right ear, ignore the melody in your left ear."
            PL_SR_marker = 2
            PR_SL_marker = 1

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
        for trial in range(num_trials):
            print(f"Starting Trial {trial + 1} of Block {block + 1}")

            # Prepare a list of 5 trails
            order = random.choices([1, 2], k=1)

            # Play sounds in sequence
            for i in order:
                if i == 1:
                    marker = [PL_SR_marker]
                    timestamp = local_clock()
                    marker_outlet.push_sample(marker, timestamp)
                    PL_SR.play()
                    core.wait(20.0)
                    
                elif i == 2:
                    marker = [PR_SL_marker]
                    timestamp = local_clock()
                    marker_outlet.push_sample(marker, timestamp)
                    PR_SL.play()
                    core.wait(20.0)

                # 5-second blank screen break
                win.flip()
                core.wait(5.0)

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
