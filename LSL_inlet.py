from pylsl import resolve_stream, StreamInlet
import numpy as np
import os


# Global Configurations
subj = "001"  # UPDATE WITH EACH PARTICIPANT
directory = 'C:/Users/Adam Luoma/BCI4Kids/IDUN_Test'  # CHANGE DEPENDING ON COMPUTER
subdir = os.path.join(directory, 'data')
eeg_path = os.path.join(subdir, f'eeg_data_{subj}.csv')

# EEG Stream Info
eeg_stream = resolve_stream(name ="IDUN", type = "EEG", )
eeg_inlet = StreamInlet(eeg_stream[0])

# Marker Stream Info
marker_streams = resolve_stream(name = 'MarkerStream', type = 'Markers')
marker_inlet = StreamInlet(marker_streams[0])


# Collect data
combined_data = []

while True:
    # Collect EEG data
    eeg_sample, eeg_timestamp = eeg_inlet.pull_sample()

    if eeg_sample is None:
        print("EEG stream ended.")
        break

    # Collect Marker data (check with timeout to avoid blocking)
    marker_sample, marker_timestamp = marker_inlet.pull_sample(timeout=0.0)
    
    # Combine EEG and marker data into one dataframe
    if marker_sample and abs(marker_timestamp - eeg_timestamp) < 0.001:
        combined_sample = np.concatenate(([eeg_timestamp], eeg_sample, marker_sample))
    else:
        combined_sample = np.concatenate(([eeg_timestamp], eeg_sample, ['']))

    combined_data.append(combined_sample)
   
    if len(combined_data) > 1000000000:
        break

# Convert to NumPy array
combined_data = np.array(combined_data, dtype=object)   
    
# Convert to NumPy arrays and save as CSV
np.savetxt(eeg_path, combined_data, delimiter=',')