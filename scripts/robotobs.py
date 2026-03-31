# Author: G. Pignata

import requests
#from bs4 import BeautifulSoup
import urllib3
from astropy.coordinates import EarthLocation, AltAz, get_sun
from astropy.time import Time
import astropy.units as u
from datetime import datetime, timezone
import time
import subprocess

sunlimit=-14 # This is the sun limit 

def sun_altitude(datetime_str):
    # These are the parameters for La Silla
    latitude_deg = -29.2567     # degrees
    longitude_deg = -70.7335     # degrees
    elevation_m = 2400        # meters

   # Define observatory location
    observatory = EarthLocation(lat=latitude_deg * u.deg,
                                lon=longitude_deg * u.deg,
                                height=elevation_m * u.m)

    # Time in UTC
    time = Time(datetime_str)

    # Sun position in AltAz
    altaz_frame = AltAz(obstime=time, location=observatory)
    sun_altaz = get_sun(time).transform_to(altaz_frame)

    return sun_altaz.alt.deg

if __name__ == "__main__":
    

    # ====================================================================
    # first loop to check the altitude of the sun to start observations

    while True:
        
        # Current UTC time
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")  # UTC
        sun_alt = sun_altitude(date)
        print(f"Sun altitude at {date} UTC = {sun_alt:.2f} degrees")
        print(date)
#        sun_alt=-19.0
        
        if sun_alt < sunlimit:

            try:
            	cmdDomeStatus = ["ntt_dome_status"]
            	resultDomeStatus = subprocess.run(cmdDomeStatus, capture_output=True, text=False)
            	stdoutDomeStatus = resultDomeStatus.stdout.decode("latin-1", errors="replace")
            	print("STDOUT:\n", stdoutDomeStatus)
            	DomeStatus = stdoutDomeStatus.split()
 
            	
            except subprocess.CalledProcessError as e:
            	print("Error when checking the dome status!")
            	print("Return code:", e.returncode)
            	print("STDOUT:\n", e.stdout)
            	print("STDERR:\n", e.stderr)
            	
            if DomeStatus[7] == "OPEN" or DomeStatus[8] == "OPEN":
            	print('Sun elevation below sunlimit and at least one dome open start observations!!')
            	break
                        
        time.sleep(60)
                	   
 ############################################################
 
# Start  questctl

#    try:        
#    	cmdStartQuestctl = ["start_questctl"]
#    	resultStartQuestctl = subprocess.run(cmdStartQuestctl, capture_output=True, text=False)
#    	stdoutStartQuestctl = resultStartQuestctl.stdout.decode("latin-1", errors="replace")  
#    	print("STDOUT:\n", stdoutStartQuestctl)
    	
#    except subprocess.CalledProcessError as e:
#    	print("Error when start questctl")
#    	print("Return code:", e.returncode)
#    	print("STDOUT:\n", e.stdout)
 
#==============================================================
    
    # open the dome
#    try:     
#    	print("Opening the dome. It will take 1.5 minutes")
#    	cmdOpenDome = ["opendome_raw"]
#    	resultOpenDome = subprocess.run(cmdOpenDome, capture_output=True, text=False)
#    	stdoutOpenDome = resultOpenDome.stdout.decode("latin-1", errors="replace")  
#    	print("STDOUT:\n", stdoutOpenDome)
#    	OpenDome = stdoutOpenDome.split()
#    	print('Schmidt Dome is:')
#    	print(OpenDome[3])
    	
#    except subprocess.CalledProcessError as e:
#    	print("Error when opening the dome")
#    	print("Return code:", e.returncode)
#    	print("STDOUT:\n", e.stdout)
#    	print("STDERR:\n", e.stderr) 
   	
#==============================================================

# Start obs_control 

#    try:
#    	print("Starting obs_control. It will take about ??? minutes")              
#    	cmdStartObsControl = ["obs_control_script", "start"]
#    	resultStartObsControl = subprocess.run(cmdStartObsControl, capture_output=True, text=False)
#    	stdoutStartObsControl = resultStartObsControl.stdout.decode("latin-1", errors="replace")  
#    	print("STDOUT:\n", stdoutStartObsControl)
    	
#    except subprocess.CalledProcessError as e:
#    	print("Error when starting obs_control")
#    	print("Return code:", e.returncode)
#    	print("STDOUT:\n", e.stdout)


##########################################################################
    
    while True:
        
        # Current UTC time
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")  # UTC
        sun_alt = sun_altitude(date)
        print(f"Sun altitude at {date} UTC = {sun_alt:.2f} degrees")
        print(date)
#        sun_alt=-12
        
        
        if sun_alt > sunlimit:
            print("Sun elevation above sun limit stop observations.")
            break
            
# ----------------------------------------------------------------------            
             # checking the NTT dome status 
        try:
            cmdDomeStatus = ["ntt_dome_status"]
            resultDomeStatus = subprocess.run(cmdDomeStatus, capture_output=True, text=False)
            stdoutDomeStatus = resultDomeStatus.stdout.decode("latin-1", errors="replace")  
            print("STDOUT:\n", stdoutDomeStatus)
            DomeStatus = stdoutDomeStatus.split()
            
