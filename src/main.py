#This Python 2 program reads the data from an LSM303D and an L3GD20H which are both attached to the I2C bus of a Raspberry Pi.
#Both can be purchased as a unit from Pololu as their MinIMU-9 v3 Gyro, Accelerometer, and Compass  product.
#
#First follow the procedure to enable I2C on R-Pi.
#1. Add the lines "ic2-bcm2708" and "i2c-dev" to the file /etc/modules
#2. Comment out the line "blacklist ic2-bcm2708" (with a #) in the file /etc/modprobe.d/raspi-blacklist.conf
#3. Install I2C utility (including smbus) with the command "apt-get install python-smbus i2c-tools"
#4. Connect the I2C device to the SDA and SCL pins of the Raspberry Pi and detect it using the command "i2cdetect -y 1".  It should show up as 1D (typically) or 1E (if the jumper is set).

import time, math

def twos_comp_combine(msb, lsb):
    twos_comp = 256*msb + lsb
    if twos_comp >= 32768:
        return twos_comp - 65536
    else:
        return twos_comp

from smbus import SMBus
busNum = 1
b = SMBus(busNum)

## LSM303D Registers --------------------------------------------------------------
LSM = 0x1d #Device I2C slave address

LSM_WHOAMI_ADDRESS = 0x0F
LSM_WHOAMI_CONTENTS = 0b1001001 #Device self-id

#Control register addresses -- from LSM303D datasheet

LSM_CTRL_0 = 0x1F #General settings
LSM_CTRL_1 = 0x20 #Turns on accelerometer and configures data rate
LSM_CTRL_2 = 0x21 #Self test accelerometer, anti-aliasing accel filter
LSM_CTRL_3 = 0x22 #Interrupts
LSM_CTRL_4 = 0x23 #Interrupts
LSM_CTRL_5 = 0x24 #Turns on temperature sensor
LSM_CTRL_6 = 0x25 #Magnetic resolution selection, data rate config
LSM_CTRL_7 = 0x26 #Turns on magnetometer and adjusts mode

#Registers holding twos-complemented MSB and LSB of magnetometer readings -- from LSM303D datasheet
LSM_MAG_X_LSB = 0x08 # x
LSM_MAG_X_MSB = 0x09
LSM_MAG_Y_LSB = 0x0A # y
LSM_MAG_Y_MSB = 0x0B
LSM_MAG_Z_LSB = 0x0C # z
LSM_MAG_Z_MSB = 0x0D

#Registers holding twos-complemented MSB and LSB of magnetometer readings -- from LSM303D datasheet
LSM_ACC_X_LSB = 0x28 # x
LSM_ACC_X_MSB = 0x29
LSM_ACC_Y_LSB = 0x2A # y
LSM_ACC_Y_MSB = 0x2B
LSM_ACC_Z_LSB = 0x2C # z
LSM_ACC_Z_MSB = 0x2D

#Registers holding 12-bit right justified, twos-complemented temperature data -- from LSM303D datasheet
LSM_TEMP_MSB = 0x05
LSM_TEMP_LSB = 0x06

# L3GD20H registers ----------------------------------------------------

LGD = 0x6b #Device I2C slave address
LGD_WHOAMI_ADDRESS = 0x0F
LGD_WHOAMI_CONTENTS = 0b11010111 #Device self-id

LGD_CTRL_1 = 0x20 #turns on gyro
LGD_CTRL_2 = 0x21 #can set a high-pass filter for gyro
LGD_CTRL_3 = 0x22
LGD_CTRL_4 = 0x23
LGD_CTRL_5 = 0x24
LGD_CTRL_6 = 0x25

LGD_TEMP = 0x26

#Registers holding gyroscope readings
LGD_GYRO_X_LSB = 0x28
LGD_GYRO_X_MSB = 0x29
LGD_GYRO_Y_LSB = 0x2A
LGD_GYRO_Y_MSB = 0x2B
LGD_GYRO_Z_LSB = 0x2C
LGD_GYRO_Z_MSB = 0x2D

#Ensure chip is detected properly on the bus ----------------------


if b.read_byte_data(LSM, LSM_WHOAMI_ADDRESS) == LSM_WHOAMI_CONTENTS:
    print 'LSM303D detected successfully on I2C bus '+str(busNum)+'.'
else:
    print 'No LSM303D detected on bus on I2C bus '+str(busNum)+'.'

if b.read_byte_data(LGD, LGD_WHOAMI_ADDRESS) == LGD_WHOAMI_CONTENTS:
    print 'L3GD20H detected successfully on I2C bus '+str(busNum)+'.'
else:
    print 'No L3GD20H detected on bus on I2C bus '+str(busNum)+'.'

#Set up the chips for reading  ----------------------
    
b.write_byte_data(LSM, LSM_CTRL_1, 0b1010111) # enable accelerometer, 50 hz sampling
b.write_byte_data(LSM, LSM_CTRL_2, 0x00) #set +/- 2g full scale
b.write_byte_data(LSM, LSM_CTRL_5, 0b01100100) #high resolution mode, thermometer off, 6.25hz ODR
b.write_byte_data(LSM, LSM_CTRL_6, 0b00100000) # set +/- 4 gauss full scale
b.write_byte_data(LSM, LSM_CTRL_7, 0x00) #get magnetometer out of low power mode

b.write_byte_data(LGD, LGD_CTRL_1, 0x0F) #turn on gyro and set to normal mode

#Read data from the chips ----------------------

while True:
    time.sleep(0.5)
    magx = twos_comp_combine(b.read_byte_data(LSM, LSM_MAG_X_MSB), b.read_byte_data(LSM, LSM_MAG_X_LSB))
    magy = twos_comp_combine(b.read_byte_data(LSM, LSM_MAG_Y_MSB), b.read_byte_data(LSM, LSM_MAG_Y_LSB))
    magz = twos_comp_combine(b.read_byte_data(LSM, LSM_MAG_Z_MSB), b.read_byte_data(LSM, LSM_MAG_Z_LSB))
    
    accx = twos_comp_combine(b.read_byte_data(LSM, LSM_ACC_X_MSB), b.read_byte_data(LSM, LSM_ACC_X_LSB))
    accy = twos_comp_combine(b.read_byte_data(LSM, LSM_ACC_Y_MSB), b.read_byte_data(LSM, LSM_ACC_Y_LSB))
    accz = twos_comp_combine(b.read_byte_data(LSM, LSM_ACC_Z_MSB), b.read_byte_data(LSM, LSM_ACC_Z_LSB))

    gyrox = twos_comp_combine(b.read_byte_data(LGD, LGD_GYRO_X_MSB), b.read_byte_data(LGD, LGD_GYRO_X_LSB))
    gyroy = twos_comp_combine(b.read_byte_data(LGD, LGD_GYRO_Y_MSB), b.read_byte_data(LGD, LGD_GYRO_Y_LSB))
    gyroz = twos_comp_combine(b.read_byte_data(LGD, LGD_GYRO_Z_MSB), b.read_byte_data(LGD, LGD_GYRO_Z_LSB))

    data = (magx, magy, magz, accx, accy, accz, gyrox, gyroy, gyroz)
    
    print data