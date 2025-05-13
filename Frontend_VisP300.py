import random
from pylsl import StreamInfo, StreamOutlet, local_clock
from psychopy import visual, core, event as psychopy_event

# === PARAMETERS ===
num_squares  = 9
num_blocks   = 4    # number of blocks (i.e. different targets)
num_repeats  = 20   # number of target appearances per block

marker_info = StreamInfo(name='MarkerStream',
                         type='Markers',
                         channel_count=1,
                         nominal_srate=250,
                         channel_format='string',
                         source_id='Marker_Outlet')
marker_outlet = StreamOutlet(marker_info, 20, 360)

# Map each square to a human‐readable name
square_labels = {
    0: "Top Left",    1: "Top Center", 2: "Top Right",
    3: "Middle Left", 4: "Center",     5: "Middle Right",
    6: "Bottom Left", 7: "Bottom Center", 8: "Bottom Right"
}

def start_window():
    window = visual.Window([800, 600], color='black')

    # --- START SCREEN & COUNTDOWN ---
    start_text = visual.TextStim(window, text="Press Enter to start",
                                 color='white', height=0.1, pos=(0, 0.85))
    start_text.draw(); window.flip()
    while True:
        keys = psychopy_event.waitKeys()
        if 'return' in keys:
            for i in (3,2,1):
                visual.TextStim(window, text=str(i),
                               color='white', height=0.1, pos=(0,0)).draw()
                window.flip(); core.wait(1)
            break
        elif 'escape' in keys:
            window.close(); core.quit()

    # --- PRE‐CREATE GRID SQUARES & LABELS ---
    positions = [(-0.5,  0.5), (0, 0.5), (0.5, 0.5),
                 (-0.5,   0),   (0,   0), (0.5,   0),
                 (-0.5, -0.5),  (0, -0.5), (0.5, -0.5)]
    squares = [visual.Rect(window, width=0.4, height=0.4,
                           pos=pos, fillColor='grey')
               for pos in positions]
    labels  = [visual.TextStim(window, text=chr(i+65),
                               color='white', height=0.1, pos=pos)
               for i, pos in enumerate(positions)]

    def draw_grid():
        for sq in squares: sq.draw()
        for lb in labels:  lb.draw()

    # --- BLOCK LOOP ---
    for block_num in range(num_blocks):
        check_close(window)

        # choose and show this block’s target
        target_index = random.randint(0, num_squares-1)
        target_name  = square_labels[target_index]
        visual.TextStim(window, text=f"TARGET: {target_name}",
                        color='yellow', height=0.1, pos=(0, 0)).draw()
        window.flip(); core.wait(2)

        # brief pause with the full grid
        draw_grid(); window.flip(); core.wait(1)


        # REPEAT FLASH‐CYCLES to get exactly `num_repeats` target‐flashes
        for rep in range(num_repeats):
            cycle = random.sample(range(num_squares), num_squares)
            for idx in cycle:
                check_close(window)

                # flash on
                squares[idx].fillColor = 'white'
                draw_grid(); window.flip()
                ts = local_clock()
                # 2 = target, 1 = non‐target
                marker = 2 if idx == target_index else 1
                marker_outlet.push_sample([str(marker)], ts)

                core.wait(0.1)

                # flash off
                squares[idx].fillColor = 'grey'
                draw_grid(); window.flip()
                core.wait(random.uniform(0.05, 0.2))

        print(f"Block #{block_num+1} done — target was \"{target_name}\" "
              f"({num_repeats} flashes)")

    # --- FINISH ---
    visual.TextStim(window, text="Finished", color='white',
                    height=0.1, pos=(0, 0)).draw()
    window.flip()
    with open("stop_signal.txt", "w") as f: f.write("STOP")
    print("Stop signal sent.")
    while True: check_close(window)


def check_close(window):
    if 'escape' in psychopy_event.getKeys():
        window.close(); core.quit()


if __name__ == "__main__":
    start_window()