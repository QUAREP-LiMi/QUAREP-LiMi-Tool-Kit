# QUAREP-LiMi Tool Kit
Automation tools for microscope quality assessment.

The tool kit is a python script to start quality measurements, analyze them and show the results. \
It acts as a minimal glue between different existing solutions.

Version 0.2.21 is the latest release.\
https://github.com/QUAREP-LiMi/QUAREP-LiMi-Tool-Kit/releases \
This version was tested during the QUAREP workshops at ELMI 2024 in Manchester and at several Nikon systems.

The Tool Kit includes Nikon NIS-Elements macros. Support for other brands and measurements is in progress.
A python distribution is included, check out the comments in the main.py file to learn module requirements.

&nbsp;
## Installation
Install the .msi package or unpack the .zip archive to the microscope PC or a portable storage device.

&nbsp;
## Illuminator Power Linearity and Stability
The QUAREP-LiMi Tool Kit supports visualization of illumination power linearity and stability results on any microscope system. \
Macros for automatic measurements on Nikon microscope system are included in the tool kit. \
Scripts for Zeiss systems can be found here: https://github.com/QUAREP-LiMi/WG1-Automation/tree/main/Microscope_Systems. 

The Nikon NIS-Elements macro supports measuring the light with the camera or a Thorlabs Optical Power Meter (PM100A, PM100D, PM100USB, PM400). 
When connected to the power meter, the Thorlabs Temperature Probe reading will be recorded as wel.
The macro runs NIS-AR 5.2 or later. For NIS-BR the advanced interpreter license is required.
The macro should work with any multi-line light source controlled by NIS-Elements.
The light sources for the Nikon point-scan confocals are not supported.

Start the QUAREP-LiMi Tool Kit from the start menu (All Programs | QUAREP | QUAREP-LiMi Tool Kit) or double click the 'run.bat' file of the portable distribution.
On the 'Measure' page, select your microscope brand.\
When 'Nikon' is selected, you will be prompted to install the Nikon macros (including the Thorlabs power meter driver):

![image](https://github.com/QUAREP-LiMi/QUAREP-LiMi-Tool-Kit/assets/98902202/069e208c-423d-4d26-999f-f40ae0507597)

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

To start the Detector gain macro, press the big button with the lamp.

On the first dialog, you can enter information on the system and reason for the measurements:

<img alt="MDG_Info" src="https://github.com/user-attachments/assets/41280a44-efdd-402b-8524-bc2b05eeeefc">

The main dialog allows defining several tests. Press the 'Help' button to opens the instruction manual.

<img width="555" alt="MDG_Setup" src="https://github.com/user-attachments/assets/569679c5-3b38-48a0-bdc8-0b5aecd99a2d">

After the Dark and Bright image series are captured, the Tool Kit will automatically start the analysis and show the results:

<img width="1003" alt="QLTK_Detector" src="https://github.com/user-attachments/assets/a70a622f-204e-4c0d-9c5a-9bd85e1e0194">

