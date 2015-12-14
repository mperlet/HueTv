# HueTv

HueTv projects the most common color onto the *Philips Hue*-lights.

![HueTv Demo](https://www.dropbox.com/s/dfni6ea5g9g66v2/huetv_demo.gif?raw=1 "HueTv Demo")

## Install

    git clone git@github.com:mperlet/HueTv.git
    pip install phue  
    
#### Fedora

    dnf install opencv-python
    
#### Arch Linux ARM
       
    pacman -S opencv python2-numpy
    
## Usage
    
Run HueTv and search a Hue-Bridge

    ./huetv.py

Set the Hue-Bridge-IP manually

    ./huetv.py -p <BridgeIp>
    
Help
    
    ./huetv.py --help