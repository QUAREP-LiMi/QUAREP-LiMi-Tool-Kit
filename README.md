# QUAREP-LiMi Tool Kit
Automation tools for microscope quality assessment.

The tool kit is a python script to start quality measurements, analyze them and show the results. \
It acts as a minimal glue between different existing solutions.

Version 0.3.31 is the latest release: https://github.com/QUAREP-LiMi/QUAREP-LiMi-Tool-Kit/releases \
Version 28 was tested during the QUAREP workshops at ELMI 2024, 2025 and at several Nikon systems. \
Version 29 includes new features that were presented during ELMI 2026.

The Tool Kit includes Nikon NIS-Elements macros. Support for other brands and measurements is in progress.
A python distribution is included, check out the comments in the main.py file to learn module requirements.

&nbsp;
## Get notified when a new version is released
To receive a notification when a new release is published, press the Watch dropdown button, select Custom and check the 'Releases' option:

<img width="358" height="515" alt="Github_Notifications" src="https://github.com/user-attachments/assets/bb6541ad-bb52-4df5-9c54-c2500172053e" />

&nbsp;
## Installation
Install the .msi package or unpack the .zip archive to the microscope PC or a portable storage device. \
Start the QUAREP-LiMi Tool Kit from the start menu (All Programs | QUAREP | QUAREP-LiMi Tool Kit) or double click the 'run.bat' file of the portable distribution.
On the 'Measure' page, select your microscope brand.\
When 'Nikon' is selected, you will be prompted to install the Nikon macros (including the Thorlabs power meter driver):

<img width="523" height="382" alt="msr_0" src="https://github.com/user-attachments/assets/b9fb0be1-1cbf-40b5-bf7d-bc88cc5bb92b" />

_**Microsoft Visual C++ Redistributables Package Setup Failed**_  
The installation of the Nikon macros is implemented in a simple window batch file that might stumble on details: \
The **Microsoft Visual C++ Redistributables Package** installation fails when a newer (and better) version is already installed. \
Unfortunately, the message "Setup failed" is not informing you on that. You can just dismiss this error dialog.

_**NIS macro error cannot evaluate error**_  
You will run into this problem when NIS is not installed in the standard folder C:\Program Files\NIS-Elements, or when the NIS installation was modified and reverted some libraries back to older versions.
When you encounter the **cannot evaluate** error please re-install the macro files by selection the 'Nikon' brand again on the 'measure' page.
If that does not help, copy the files manually to the correct location:
- Locate the two .zip files in de folder c:\program files\quarep-limi\quarep limi toolkit\macros.
  The structure in these files matches the structure on how to should end up in the C:\ drive.
- Stop NIS-Elements.
- Unpack the .zip files to some temporary folder.
- Drag the 'Program Files' folder in the root of the zip file to the C:\ drive.
  This assumes NIS is installed in c:\program files\nis-elements.
  If NIS is installed at a different location, you have to select all files in the zip file folder "~\Program Files\NIS-Elements" and drag them to the NIS installation folder.

&nbsp;
## Illuminator Power Linearity and Stability
The QUAREP-LiMi Tool Kit supports visualization of illumination power linearity and stability results on any microscope system. \
There are three tools to measure the power automatically.

_**SmartLPM**_  
The 'SmartLPM' tool included in the toolkit can be used to track the power off any automated microscope using a Thorlabs power meter. \
The SmartLPM tool can be started by pressing the SmartLPM button on the Measure page. \
Instructions are found on the SmartLPM repository: https://github.com/QUAREP-LiMi/SmartLPM.

_**Zeiss scripts**_  
Scripts for Zeiss systems can be found here: https://github.com/QUAREP-LiMi/WG1-Automation/tree/main/Microscope_Systems. \

_**Nikon NIS-Elements MeasurePowerStability.mac**_  
The Nikon NIS-Elements macro supports measuring the light with the camera or a Thorlabs Optical Power Meter (PM100A, PM100D, PM100USB, PM400). 
When connected to the power meter, the Thorlabs Temperature Probe reading will be recorded as wel.
The macro runs NIS-AR 5.2 or later. For NIS-BR the advanced interpreter license is required.
The macro should work with any multi-line light source controlled by NIS-Elements.
The light sources for the Nikon point-scan confocals are not supported.

To start the illumination power linearity and stability measurements macro, press the big button with the lamp.

The first time, press the 'Settings' button and fill in the details of your light source, such as the brand, model en serial number:

