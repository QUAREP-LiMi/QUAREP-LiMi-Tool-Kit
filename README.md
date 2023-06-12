# QUAREP-LiMi Tool Kit
Automation tools for microscope quality assessment.

The tool kit is a python script to start quality measurements, analyze them and show the results.

Version 0.1.14 is the first release.\
https://github.com/QUAREP-LiMi/QUAREP-LiMi-Tool-Kit/releases \
This version was tested during the QUAREP workshops at ELMI 2023 in the Netherlands.

Version 0.1.14 supports measuring and visualization of illumination power linearity and stability on  Nikon microscope system.\
Requirements:
- Thorlabs power meter + optional thermometer
- NIS-AR or NIS-BR + advanced interpreter license
- Nikon point-scan confocal is not (yet) supported

Support for other brands and measurements is in progress.

## Installation
Install the package or unpack the archive to the microscope PC or a portable storage device.

## Usage
Start the script from the start menu (All Programs | QUAREP | QUAREP-LiMi Tool Kit) or double click the 'run.bat' file of the portable distribution.
On the 'Measure' page, select your microscope brand.\
When 'Nikon' is selected, you will be prompted to install the Nikon macros (including the Thorlabs power meter driver):

![QLTK_measure](https://github.com/QUAREP-LiMi/QUAREP-LiMi-Tool-Kit/assets/98902202/7058b946-c6f4-4942-8b5a-5566d2b9ddb8)

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


