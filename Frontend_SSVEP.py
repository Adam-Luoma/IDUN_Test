
from psychopy import visual, core, event as psychopy_event
import random
from pylsl import StreamInfo, StreamOutlet, local_clock

# Setup LSL outlet
marker_info = StreamInfo(name='MarkerStream',
                         type='Markers',
                         channel_count=1,
                         nominal_srate=250,
                         channel_format='int32',
                         source_id='Marker_Outlet')
marker_outlet = StreamOutlet(marker_info, 20, 360)


# Parameters
num_blocks = 8
num_trials = 10
trial_duration = 20  # seconds per trial
frame_rate = 60.0  # Your monitor's refresh rate

# Flicker settings
hz_left = 10  # 100ms cycle
hz_right = 12.5   # 80ms cycle
frame_interval = 1.0 / frame_rate

frames_per_cycle_left = int(round(frame_rate / hz_left))
frames_per_cycle_right = int(round(frame_rate / hz_right))

# Setup window and stimuli
win = visual.Window([800, 600], color='black', units='norm')
fixation = visual.TextStim(win, text='+', color='white', height=0.1)
block_text = visual.TextStim(win, text='', color='white', height=0.07)

square_left = visual.Rect(win, width=0.4, height=0.4, fillColor='white',
                          lineColor='white', pos=(-0.5, 0))
square_right = visual.Rect(win, width=0.4, height=0.4, fillColor='white',
                           lineColor='white', pos=(0.5, 0))


def flicker_both(duration_sec):
    total_frames = int(duration_sec * frame_rate)
    for frame in range(total_frames):
        draw_left = (frame % frames_per_cycle_left) < (frames_per_cycle_left / 2)
        draw_right = (frame % frames_per_cycle_right) < (frames_per_cycle_right / 2)

        if draw_left:
            square_left.draw()
        if draw_right:
            square_right.draw()
        fixation.draw()
        win.flip()

        if 'escape' in psychopy_event.getKeys():
            win.close()
            core.quit()

# Main experiment loop
while True:
    for block in range(num_blocks):
        if block % 2 == 0:
            target_instruction = "Attend to the LEFT flashing square. Ignore the right."
            attention_marker = 1
        else:
            target_instruction = "Attend to the RIGHT flashing square. Ignore the left."
            attention_marker = 2

        block_text.text = f"Starting Block {block + 1}\n{target_instruction}\nPress Enter to start."
        block_text.draw()
        win.flip()

        while True:
            keys = psychopy_event.waitKeys()
            if 'return' in keys:
                break
            elif 'escape' in keys:
                win.close()
                core.quit()

        fixation.draw()
        win.flip()
        core.wait(5.0)

        for trial in range(num_trials):
            print(f"Starting Trial {trial + 1} of Block {block + 1}")
            marker_outlet.push_sample([attention_marker], local_clock())                
            flicker_both(trial_duration)

            # 5-second blank screen break
            win.flip()
            core.wait(5.0)

            if 'escape' in psychopy_event.getKeys():
                win.close()
                core.quit()

        print(f"Block {block + 1} completed")

    with open("stop_signal.txt", "w") as stop_file:
        stop_file.write("STOP")
    print("Stop signal sent.")

    win.close()
    core.quit()