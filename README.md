# DRIVING SIM INSTRUCTIONS

## Powering On
### MOOG
1. Turn on MOOG computer at back of driving sim
2. Turn on Power Strip at front of driving sim
    1. Make sure all cables are plugged in
3. Turn on the Battery Enable Switch at front of driving sim
4. Plug in green 3 phase Power Cord
5. Ensure E-Stop is disengaged
### Other
1. Plug arduino into computer (labelled)
2. Turn on projectors with remote
    1. Should only have to press on button once
    2. Ensure that all projectors have successfully turned on


## Assetto Startup
1. Open Assetto and begin a race with desired car and track
    1. Click Main Menu
    2. Click Drive
    3. Select a car
    4. Select a track
    5. Change settings (manual, automatic, damage, etc.)
    6. Click Start Engine
2. Make sure to click the steering wheel at the top of the menu once it starts to begin

## Terminal Commands
1. Open a terminal, and navigate to ~/Desktop/"Assetto Corsa Shared Memory"
    1. In bash:
        ``` cd ~/Desktop/"Assetto Corsa Shared Memory" ```
    2. In powershell:
        ``` cd 'C:\Users\Drive Sim\Desktop\Assetto Corsa Shared Memory' ```
    3. This can also be done by opening the VS Code folder
2. Run assetto_moog_control.py
    1. In bash:
        ``` python assetto_moog_control.py ```
    2. In powershell:
        ``` python .\assetto_moog_control.py ```
3. To kill in powershell run:
    ``` taskkill /F /IM python.exe ```
    1. You will need to run this before restarting teh code if the base faults (as in an ESTOP)

