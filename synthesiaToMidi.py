import cv2
import midi_helper
from midi_helper import play_note, create_new_track, init_midi, save_midi, midi_note_to_notation
import color_helper
from color_helper import get_hue, are_same_hue, get_saturation, get_brightness, is_key_color, colorfulness
import os
import time
import argparse
import numpy as np

key_list = []
keys_color = []
music_tracks_color = []

avg_key_width = 0
key_width_tolerance = 0
hue_threshold = 20

# This function search for the keyboard rectangle, find each key with their rectangles and associate a note to each key
# Compile the list key_list that contains all information about each key of the keyboard and returns a couple of variable 
# containing the keyboard start and end rows
def search_keyboard(binary_frame):
    global key_list, key_width_tolerance, avg_key_width

    color_changes = 0
    max_color_changes = 0
    current_color = 255
    keyboard_start_line = 0
    keyboard_end_line = -1
    black_white_keys_border = 0
    key_width = 0

    height, width = binary_frame.shape
    for i in range(height-1, int(height*0.7), -1):  # Altezza
        color_changes = 0
        for j in range(width):  # Larghezza
            pixel = binary_frame[i, j]
            key_width += 1
            if pixel != current_color:
                current_color = pixel
                if key_width > 6:
                    color_changes += 1
                key_width = 0
        #print(f'color_changes: {color_changes}')
        if keyboard_end_line > 0:
            #started the black keys area
            if(color_changes > max_color_changes * 1.4):
                max_color_changes = color_changes
                black_white_keys_border = i
            if color_changes < 30:
                keyboard_start_line = i
                break
            else:
                max_color_changes = min(color_changes, max_color_changes)
        else:
            if color_changes >= 30:
                keyboard_end_line = i
                max_color_changes = color_changes

    print(keyboard_start_line, black_white_keys_border,keyboard_end_line )
    
    white_keys_middle_line = (keyboard_end_line + black_white_keys_border) // 2
    black_keys_middle_line = (black_white_keys_border + keyboard_start_line) // 2

    #get the position of each white key and the average width
    current_color = 0
    white_keys_borders = []
    black_keys_borders = []
    start_key_col = 0
    for j in range(width):  # Larghezza
        pixel = binary_frame[white_keys_middle_line, j]
        if pixel == 255 and current_color == 0: #transition from black to white
            start_key_col = j
            current_color = pixel
        if pixel == 0 and current_color == 255: #transition from white to black
            current_color = pixel
            white_keys_borders.append([start_key_col, j])
    if(current_color == 255):
        white_keys_borders.append([start_key_col, j])

    #get the position of each black key and the average width
    current_color = 255
    key_width = 0
    white_keys = []
    black_keys = []
    for j in range(width):  # Larghezza
        pixel = binary_frame[black_keys_middle_line, j]
        if pixel == 0:
            key_width += 1
        if pixel == 0 and current_color == 255: #transition from white to black
            start_key_col = j
            current_color = pixel
        if pixel == 255 and current_color == 0: #transition from black to white
            if key_width > 5:
                black_keys_borders.append([start_key_col, j])
            current_color = pixel
            key_width = 0
    if(current_color == 0):
        black_keys_borders.append([start_key_col, j])

    #find the average white key width
    white_key_width = 0
    for key in white_keys_borders:
        white_key_width += key[1] - key[0]
    white_key_width /= len(white_keys_borders)

    #find the average black key width
    black_key_width = 0
    for key in black_keys_borders:
        black_key_width += key[1] - key[0]
    black_key_width /= len(black_keys_borders)

    avg_key_width = (white_key_width + black_key_width) / 2
    key_width_tolerance = max(abs(white_key_width - avg_key_width), abs(black_key_width - avg_key_width)) * 1.5

    print(f'avg white: {white_key_width}, avg black: {black_key_width}, whites: {len(white_keys_borders)}, blacks: {len(black_keys_borders)}')
    #compile the two arrays for white and black keys
    for key in white_keys_borders:
        white_keys.append({"note": 0, "pos": (key[0] + key[1]) / 2, "rect": [key[0]+1, black_white_keys_border+3, key[1]-1, keyboard_end_line-3], "is_pressed": False, "size": white_key_width, "key": "white", "default_color": (255, 255, 255)})
    for key in black_keys_borders:
        black_keys.append({"note": 0, "pos": (key[0] + key[1]) / 2, "rect": [key[0]+1, keyboard_start_line+3, key[1]-1, black_white_keys_border-3], "is_pressed": False, "size": black_key_width, "key": "black", "default_color": (0, 0, 0)})
    
    #merge the lists
    key_list = white_keys + black_keys

    # Ordina la lista unita in base alla chiave "pos"
    key_list = sorted(key_list, key=lambda x: x["pos"])

    # search for a octave pattern
    octave_pattern = ["white", "black", "white", "black", "white", "white", "black", "white", "black", "white", "black", "white"]
    key_octave_list = [element["key"] for element in key_list]
    octave_indexes = find_key_octave_pattern(key_octave_list, octave_pattern)

    # find middle c
    middle_c_index = min(
        octave_indexes, key=lambda i: abs(i - len(key_list) // 2)
    )
    keyboard_starting_note_index = 60 - middle_c_index
    
    for key in key_list:
        key["note"] = keyboard_starting_note_index
        keyboard_starting_note_index += 1
    return keyboard_start_line, black_white_keys_border, keyboard_end_line

# find a octave pattern in the key sequence. Used to identify each note of the keyboard
def find_key_octave_pattern(sequence, pattern):
    pattern_len = len(pattern)
    results = []  # Per memorizzare gli indici iniziali delle corrispondenze

    # Scorri la sequenza per cercare il pattern
    for i in range(len(sequence) - pattern_len + 1):
        # Confronta il sottogruppo della sequenza con il pattern
        if sequence[i:i + pattern_len] == pattern:
            results.append(i)
    
    return results

# checks a few rows at the and of the frame to confirm that there is a valid keyboard on screen
def is_keyboard_present(gray_frame):
    current_color = 255
    
    #_, binary_frame = cv2.threshold(gray_frame, 180, 255, cv2.THRESH_BINARY)

    for i in range(gray_frame.shape[0]-1, int(gray_frame.shape[0]*0.9), -20):  # height
        color_change = 0
        key_width = 0
        for j in range(gray_frame.shape[1]):  # width
            pixel = gray_frame[i, j]
            key_width += 1

            if(pixel > 180 and current_color == 0):
                current_color = 255
                #print(f"width: {key_width}")
                if key_width > 6 and key_width < 40:
                    color_change += 1
                key_width = 0
            if(pixel < 120 and current_color == 255):
                current_color = 0
                #print(f"width: {key_width}")
                if key_width > 6 and key_width < 40:
                    color_change += 1
                key_width = 0
        #print(f'color_changes present: {color_change}')
        if color_change > 30:
            #cv2.imshow('frame', gray_frame)
            #cv2.waitKey(0)
            return True

    return False

# get the color of each key in the keyboard and returns a list of them
def get_keys_color(frame):
    average_colors = []
    for key in key_list:
        average_colors.append(cv2.mean(frame[key["rect"][1]:key["rect"][3], key["rect"][0]:key["rect"][2]])[:3])
    return average_colors

# Function that finds and hightlight the note rectangles while they are moving across the screen
# This is not used
def find_notes_rectangles(frame, binary_frame, roi_height, rect_width, tolerance):

    roi = binary_frame[0:roi_height, 0:binary_frame.shape[1]]
    # Find contours
    contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter rectangles by width
    selected_rectangles = []

    for contour in contours:
        # Get a bounding rectangle for the contour
        x_rect, y_rect, w_rect, h_rect = cv2.boundingRect(contour)
        
        # Check if the width is within the target range
        if rect_width - tolerance <= w_rect <= rect_width + tolerance:
            selected_rectangles.append((x_rect, y_rect, w_rect, h_rect))
            # Draw the rectangle on the image
            cv2.rectangle(frame, (x_rect, y_rect), (x_rect + w_rect, y_rect + h_rect), (0, 255, 0), 2)


# search for a track identifies by a specific color
# returns the index of the track if it exists -1 otherwise
def find_track_by_color(color):
    index = 0
    for track_color in music_tracks_color:
        if are_same_hue(color, track_color, hue_threshold):
            return index
        index += 1
    return -1

def print_debug_text(frame, text, position, size):
    # Disegna il bordo del testo
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, size, (255, 255, 255), thickness=2 + 2, lineType=cv2.LINE_AA)

    # Disegna il testo sopra il bordo
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, size, (0, 0, 0), thickness=2, lineType=cv2.LINE_AA)

