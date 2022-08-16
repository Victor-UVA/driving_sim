# DRIVING SIM INSTRUCTIONS

## Powering On
1. Turn on MOOG computer at back of driving sim
2. Turn on Power Strip at front of driving sim
    a. Make sure all cables are plugged in
3. Turn on the Battery Enable Switch at front of driving sim
4. Plug in green 3 phase Power Cord

## Assetto Startup
1. Open Assetto and begin a race with desired car and track
2. Make sure to click the steering wheel at the top of the menu once it starts to begin

## Terminal Commands
1. Open a terminal, and navigate to ~/Desktop/"Assetto Corsa Shared Memory"
    a. In bash:
        ``` cd ~/Desktop/"Assetto Corsa Shared Memory" ```
    b. In powershell:
        ``` cd 'C:\Users\Drive Sim\Desktop\Assetto Corsa Shared Memory' ```
2. Run assetto_moog_control.py
    a. In bash:
        ``` python assetto_moog_control.py ```
    b. In powershell:
        ``` python .\assetto_moog_control.py ```
3. To kill in powershell run:
    ``` taskkill /F /IM python.exe ```

