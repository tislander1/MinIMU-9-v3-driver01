# MinIMU-9-v3-driver01

Read data from MinIMU-9 v3 Gyro, Accelerometer, and Compass (Pololu branded)
This Python 2 program reads the data from an LSM303D and an L3GD20H which are both attached to the I2C bus of a Raspberry Pi.
Both can be purchased as a unit from Pololu as their MinIMU-9 v3 Gyro, Accelerometer, and Compass  product.

Follow the procedure to enable I2C on a Raspberry Pi:

- Add the lines "ic2-bcm2708" and "i2c-dev" to the file /etc/modules
- Comment out the line "blacklist ic2-bcm2708" (with a ) in the file /etc/modprobe.d/raspi-blacklist.conf
- Install I2C utility (including smbus) with the command "apt-get install python-smbus i2c-tools"
- Connect the I2C device to the SDA and SCL pins of the Raspberry Pi and detect it using the command "i2cdetect -y 1".  It should show up as 1D (typically) or 1E (if the jumper is set).
