# Designing a «Digital Twin» of a Radio Telescope

## Application Instructions
These instructions explain how to start the Simulation and Analysis Tool for Radio Observations (SATRO). 
As a first step specific requirements need to be fullfiled.

### 1. Make sure you are meeting specific requirements
When not executing SATRO on the interal FHWN server (server1062.cs.technik.fhnw.ch) you need to make sure you fulfill specific requirements:

#### CASA
To run the SATRO application Common Astronomy Software Applications (CASA) needs to be installed on your operating system (only macOS and Linux).

https://casa.nrao.edu/casa_obtaining.shtml

CASA version 5.3.0-143 (Python 2.7) is sufficient for execution.

#### Python Packages
Those Python packages are required to be installed in your CASA distribution:

- matplotlib 2.2.5
- astropy 2.0.9
- pandas 0.24.2


### 2. Start CASA 
As a first step you need to start CASA from the console. The official documentation from CASA helps you to get started:

https://casa.nrao.edu/casadocs/casa-5.4.1/usingcasa

If you are using macOS following command can be executed directly in the console to start CASA:
```
/yourPathWhereCasaIsInstalled/CASA.app/Contents/MacOS/casa
```


### 3. Execute the script and start SATRO
After CASA has started go to this folder

dt_radio_telescope/SATRO

To simply start the application you have to enter
```
execfile('app_starter.py')
```

Afterwards the graphical user interface will appear and you are ready to simulate your radio observations.
On macOS there might be complications with displaying the user manual from the GUI.
More information about SATRO can be found in the user manual

dt_radio_telescope/SATRO/user_manual.pdf

