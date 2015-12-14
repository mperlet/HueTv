#!/usr/bin/env python
# -- coding: utf-8 --


# https://github.com/studioimaginaire/phue/blob/master/phue.py
# http://www.developers.meethue.com/documentation/core-concepts
# http://stackoverflow.com/questions/22588146/tracking-white-color-using-python-opencv
# http://docs.opencv.org/master/df/d9d/tutorial_py_colorspaces.html#gsc.tab=0
# http://giusedroid.blogspot.de/2015/04/using-python-and-k-means-in-hsv-color.html
# http://stackoverflow.com/questions/2890896/extract-ip-address-from-an-html-string-python
# http://stackoverflow.com/questions/603852/multicast-in-python
# https://gist.github.com/dankrause/6000248

import argparse
import socket
import struct
import re
import cv2

from phue import Bridge
from collections import Counter


def find_hue_bridge():
    """Function to find one Hue-Bridge in the current LAN"""
    MCAST_GRP = '239.255.255.250'
    MCAST_PORT = 1900

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        ssdp_package = sock.recv(10240)
        if 'hue-bridgeid' in ssdp_package:
            ip_addr = re.findall( r'[0-9]+(?:\.[0-9]+){3}', ssdp_package)
            if MCAST_GRP in ip_addr:
                ip_addr.remove(MCAST_GRP)
            if len(ip_addr) == 1:
                return ip_addr.pop()


def huetv(img_size=100, webcam=0, buffer_size=5, bridge_ip=''):
    """Function to start the read-calc-set-Loop
        * read a webcam-picture
        * calculate the most common color
        * set the color to all hue-lights
    """

    CV2_QUOT_PHILIPS = 179.0 / 65280.0

    # HUE API
    hue_bridge = Bridge(bridge_ip)
    hue_bridge.connect()
    hue_bridge.get_api()

    # WEBCAM API
    cam = cv2.VideoCapture(webcam)
    buf = []


    while True:
        # Read new Webcam Image
        _, image = cam.read()

        # Resize Image
        image = cv2.cvtColor(cv2.resize(image, (img_size, img_size)), cv2.COLOR_BGR2HSV)

        # Calculate the most common color
        philips_hue = int(Counter(image[:,:,0].flatten().tolist()).most_common(1)[0][0] / CV2_QUOT_PHILIPS)

        # Add to color-buffer
        buf.append(philips_hue)

        # if buffer is full
        if(len(buf) == buffer_size):

            # calculate the mean color
            hue = sum(buf)/len(buf)

            # set the color to all hue-lights
            for i in range(1, len(hue_bridge.lights)):
                hue_bridge.set_light(i, 'hue', hue)
            print(hue)

            # reset the buffer
            buf = []

if __name__ == "__main__":
    # get commandline parameters
    parser = argparse.ArgumentParser(
        description="HueTv projects the most common color onto the *Philips Hue*-lights.")
    parser.add_argument('-i' ,'--image-size', dest='img_size', type=int,
                        help="""Resizes the captured image to the given size.
                        Lower is faster, default is 100""", default=100)
    parser.add_argument('-w' ,'--webcam', dest='webcam', type=int,
                        help="""Set a specific webcam if you have
                             more than one connected camera.
                             Use 1 if you want to use your second webcam.
                             Default is 0.""", default=0)
    parser.add_argument('-b' ,'--buffer_size', dest='buffer_size', type=int,
                        help="""Set a Buffersize, The buffer stores the common colors.
                                Lower is faster, default is 5""", default=5)
    parser.add_argument('-p' ,'--bridge-ip', dest='bridge_ip', type=str,
                        help="""Insert your Bridge-IP.""")
    args = parser.parse_args()


    if not args.bridge_ip:
        print("Try to find Hue-Bridge...")
        bridge_ip = find_hue_bridge()
        print("Hue-Bridge-IP: %s" % bridge_ip)
    else:
        bridge_ip = args.bridge_ip


    # Execute the RCS-Loop
    huetv(args.img_size, args.webcam, args.buffer_size, bridge_ip)




