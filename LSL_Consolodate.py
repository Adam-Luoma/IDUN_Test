import os
import numpy as np
import mne
from mne_lsl.stream import StreamLSL
from mne_lsl.lsl import resolve_streams, StreamInlet
from bci_essentials.data_tank import DataTank

# ------------------------ Setup ------------------------

subj = "AudP300_00XX"
directory = 'C:/Users/adamc/IDUN_Test'
subdir = os.path.join(directory, 'data')
os.makedirs(subdir, exist_ok=True)

idun_fif_path = os.path.join(subdir, f'eeg_data_{subj}_IDUN_raw.fif')
dsi_fif_path = os.path.join(subdir, f'eeg_data_{subj}_DSI_raw.fif')
marker_path = os.path.join(subdir, f'marker_data_{subj}.npy')

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

acq_delay = 0.01

idun = StreamLSL(name="IDUN", bufsize=60)  
dsi = StreamLSL(name="DSI-7", bufsize=60)

idun.connect(acquisition_delay=acq_delay)
dsi.connect(acquisition_delay=acq_delay)

marker_inlet = StreamInlet(marker_stream)

print("Streams connected.")

# ------------------------ Initialize Data Tank ------------------------
# Initialize DataTank instance for storing EEG data in a structured manner
idun_data_tank = DataTank(name="IDUN", data_path=subdir, n_channels=1, sample_rate=250)  # Replace with correct settings
dsi_data_tank = DataTank(name="DSI-7", data_path=subdir, n_channels=6, sample_rate=256)  # Replace with correct settings

marker_samples, marker_timestamps = [], []
# ------------------------ Recording Loop ------------------------

print("Recording... press Ctrl+C to stop.")

try:
    while True:
        # IDUN
        chunk1, ts1 = idun.get_data()
        if chunk1.size > 0:
            idun_data_tank.append_data(chunk1, ts1)  # Append data chunk to the DataTank

        # DSI
        chunk2, ts2 = dsi.get_data()
        if chunk2.size > 0:
            dsi_data_tank.append_data(chunk2, ts2)  # Append data chunk to the DataTank

        # Marker
        sample, ts = marker_inlet.pull_sample(timeout=0.0)
        if sample is not None:
            marker_samples.append(sample)
            marker_timestamps.append(ts)

except KeyboardInterrupt:
    print("Recording stopped.")

# Save IDUN and DSI data using DataTank's save functionality
idun_data_tank.save_data(idun_fif_path)
dsi_data_tank.save_data(dsi_fif_path)

# Save markers
np.save(marker_path, {"markers": marker_samples, "timestamps": marker_timestamps})
print(f"Saved markers to {marker_path}")
    
