#!/bin/bash
#Useful for deleting the background so it is transparent and then overlay onto white background before saving.
#White background is my most important, transparent is black in most viewers and is black when render through StableDiff
#Script will be receiving parameters so you can specify colors with the words for well known colors and hexidecimal like the web.
#Script will also be able to specify the decimal variations and the alpha channels so you can have a semi transparent background.
#Script should be able to accept a swatch, or a stream, or a low quality background, or a high quality backround image and will have crop fit opts
#Once the layering stuff is cool, this guy gets renamed, don't depend on him existing, he will have a more evolved version next to him and go away.
python3 simple_bg_to_transparent.py