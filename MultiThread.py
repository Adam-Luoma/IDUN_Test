import threading
import subprocess
import time

"""
NOTES For Running the IDUN application:
Before you run this script make sure 
1) You have done an impedance check on the IDUN Web Browser App
2) You have updated your directory based on your computer in LSL_inlet.py
3) You have updated the subject identification in LSL_inlet.py
"""



def run_script(script_name):
    subprocess.run(["python", script_name])

if __name__ == "__main__":
    script1_thread = threading.Thread(target=run_script, args=("IDUN_Collect.py",))
    script2_thread = threading.Thread(target=run_script, args=("Frontend_AudP300.py",))
    #script2_thread = threading.Thread(target=run_script, args=("Frontend_VisP300.py",))
    #script2_thread = threading.Thread(target=run_script, args=("Frontend_ASSR.py",))
    #script2_thread = threading.Thread(target=run_script, args=("Frontend_SSVEP.py",))
    script3_thread = threading.Thread(target=run_script, args=("LSL_Consolodate.py",))
    #script3_thread = threading.Thread(target=run_script, args=("LSL_inlet_w_DSI.py",))

    script1_thread.start()
    script2_thread.start()
    # Wait for 10 seconds to allow the rest of the system to initialize
    print("Waiting for system to initialize...")
    time.sleep(15)
    print("Starting data collection...")
    script3_thread.start()

    script1_thread.join()
    script2_thread.join()
    script3_thread.join()

    print("All scripts have finished executing.")