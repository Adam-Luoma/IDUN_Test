from pylsl import resolve_stream, StreamInlet
import numpy as np
import os
import time

# Data storage
subj = "001"  # UPDATE WITH EACH PARTICIPANT
directory = 'C:/Users/Adam Luoma/BCI4Kids/IDUN_Test'  # CHANGE DEPENDING ON COMPUTER
subdir = os.path.join(directory, 'data')
eeg_path = os.path.join(subdir, f'eeg_data_{subj}.csv')

# Function to try resolving streams
def resolve_lsl_streams():
    print("Resolving EEG and Marker streams...")
    eeg_streams = resolve_stream('type', 'EEG')
    marker_streams = resolve_stream('type', 'Markers')
    return eeg_streams, marker_streams

# Initialize an empty list to store combined data
combined_data = []

# Attempt to resolve streams
eeg_streams, marker_streams = resolve_lsl_streams()

# If streams are found, create inlets
if eeg_streams and marker_streams:
    eeg_inlet = StreamInlet(eeg_streams[0])
    marker_inlet = StreamInlet(marker_streams[0])

# Flag to control the loop
    streams_active = True

    # Collect and combine data
    while streams_active:
        try:
            # Pull EEG data
            eeg_sample, eeg_timestamp = eeg_inlet.pull_sample(timeout=1.0)

            # Check if the EEG stream has ended
            if eeg_sample is None:
                print("EEG stream ended.")
                streams_active = False
                break

            # Pull Marker data (check with timeout to avoid blocking)
            marker_sample, marker_timestamp = marker_inlet.pull_sample(timeout=0.0)

            # Combine EEG and Marker into a single column
            if marker_sample and abs(marker_timestamp - eeg_timestamp) < 0.001:
                combined_sample = np.concatenate(([eeg_timestamp], eeg_sample, marker_sample))
            else:
                combined_sample = np.concatenate(([eeg_timestamp], eeg_sample, ['']))

            combined_data.append(combined_sample)

        except Exception as e:
            print(f"Error: {e}. Reconnecting...")
            time.sleep(2)  # Wait before attempting to reconnect
            eeg_streams, marker_streams = resolve_lsl_streams()
            if eeg_streams and marker_streams:
                eeg_inlet = StreamInlet(eeg_streams[0])
                marker_inlet = StreamInlet(marker_streams[0])
            else:
                print("Unable to reconnect. Ending data collection.")
                streams_active = False
                break

else:
    print("No streams found. Exiting.")

# Convert to NumPy array
combined_data = np.array(combined_data, dtype=object)   
    
# Convert to NumPy arrays and save as CSV
np.savetxt(eeg_path, combined_data, delimiter=',')
