from pylsl import resolve_stream, StreamInlet
import numpy as np
import os

from idun_guardian_sdk import GuardianClient

# Global Configurations
subj = "001"  # UPDATE WITH EACH PARTICIPANT
directory = 'C:/Users/Students/source/repos/IDUN_Test/'  # CHANGE DEPENDING ON COMPUTER
subdir = os.path.join(directory, 'data')
eeg_path = os.path.join(subdir, f'eeg_data_{subj}.csv')

# Initialize IDUN
my_api_token = "idun_GAtJDPZJ1bbs47Mf4KEBA3-v35iudqE3NSGSLD3OE8zE8KN2CHcN809-"
my_address = "E5-1E-FD-F5-15-26"
client = GuardianClient(api_token=my_api_token, address = my_address)

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