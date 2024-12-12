import colorsys
import numpy as np
import cv2

# return the hue of a color
def get_hue(color):
    # Normalize RGB values to the range [0, 1]
    color_normalized = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
    
    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(*color_normalized)
    
    # Convert hue from [0, 1] to [0, 360]
    return h * 360

# checks whether two color have same hue within a tolerance
def are_same_hue(color1, color2, hue_threshold):
    hue1 = get_hue(color1)
    hue2 = get_hue(color2)
    
    # Calculate the absolute difference and adjust for the wrap-around at 360°
    diff = abs(hue1 - hue2)
    diff = min(diff, 360 - diff)  # Take the shortest distance around the circle
    
    # Check if the hue difference is within the tolerance
    return diff <= hue_threshold

#return a value rapresenting the color type
# 0 means close to black
# 255 means close to white
# near 127 means colorful
def color_descriptor(rgb_color):
    # Convert RGB to HSV
    r, g, b = rgb_color
    rgb_array = np.uint8([[rgb_color]])  # Convert to array for OpenCV
    hsv_color = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HSV)[0][0]

    # Extract components
    hue, saturation, value = hsv_color

    # Calculate luminosity (perceptual luminance)
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

    # Combine luminance and saturation to calculate the descriptor
    descriptor = (luminance * 0.7 + saturation * 0.3)

    return descriptor

def colorfulness(color):
    r, g, b = color

    #rescale the channels between 0 and 1
    delta_r, delta_b, delta_g = r / 255, b /255, g / 255
    #calculates the difference between each channels
    delta_rb, delta_rg, delta_bg = abs(delta_r-delta_b), abs(delta_r-delta_g), abs(delta_b-delta_g)
    #amplify the difference between channels deltas (the more different 2 channels are the more it is colorful)
    delta_rb = delta_rb*delta_rb
    delta_rg = delta_rg*delta_rg
    delta_bg = delta_bg*delta_bg
    #sum the channles pair deltas
    color_difference = delta_rb + delta_rg + delta_bg

    #calculate a value that is higher the more it is far from black and white
    lum = r + b + g
    bw_corrector = min(765-lum, lum) / 120
    
    return color_difference * bw_corrector


# returns the saturation of a color
def get_saturation(color):
    # Normalize RGB values to the range [0, 1]
    color_normalized = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
    
    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(*color_normalized)

    return s

# function that return the brightness of the color
# the brightness is calculated in a unortodox way giving more importance to high component color than to the total composition
# for example the color (150, 0, 0) have higher brightness than the color (50, 50, 50) even though the cum of the component gives the same number
# in reality this function calculates the "vivacity" of a color
def get_brightness(color):
    r, g, b = color
    brighness = (r / 255) * (r / 255) + (g / 255) * (g / 255) + (b / 255) * (b / 255)
    return brighness  #value between 0 and 3

# return true if the key is black or white (the key is not pressed)
# this function checks for saturation (which should be low for black and white colors) 
# and brightness (because sometime black keys have pretty high saturation)
def is_key_color(color):
    lum = get_brightness(color)
    if get_saturation(color) < 0.3 or lum < 0.25:
        return True
    return False