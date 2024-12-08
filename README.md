## Synthesia video to Midi converter  
# Description
Small python script that create a midi file from a synthesia video.  
The script analyze the frames of the video (no audio involved) and detects the change in color in the virtual keyboard keys. It than convert the color changes into midi messages (note on and note off) that are stored into a file. The script is distinguish between different colors of the keys and separate the notes automatically into different tracks.  
This is a one day project so it's still bare bone as for graphics, error handling ecc...  
Also, there are some problems that needs to be fixed such as:
* tracks desyncronization
* issues in detecting the notes when there are graphical effects on the video (for example the glow of light when the note hit the key in newer synthesia videos)

# Requirements  
Python3 and a few pip packages: opencv-python, mido

# Windows installation
Install python3 from [here](https://www.python.org/downloads/)  
Follow this page to install pip3 [pip.pypa.io](https://pip.pypa.io/en/stable/installation/)
Then open a terminal in the folder you cloned the repo in and run the following:  
```bash
pip install -r requirements.txt
```  
# Linux installation  
Open a terminal in the folder you cloned the repo in and run the following:
```bash  
sudo apt-get update
sudo apt install python3
python3 -m ensurepip --upgrade
pip install -r requirements.txt
```  

# Run  
```bash
python3 synthesiaToMidi.py video.mp4
```  
When is done a new file names (in this case) video.mid should appear in the same folder of video.mp4.  

# Troubleshooting  
If the script breaks a few seconds after launching it it's probably due to the fact that it wasn't able to properly find the keyboard on screen. Frequently this is due to some animations of effect going on on screen that hides the keys or mess with the brightness. The easiest way to fix this is to cut the video so it starts when the keyboard is already visible and beautiful. 
