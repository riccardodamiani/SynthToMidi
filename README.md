# Synthesia video to Midi converter  
## Description
Small python script that create a MIDI file from a synthesia video. Once you have the MIDI file you can visualize the music sheet using a software like [Muse Score](https://musescore.org/).  
The script analyze the frames of the video (no audio involved) and detects the change in color in the virtual keyboard keys. It than convert the color changes into midi messages (note on and note off) that are stored into a file. The script can distinguish between different colors of the keys and separate the notes automatically into different tracks.  
This is a one day project so it's still bare bone as for graphics, error handling ecc...  
Also, there are some problems that needs to be fixed such as:
* issues in detecting the notes when there are graphical effects on the video (for example the glow of light when the note hit the key in newer synthesia videos)
* incorrectly identify notes in some videos

## Requirements  
Python3 and a few pip packages: opencv-python, mido

## Windows installation
Install python3 from [here](https://www.python.org/downloads/)  
Follow this page to install pip3 [pip.pypa.io](https://pip.pypa.io/en/stable/installation/)
Then open a terminal in the folder you cloned the repo in and run the following:  
```bash
pip install -r requirements.txt
```  
## Linux installation  
Open a terminal in the folder you cloned the repo in and run the following:
```bash  
sudo apt-get update
sudo apt install python3
python3 -m ensurepip --upgrade
pip install -r requirements.txt
```  

## Run  
```bash
python3 synthesiaToMidi.py video.mp4
```  
When is done a new file named (in this case) video.mid should appear in the same folder of video.mp4.  
You can also process all files in a folder with the command:  
```bash
python3 synthesiaToMidi.py path_to_folder
```  

## Troubleshooting  
If the script breaks a few seconds after launching it it's probably due to the fact that it wasn't able to properly find the keyboard on screen. Frequently this is due to some animations of effect going on on screen that hides the keys or mess with the brightness. The easiest way to fix this is to cut the video so it starts when the keyboard is already visible and beautiful.  
Another thing that can cause problems are low saturation note colors or graphical effects such as a light flash when a note is pressed. These can cause some notes to not be detected when they should and other that are detected when they should not. To fix these issues a parameter is added called color_insensitivity. This parameter changes the color threshold of a key to be considered as pressed. To use this parameter add -c to the end of the command followed by the threshold value (default is 0.2).  
```bash
python3 synthesiaToMidi.py video.mp4 -c 0.1
```  
In general if some notes are not detected you should lower the color_insensitivity, if are detected notes that don't exists you should rise the color_insensitivity. Normally it should be in the range 0.05-0.8.  
To help debug there is also a debug paramenter (-d) that, when activated, it will save a debug.mp4 video with some information about the processing such as the note detected (larger text on top of the pressed key) and the color index that is compared with the color_insensitivity threshold (smalled text on the bottom of the screen).