# delpass
Code used to control Delpass panel

# Install Python3 libraries
`sudo pip install -r requirements.txt`

# If developping on Raspberry install one more library
`sudo pip install rpi_ws281x`

# Disable sound PWM:
Comment the folowing line in `/boot/config.txt`:
`dtparam=audio=on`