![QLTK_settings](https://github.com/QUAREP-LiMi/QUAREP-LiMi-Tool-Kit/assets/98902202/5d999dd3-26d4-47d9-b781-e1abdec55a2b)

Next, connect and power your power meter and press the 'Meter' button to check the connection:

![QLTK_meter](https://github.com/QUAREP-LiMi/QUAREP-LiMi-Tool-Kit/assets/98902202/aea9da5a-cb09-4f1d-b394-9d4f5d51b3c2)

The main macro dialog show the protocol settings on the left.\
Configure them as desired.\
On the right all light source lines are listed.\
Create an OC for each line and set the desired powers for the 'low power' and 'high power' measurements:

![QLTK_macro](https://github.com/QUAREP-LiMi/QUAREP-LiMi-Tool-Kit/assets/98902202/a29f1bee-7a9e-4cf8-9365-3157df4fe60a)

Finally, press the 'Start' button to start the measurement.\
Enter the measurement details in the 'Information' dialog and press 'Start' to really start:

![QLTK_info](https://github.com/QUAREP-LiMi/QUAREP-LiMi-Tool-Kit/assets/98902202/9a327c28-cc2c-486d-abcf-baf457fe4ef7)

A progress dialog will show the activity and last measured power:

![QLTK_progress](https://github.com/QUAREP-LiMi/QUAREP-LiMi-Tool-Kit/assets/98902202/96a50d0d-bf54-413f-8ecd-34e3c97bc4a6)

The QUAREP-LiMi Tool Kit 'Browse Results' page will be activated.
The first time, enter the location of the measurement results (defaults to c:\QUAREP).
On the left top panel, all illuminators are listed.
The left bottom panel shows the dates for which measurements are available.
The right hand panel shows the measurements results.
Use the buttons on the top to filter for which lines or protocols the results are shown.
The information panel can be edited to add extra information.

![QLTK_Results](https://github.com/QUAREP-LiMi/QUAREP-LiMi-Tool-Kit/assets/98902202/d4281b29-8053-473f-a40d-1961eb7ddab8)

&nbsp;
## Detector Photo Conversion Factor (gain), Capacity, Read-Noise
The QUAREP-LiMi Tool Kit includes the [analysis tool for inhomogeneous illumination](https://github.com/mcfaddendavid/betalight-calibration/releases) from David McFadden to calculate the detector photo conversion factor, capacity, read-noise and other detector quality parameters. 
A macro for Nikon NIS-Elements is included to capture the required images.

_**Nikon NIS-Elements MeasureDetectorGain.mac**_  
To start the Detector gain macro, press the big button with the lamp.

On the first dialog, you can enter information on the system and reason for the measurements:

<img alt="MDG_Info" src="https://github.com/user-attachments/assets/41280a44-efdd-402b-8524-bc2b05eeeefc">

The main dialog allows defining several tests. Press the 'Help' button to opens the instruction manual.

<img width="555" alt="MDG_Setup" src="https://github.com/user-attachments/assets/569679c5-3b38-48a0-bdc8-0b5aecd99a2d">

After the Dark and Bright image series are captured, the Tool Kit will automatically start the analysis and show the results:

<img width="1003" alt="QLTK_Detector" src="https://github.com/user-attachments/assets/a70a622f-204e-4c0d-9c5a-9bd85e1e0194">

&nbsp;
## Stage Repeatability 
Version 29 includes the NIS-Elements macros to run the QUAREP Working Group 6 published protocol to assess stage repeatability.

_**Nikon NIS-Elements MeasureStageRepeatability.mac**_  
This macro guides you through the capture of the QUAREP-LiMi protocol for stage repeatiblity.
After the experiment, the images will be thresholded (there must be only one spot in the FOV),
the position of the tracking mark is recorded and the standard deviation of the positions is calculated.

Press the big button with the arrows to start the macro.
The macro prompts for the following parameters:
<img width="644" height="273" alt="msr_1" src="https://github.com/user-attachments/assets/7a43d637-54fa-41bb-b0d8-4287f3087344" /> 

The results will be shown separately for X,Y, direction and shift distance:
<img width="782" height="791" alt="msr_2" src="https://github.com/user-attachments/assets/1304311e-48a6-4722-a937-61d7f257d9af" />

The QUAREP-LiMi Tool Kit Browse page will show the results of all tests in a table.
It results that exceed the warning limit are highlighted in red.
 <img width="1486" height="237" alt="msr_3" src="https://github.com/user-attachments/assets/2295b9cd-982b-4fb8-8815-8888c29bb045" />

