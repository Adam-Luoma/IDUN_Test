import numpy as np
import os
from mne_lsl.stream import StreamLSL
from pylsl import resolve_stream, StreamInlet

# Participant and path setup
subj = "AudP300_00XX"  # UPDATE WITH EACH PARTICIPANT
directory = 'C:/Users/Adam Luoma/BCI4Kids/IDUN_Test'
subdir = os.path.join(directory, 'data')
eeg_path = os.path.join(subdir, f'eeg_data_{subj}.npy')
DSI_path = os.path.join(subdir, f'DSI_data_{subj}.npy')
marker_path = os.path.join(subdir, f'marker_data_{subj}.npy')

# Resolve streams
# Resolve streams
print("Looking for EEG and marker streams...")
all_streams = resolve_stream()

# Print all stream names to help you debug
for stream in all_streams:
    print(f"Found stream: {stream.name()}")

# Helper to get stream by name
def get_stream_by_name(streams, target_name):
    for stream in streams:
        if stream.name() == target_name:
            return stream
    return None

# Assign streams explicitly
idun_stream = get_stream_by_name(all_streams, "IDUN")  # Replace with exact name if needed
dsi_stream = get_stream_by_name(all_streams, "DSI-7")  # Replace with exact name if needed
marker_stream = get_stream_by_name(all_streams, "MarkerStream")

# Check streams
if not idun_stream or not dsi_stream or not marker_stream:
    print("Could not find all required streams. Found:")
    print(f"  IDUN_Guardian: {bool(idun_stream)}")
    print(f"  DSI-7: {bool(dsi_stream)}")
    print(f"  Markers: {bool(marker_stream)}")
    exit()

# Connect to EEG streams
eeg1 = StreamLSL(bufsize=1000, name="IDUN", channel_names=["ch1"], channel_types=["EEG"])
eeg2 = StreamLSL(bufsize=1000, name="DSI-7")

# The connection should explicitly reference the resolved streams with acquisition_delay
acq_delay = 0.01 

# The connection should explicitly reference the resolved streams
eeg1.connect(acquisition_delay = acq_delay)
eeg2.connect(acquisition_delay= acq_delay)

# Marker stream (via pylsl)
marker_inlet = StreamInlet(marker_stream)

print("Streams connected successfully.")

# Storage variables
eeg1_samples, eeg1_timestamps = [], []
eeg2_samples, eeg2_timestamps = [], []
marker_samples, marker_timestamps = [], []

# Set batch size and save interval
SAVE_INTERVAL = 1000  # Save data every 1000 samples

print("Starting data collection. Press Ctrl+C to stop.")
try:
    while True:
        # EEG1 (IDUN)
        data1, timestamps1 = eeg1.get_data()
        if data1.size > 0:
            eeg1_samples.append(data1.T)
            eeg1_timestamps.extend(timestamps1)

        # EEG2 (DSI)
        data2, timestamps2 = eeg2.get_data()
        if data2.size > 0:
            eeg2_samples.append(data2.T)
            eeg2_timestamps.extend(timestamps2)

        # Marker
        marker_sample, marker_timestamp = marker_inlet.pull_sample(timeout=0.0)
        if marker_sample is not None:
            marker_samples.append(marker_sample)
            marker_timestamps.append(marker_timestamp)

        # Save data periodically to prevent memory overload
        if len(eeg1_timestamps) >= SAVE_INTERVAL:
            # Save EEG1 (IDUN) data to .npy
            eeg1_array = np.vstack(eeg1_samples)
            eeg1_time_array = np.array(eeg1_timestamps[:len(eeg1_array)])
            eeg1_data_matrix = np.column_stack((eeg1_array, eeg1_time_array))
            np.save(eeg_path, eeg1_data_matrix)

            # Clear the lists after saving
            eeg1_samples.clear()
            eeg1_timestamps.clear()

            # Save EEG2 (DSI) data to .npy
            eeg2_array = np.vstack(eeg2_samples)
            eeg2_time_array = np.array(eeg2_timestamps[:len(eeg2_array)])
            eeg2_data_matrix = np.column_stack((eeg2_array, eeg2_time_array))
            np.save(DSI_path, eeg2_data_matrix)

            # Clear the lists after saving
            eeg2_samples.clear()
            eeg2_timestamps.clear()

except KeyboardInterrupt:
    print("Data collection stopped by user.")

# # Save EEG1 (IDUN)
# eeg1_array = np.vstack(eeg1_samples)
# eeg1_time_array = np.array(eeg1_timestamps[:len(eeg1_array)])
# eeg1_data_matrix = np.column_stack((eeg1_array, eeg1_time_array))
# np.savetxt(eeg_path, eeg1_data_matrix, delimiter=',')

# # Save EEG2 (DSI)
# eeg2_array = np.vstack(eeg2_samples)
# eeg2_time_array = np.array(eeg2_timestamps[:len(eeg2_array)])
# eeg2_data_matrix = np.column_stack((eeg2_array, eeg2_time_array))
# np.savetxt(DSI_path, eeg2_data_matrix, delimiter=',')

# # Save filtered markers
# filtered = [
#     (s[0], t) for s, t in zip(marker_samples, marker_timestamps)
#     if s is not None and isinstance(s, list) and s[0] in [1, 2]
# ]

# if filtered:
#     marker_vals, marker_times = zip(*filtered)
#     marker_data = np.column_stack((marker_vals, marker_times))
#     np.savetxt(marker_path, marker_data, delimiter=',')
# else:
#     print("No valid markers [1] or [2] found.")

    
