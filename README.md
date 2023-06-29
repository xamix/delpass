# delpass
Code used to control Delpass panel

# Install Python3 libraries
`sudo pip install -r requirements.txt`

# If developping on Raspberry install one more library
`sudo pip install rpi_ws281x`

# Disable sound PWM:
Since this library and the onboard Raspberry Pi audio both use the PWM, they cannot be used together. You will need to blacklist the Broadcom audio kernel module by creating a file `/etc/modprobe.d/snd-blacklist.conf` with `blacklist snd_bcm2835`
