import colorsys

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