#            DomeStatus[7]="CLOSE"
#            DomeStatus[8]="CLOSE"
            
        except subprocess.CalledProcessError as e:
            print("Error when checking the domes status!")
            print("Return code:", e.returncode)
            print("STDOUT:\n", e.stdout)
            
        stopobscode=0
        if DomeStatus[7] == "CLOSE" and DomeStatus[8] == "CLOSE":
            stopobscode=1
        			
            print('Two domes closed, stop observation and staw the telescope')
            try:
            	print("Stopping obs_control. It will take about ??? minutes")
            	cmdStopObsControl = ["obs_control_script", "stop"]
#            	resultStopObsControl = subprocess.run(cmdStopObsControl, capture_output=True, text=False)
#            	stdoutStopObsControl = resultStopObsControl.stdout.decode("latin-1", errors="replace")
#            	print("STDOUT:\n", stdoutStopObsControl)
            	
            except subprocess.CalledProcessError as e:
               	print("Error when starting obs_control")
               	print("Return code:", e.returncode)
               	print("STDOUT:\n", e.stdout)
               	
            try:
            	print("Stowing the Telescope. It will take about 3 minutes")
            	cmdStowTelescope = ["stow_telescope"]
            	#resultStowTelescope = subprocess.run(cmdStowTelescope, capture_output=True, text=False)
            	#stdoutStowTelescope = resultStowTelescope.stdout.decode("latin-1", errors="replace")
            	#print("STDOUT:\n", stdoutStowTelescope)
            	#stdoutStowTelescope = stdoutStowTelescope.split()
            	
            except subprocess.CalledProcessError as e:
            	print("Error when checking the dome status!")
            	print("Return code:", e.returncode)
            	print("STDOUT:\n", e.stdout)
            	print("STDERR:\n", e.stderr)
            	
        if (DomeStatus[7] == "OPEN" or DomeStatus[8] == "OPEN") and stopobscode==1:
        	print('Restarting Observations')

        print('obs code')
        print(stopobscode)   
            	
        print('keep Cheking')    	
        time.sleep(60)
        
###################################################################################        
# This is to close the dome

#    try:
#     	print("Closing the dome. It will take 1.5 minutes")  
#    	cmdCloseDome = ["closedome"]
#    	resultCloseDome = subprocess.run(cmdCloseDome, capture_output=True, text=False)
#    	stdoutCloseDome = resultCloseDome.stdout.decode("latin-1", errors="replace")  
#    	print("STDOUT:\n", stdoutCloseDome)
#    	CloseDome = stdoutCloseDome.split()
#    	print('Schmidt Dome is:')
#    	print(CloseDome[3])
    	
#    except subprocess.CalledProcessError as e:
#    	print("Error when checking the dome status!")
#    	print("Return code:", e.returncode)
#    	print("STDOUT:\n", e.stdout)
#    	print("STDERR:\n", e.stderr)

#==============================================================

# Final Stop obs_control 

    try:
    	print("Stopping obs_control. It will take about ??? minutes")      
#    	cmdStopObsControl = ["obs_control_script", "stop"]
#    	resultStopObsControl = subprocess.run(cmdStopObsControl, capture_output=True, text=False)
#    	stdoutStopObsControl = resultStopObsControl.stdout.decode("latin-1", errors="replace")  
#    	print("STDOUT:\n", stdoutStopObsControl)
    	
    except subprocess.CalledProcessError as e:
    	print("Error when starting obs_control")
#    	print("Return code:", e.returncode)
#    	print("STDOUT:\n", e.stdout)

     
#==============================================================

# Final Stow of the telescope

    try:     
    	print("Stowing the Telescope. It will take about 3 minutes")
#    	cmdStowTelescope = ["stow_telescope"]
#    	resultStowTelescope = subprocess.run(cmdStowTelescope, capture_output=True, text=False)
#    	stdoutStowTelescope = resultStowTelescope.stdout.decode("latin-1", errors="replace")  
#    	print("STDOUT:\n", stdoutStowTelescope)
#    	stdoutStowTelescope = stdoutStowTelescope.split()
    	
    except subprocess.CalledProcessError as e:
    	print("Error when checking the dome status!")
#    	print("Return code:", e.returncode)
#    	print("STDOUT:\n", e.stdout)
#    	print("STDERR:\n", e.stderr)


#==============================================================    

#  Stop questctl
 
    try:        
    	cmdStopQuestctl = ["stop_questctl"]
#    	resultStopQuestctl = subprocess.run(cmdStopQuestctl, capture_output=True, text=False)
#    	stdoutStopQuestctl = resultStopQuestctl.stdout.decode("latin-1", errors="replace")  
#    	print("STDOUT:\n", stdoutStopQuestctl)
    	
    except subprocess.CalledProcessError as e:
    	print("Error when checking the dome status!")
#    	print("Return code:", e.returncode)
#    	print("STDOUT:\n", e.stdout)
    
