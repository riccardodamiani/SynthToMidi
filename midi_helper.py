import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage

midi_tracks = []
midiFile = None
ticksPerBeat = 480
ticksPerSecond = 0
track_tempo = 0
octave_notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def midi_note_to_notation(note):
    notation_index = note % len(octave_notes)
    octave_count = (note // 12) - 1
    return octave_notes[notation_index] + str(octave_count)

def play_note(track_index, msg, note, velocity, time):
    global midi_tracks, ticksPerSecond

    if not track_exists(track_index):
        return False
    
    time = time * ticksPerSecond
    last_message_time = midi_tracks[track_index]["last_msg_time"]
    midi_tracks[track_index]["last_msg_time"] = time

    msg_time = time - last_message_time
    midi_tracks[track_index]["track"].append(Message(msg, note=note, velocity=velocity, time=int(msg_time)))
    return True

def track_exists(track_index):
    global midi_tracks

    if track_index >= len(midi_tracks) or track_index < 0:
        return False
    return True

def create_new_track():
    global track_tempo, midi_tracks

    track_index = len(midi_tracks)
    track = MidiTrack()
    midi_tracks.append({"track": track, "last_msg_time": 0})
    track.append(MetaMessage('set_tempo', tempo=track_tempo))
    midiFile.tracks.append(track)
    return track_index

def init_midi(beatsPerMinute):
    global ticksPerSecond, ticksPerBeat, track_tempo, midiFile
    ticksPerSecond = (beatsPerMinute / 60) * ticksPerBeat
    track_tempo = int(60 * 1_000_000 / beatsPerMinute)  # Convert beats per second to microseconds per beat

    midiFile = MidiFile(ticks_per_beat=ticksPerBeat)

def save_midi(filename):
    global midiFile
    midiFile.save(filename)
