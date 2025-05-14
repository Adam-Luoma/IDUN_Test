import os
import numpy as np
import mne
import time
from mne_lsl.stream import StreamLSL
from mne_lsl.lsl import resolve_streams, StreamInlet
from bci_essentials.data_tank.data_tank import DataTank

# ------------------------ Setup ------------------------

subj = "000X_ASSR"
directory = 'C:/Users/adamc/IDUN_Test'
subdir = os.path.join(directory, 'data')
os.makedirs(subdir, exist_ok=True)

idun_fif_path = os.path.join(subdir, f'eeg_data_{subj}_IDUN_raw.fif')
dsi_fif_path = os.path.join(subdir, f'eeg_data_{subj}_DSI_raw.fif')
marker_path = os.path.join(subdir, f'marker_data_{subj}.npy')


def check_stop_signal():
    """Check if the stop signal file exists."""
    return os.path.exists("stop_signal.txt")
# ------------------------ Stream Discovery ------------------------

print("Looking for EEG and marker streams...")
all_streams = resolve_streams()
print(all_streams)


def get_stream_by_name(streams, target_name):
    for stream in streams:
        if stream.name == target_name:
            return stream
    return None

idun_stream = get_stream_by_name(all_streams, "IDUN")
dsi_stream = get_stream_by_name(all_streams, "DSI-7")
marker_stream = get_stream_by_name(all_streams, "MarkerStream")

if not idun_stream or not dsi_stream or not marker_stream:
    print("Missing one or more required streams.")
    exit()


# ------------------------ Connect EEG Streams ------------------------

idun = StreamInlet(idun_stream)
dsi = StreamInlet(dsi_stream)
marker_inlet = StreamInlet(marker_stream)


# Wait for first samples
print("Waiting for first samples...")
idun.open_stream()
dsi.open_stream()

# Get initial sample to verify connection
test_chunk1, _ = idun.pull_sample()
test_chunk2, _ = dsi.pull_sample()
print(f"First IDUN sample shape: {test_chunk1.shape}")
print(f"First DSI sample shape: {test_chunk2.shape}")

# Initialize empty lists to store data
idun_data = []
idun_timestamps = []
dsi_data = []
dsi_timestamps = []
marker_samples = []
marker_timestamps = []

# ------------------------ Recording Loop ------------------------
print("Recording... press Ctrl+C to stop.")
start_time = time.time()
idun_last_timestamp = 0
dsi_last_timestamp = 0

idun_winsize = 250  # 1 second of data at 250 Hz
dsi_winsize = 300   # 1 second of data at 500 Hz

try:
    while True:
        # IDUN - Get data and append to lists
        chunk1, ts1 = idun.pull_chunk(max_samples=250)
        if chunk1.size > 0:
            # Transpose IDUN data to (1, samples) format
            chunk1 = chunk1.T
            
            if min(ts1) > idun_last_timestamp:
                idun_data.append(chunk1)
                idun_timestamps.extend(ts1)
                idun_last_timestamp = max(ts1)

        # DSI-7 - Get data and append to lists
        chunk2, ts2 = dsi.pull_chunk(max_samples=300)
        if chunk2.size > 0:
            # Transpose DSI data to (channels, samples) format
            chunk2 = chunk2.T
            
            if min(ts2) > dsi_last_timestamp:
                dsi_data.append(chunk2)
                dsi_timestamps.extend(ts2)
                dsi_last_timestamp = max(ts2)

        # Check for markers
        marker_chunk, marker_ts = marker_inlet.pull_chunk()
        if marker_chunk.size > 0:
            for sample, ts in zip(marker_chunk, marker_ts):
                # Store only non-zero markers
                if sample[0] != 0:
                    marker_samples.append(int(sample[0]))  # Convert to int and store first value
                    marker_timestamps.append(ts)

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Recording stopped.")

# ------------------------ Data Saving ------------------------
# Process and save IDUN Data
print("Processing IDUN data...")
idun_eeg = np.concatenate(idun_data, axis=1)
idun_timestamps = np.array(idun_timestamps)
idun_start_time = idun_timestamps[0]

# Create IDUN MNE object
sfreq = 250
ch_names = ['IDUN_EEG']
ch_types = ['eeg']
info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
idun_raw = mne.io.RawArray(idun_eeg, info)
idun_raw.save(idun_fif_path, overwrite=True)

# Process and save DSI Data
print("Processing DSI data...")
dsi_eeg = np.concatenate(dsi_data, axis=1)
dsi_timestamps = np.array(dsi_timestamps)
dsi_start_time = dsi_timestamps[0]

# Create DSI MNE object
dsi_sfreq = 300
dsi_ch_names = ['Fz', 'C3', 'Cz', 'C4', 'Pz', 'Po7', 'Po8']
dsi_ch_types = ['eeg'] * 7
dsi_info = mne.create_info(ch_names=dsi_ch_names, sfreq=dsi_sfreq, ch_types=dsi_ch_types)
dsi_raw = mne.io.RawArray(dsi_eeg, dsi_info)
dsi_raw.save(dsi_fif_path, overwrite=True)

# Save markers in a more structured format
# Save markers with relative timestamps
marker_timestamps = np.array(marker_timestamps)
marker_data = {
    'markers': np.array(marker_samples),
    'timestamps': marker_timestamps,
    'relative_to_idun': marker_timestamps - idun_start_time,
    'relative_to_dsi': marker_timestamps - dsi_start_time,
    'idun_start_time': idun_start_time,
    'dsi_start_time': dsi_start_time
}
np.save(marker_path, marker_data)

print(f"Saved IDUN data to {idun_fif_path}")
print(f"Saved DSI data to {dsi_fif_path}")
print(f"Saved marker data to {marker_path}")