def process(filename, args):
    global key_list, keys_color, music_tracks_color
    key_list = []
    keys_color = []
    music_tracks_color = []

    midi_filename = os.path.splitext(filename)[0] + '.mid'
    debug_video_filename = "debug.mp4"
    default_note_volume = args.volume
    
    # some variables
    beatsPerMinute = 60

    init_midi(beatsPerMinute)
    keyboard_check_timer = 0
    valid_keyboard = False

    # load the video
    cap = cv2.VideoCapture(filename)
    #open a debug video
    if args.debug:
        # Ottieni la risoluzione e il frame rate dal video originale
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        # Codec e creazione del VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(debug_video_filename, fourcc, fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        #print(f"Current time: {current_time}")

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary_frame = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY)
        if args.debug:
            debug_frame = np.copy(frame)

        #wait for the image to be bright enough and than search the keys
        if(not valid_keyboard):
            if(not is_keyboard_present(gray_frame)):
                continue
            else:
                #initialize the keyboard the first time
                if not valid_keyboard:
                    valid_keyboard = True
                    keyboard_start_line, black_white_keys_border,keyboard_end_line = search_keyboard(binary_frame)
                    keys_color = get_keys_color(frame)
                    keyboard_check_timer = time.time()
                    print(key_list)
        
        # every second check whether there is a valid keyboard on screen and recalculate the key color
        if time.time() - keyboard_check_timer > 1.0:
            keyboard_check_timer = time.time()
            if(not is_keyboard_present(gray_frame)):
                valid_keyboard = False
                continue

        #update the colors
        new_keys_color = get_keys_color(frame)
        
        #checks whether a key was pressed or released
        for old_color, new_color, key in zip(keys_color, new_keys_color, key_list):
            # the key is not pressed
            #print(np.linalg.norm(np.array(new_color) - np.array(default_white_key_color)))
            colorfulness_value = colorfulness(new_color)
            if args.debug and colorfulness_value > 0.01:
                print_debug_text(debug_frame, str(colorfulness_value)[:3] if colorfulness_value>=0.1 else str(colorfulness_value)[1:4], (key["rect"][0], frame_height-10-10*(key["note"]%3)), 0.4)
            if colorfulness_value <= args.color_insensitivity:
                if key["is_pressed"]: #the key was pressed
                    key["is_pressed"] = False
                    track_index = find_track_by_color(old_color)
                    print("Key " + midi_note_to_notation(key["note"]) + f" ({str(key['note'])}) " + " released")
                    play_note(track_index, 'note_off', note=key["note"], velocity=default_note_volume, time=current_time)
            else: #the key is pressed
                #the key was not pressed
                if not key["is_pressed"]:
                    key["is_pressed"] = True
                    # press the key in the new track
                    track_index = find_track_by_color(new_color)
                    if track_index == -1:
                        print("Created new track")
                        track_index = create_new_track()
                        music_tracks_color.append(new_color)
                    
                    if args.debug:
                        print_debug_text(debug_frame, midi_note_to_notation(key["note"]), (key["rect"][0], key["rect"][1]), 0.6)
                    print("Key " + midi_note_to_notation(key["note"]) + f" ({str(key['note'])}) " + " pressed")
                    #print(f"lum: {get_brightness(new_color)}, sat {get_saturation(new_color)}")
                    play_note(track_index, 'note_on', note=key["note"], velocity=default_note_volume, time=current_time)
                #if the key was pressed by another color (another voice) or if the color became more intense 
                # (multiple presses of same key) replay the same key
                elif not are_same_hue(old_color, new_color, hue_threshold):
                    #release the key
                    track_index = find_track_by_color(old_color)
                    print("Key " + midi_note_to_notation(key["note"]) + f" ({str(key['note'])}) " + " released")
                    play_note(track_index, 'note_off', note=key["note"], velocity=default_note_volume, time=current_time)

                    # press the key again
                    track_index = find_track_by_color(new_color)
                    if track_index == -1:
                        print("Created new track")
                        track_index = create_new_track()
                        music_tracks_color.append(new_color)
                    
                    if args.debug:
                        print_debug_text(debug_frame, midi_note_to_notation(key["note"]), (key["rect"][0], key["rect"][1]), 0.6)
                    print("Key " + midi_note_to_notation(key["note"]) + f" ({str(key['note'])}) " + " pressed")
                    #print(f"hues - old color: {get_hue(old_color)}, new color {new_color}")
                    play_note(track_index, 'note_on', note=key["note"], velocity=default_note_volume, time=current_time)
                elif args.debug:
                    print_debug_text(debug_frame, midi_note_to_notation(key["note"]), (key["rect"][0], key["rect"][1]), 0.6)
        keys_color = new_keys_color

        #cv2.imshow('frame', frame)
        #cv2.waitKey(0)
        if args.debug:
            out.write(debug_frame)  # Salva il frame nel video

    # save the midi file
    save_midi(midi_filename)
    print(f"Saved as {midi_filename}")

    cap.release()
    if args.debug:
        out.release()
    cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("filename", help="Input video filename", type=str)
    parser.add_argument("-v", "--volume", help="Change the midi note velocity (0-127)", type=int, default=64)
    parser.add_argument("-c", "--color_insensitivity", help="Change how sensitive it is to keys color. The lower the more sensitive it is to difference from the default key color (white/black)", type=float, default=0.07)
    parser.add_argument("-d", "--debug", help="Create an output mp4 file for debugging", action="store_true")

    # Parse the arguments
    args = parser.parse_args()

    if os.path.isdir(args.filename):
        directory = args.filename
        for filename in os.listdir(args.filename):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):  # Controlla se è un file (esclude le cartelle)
                process(file_path, args)
    elif os.path.isfile(args.filename):
        process(args.filename, args)

if __name__ == "__main__":
    main()