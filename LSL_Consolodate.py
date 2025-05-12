import os
import numpy as np
import mne
from mne_lsl.stream import StreamLSL
from mne_lsl.lsl import resolve_streams, StreamInlet
from bci_essentials.data_tank.data_tank import DataTank

# ------------------------ Setup ------------------------

subj = "AudP300_00XX"
directory = 'C:/Users/adamc/IDUN_Test'
subdir = os.path.join(directory, 'data')
os.makedirs(subdir, exist_ok=True)

idun_fif_path = os.path.join(subdir, f'eeg_data_{subj}_IDUN_raw.npy')
dsi_fif_path = os.path.join(subdir, f'eeg_data_{subj}_DSI_raw.npy')
marker_path = os.path.join(subdir, f'marker_data_{subj}.csv')


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

acq_delay = 0.01

idun = StreamLSL(name="IDUN", bufsize=60)  
dsi = StreamLSL(name="DSI-7", bufsize=60)

idun.connect(acquisition_delay=acq_delay)
dsi.connect(acquisition_delay=acq_delay)

marker_inlet = StreamInlet(marker_stream)

print("Streams connected.")

# ------------------------ Initialize Data Tank ------------------------
# Initialize DataTank instances for storing EEG data
idun_data_tank = DataTank() 
dsi_data_tank = DataTank()   

marker_samples, marker_timestamps = [], []
# ------------------------ Recording Loop ------------------------
print("Recording... press Ctrl+C or create 'stop_signal.txt' to stop.")

try:
    while True:
        # Break loop if stop file is detected
        if check_stop_signal():
            print("Stop signal file detected. Stopping recording...")
            break

        # IDUN - Get data and append to DataTank
        chunk1, ts1 = idun.get_data()
        if chunk1.size > 0:
            idun_data_tank.add_raw_eeg(chunk1, ts1)

        # DSI - Get data and append to DataTank
        chunk2, ts2 = dsi.get_data()
        if chunk2.size > 0:
            dsi_data_tank.add_raw_eeg(chunk2, ts2)

        # Marker - Get data and append to list
        sample, ts = marker_inlet.pull_sample(timeout=0.0)
        if sample is not None:
        # Make sure to check for a valid value
            if isinstance(sample, (list, np.ndarray)) and len(sample) > 0:
                marker_value = sample[0]
                marker_samples.append(marker_value)
                marker_timestamps.append(ts)

except KeyboardInterrupt:
    print("Recording stopped by user.")

# ------------------------ Data Saving  ------------------------
# Save IDUN EEG data and timestamps
idun_eeg = idun_data_tank.get_raw_eeg()
idun_timestamps = idun_data_tank._DataTank__raw_eeg_timestamps  # private attribute

idun_save_path = os.path.join(subdir, f"eeg_data_{subj}_IDUN.npy")
np.save(idun_save_path, {"eeg": idun_eeg, "timestamps": idun_timestamps})
print(f"Saved IDUN EEG data and timestamps to {idun_save_path}")

# Save DSI EEG data and timestamps
dsi_eeg = dsi_data_tank.get_raw_eeg()
dsi_timestamps = dsi_data_tank._DataTank__raw_eeg_timestamps  # private attribute

dsi_save_path = os.path.join(subdir, f"eeg_data_{subj}_DSI.npy")
np.save(dsi_save_path, {"eeg": dsi_eeg, "timestamps": dsi_timestamps})
print(f"Saved DSI EEG data and timestamps to {dsi_save_path}")

with open(os.path.join(subdir, f"marker_data_{subj}.csv"), "w") as f:
    for sample, ts in zip(marker_samples, marker_timestamps):
        if isinstance(sample, (list, np.ndarray)) and len(sample) > 0:
            # Extract the first element from the list/array
            sample = sample[0]
        f.write(f"{sample}, {ts}\n")