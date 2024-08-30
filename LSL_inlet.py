from pylsl import resolve_stream, StreamInlet
import numpy as np
import os
import time

# Data storage
subj = "001"  # UPDATE WITH EACH PARTICIPANT
directory = 'C:/Users/Adam Luoma/BCI4Kids/IDUN_Test'  # CHANGE DEPENDING ON COMPUTER
subdir = os.path.join(directory, 'data')
eeg_path = os.path.join(subdir, f'eeg_data_{subj}.csv')
marker_path = os.path.join(subdir, f'marker_data_{subj}.csv')

# Function to try resolving streams
def resolve_lsl_streams():
    print("Resolving EEG and Marker streams...")
    eeg_streams = resolve_stream('type', 'EEG')
    marker_streams = resolve_stream('type', 'Markers')
    return eeg_streams, marker_streams

# Initialize an empty list to store combined data
eeg_samples = []
eeg_timestamps = []
marker_samples = []
marker_timestamps = []

# Attempt to resolve streams
eeg_streams, marker_streams = resolve_lsl_streams()

# If streams are found, create inlets
if eeg_streams and marker_streams:
    eeg_inlet = StreamInlet(eeg_streams[0])
    print("EEG stream successfully found")
    marker_inlet = StreamInlet(marker_streams[0])
    print("Marker stream successfully found")

# Flag to control the loop
    streams_active = True

    # Collect and combine data
    while streams_active:
        try:
            # Pull EEG data
            eeg_sample, eeg_timestamp = eeg_inlet.pull_sample(timeout=1.0)
            eeg_samples.append(eeg_sample)
            eeg_timestamps.append(eeg_timestamp)
            
            # Check if the EEG stream has ended
            if eeg_sample is None:
                print("EEG stream ended.")
                streams_active = False
                break

            # Pull Marker data (check with timeout to avoid blocking)
            marker_sample, marker_timestamp = marker_inlet.pull_sample(timeout=0.0)
            marker_samples.append(marker_sample)
            marker_timestamps.append(marker_timestamp)
            

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
    print("No streams found in LSL INLET SCRIPT Exiting.")

# Insert NaN for missing values
eeg_samples_clean = [np.nan if sample is None else sample for sample in eeg_samples]
eeg_timestamps_clean = [np.nan if sample is None else sample for sample in eeg_timestamps]
marker_samples_clean = [np.nan if sample is None else sample for sample in marker_samples]
marker_timestamps_clean = [np.nan if sample is None else sample for sample in marker_timestamps]

# Convert to NumPy array
eeg_samples_array = np.array(eeg_samples_clean)
eeg_timestamps_array = np.array(eeg_timestamps_clean)
marker_samples_array = np.array(marker_samples_clean)
marker_timestamps_array = np.array(marker_timestamps_clean)
    
eeg_data = np.vstack([eeg_samples_array, eeg_timestamps_array])
marker_data = np.vstack([marker_samples_array, marker_timestamps_array])

# Convert to NumPy arrays and save as CSV
np.savetxt(eeg_path, eeg_data, delimiter=',')
np.savetxt(marker_path, marker_data, delimiter=',')
