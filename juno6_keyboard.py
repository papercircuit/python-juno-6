import pygame
import pygame.midi
import pygame.locals
import numpy as np
from scipy.signal import butter, lfilter
import sounddevice as sd

# Add the sawtooth_wave, low_pass_filter, and adsr_envelope functions here

def sawtooth_wave(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    waveform = 2 * (t * freq - np.floor(0.5 + t * freq))
    return waveform

def square_wave(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    waveform = 2 * (t * freq - np.floor(0.5 + t * freq))
    waveform[waveform < 0] = -1
    waveform[waveform > 0] = 1
    return waveform

def sub_wave(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    waveform = 2 * (t * freq - np.floor(0.5 + t * freq))
    waveform[waveform < 0] = -1
    waveform[waveform > 0] = 1
    waveform = waveform * 0.5
    return waveform

def low_pass_filter(signal, cutoff_freq, sample_rate=44100, order=4):
    nyquist_freq = 0.5 * sample_rate
    normalized_cutoff = cutoff_freq / nyquist_freq
    b, a = butter(order, normalized_cutoff, btype='low', analog=False)
    filtered_signal = lfilter(b, a, signal)
    return filtered_signal

def adsr_envelope(duration, attack, decay, sustain, release,        sample_rate=44100):
    total_samples = int(duration * sample_rate)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)

    envelope = np.zeros(total_samples)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain, decay_samples)
    envelope[attack_samples + decay_samples:-release_samples] = sustain
    envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)

    return envelope

class Voice:
    def __init__(self, midi_note_number):
        self.midi_note_number = midi_note_number
        self.freq = 440 * (2**((midi_note_number - 69) / 12))
        self.duration = 1
        self.attack = 0.1
        self.decay = 0.2
        self.sustain = 0.6
        self.release = 0.5
        self.pwm_width = 0.5
        self.sub_osc_level = 0.5
        self.cutoff_freq = 2000
        self.resonance = 0.5

    def generate_waveform(self):
        waveform_saw = sawtooth_wave(self.freq, self.duration)
        waveform_square = square_wave(self.freq, self.duration, self.pwm_width)
        waveform_sub = square_wave(self.freq / 2, self.duration, 0.5) * self.sub_osc_level
        waveform = waveform_saw + waveform_square + waveform_sub
        return waveform

    def generate_envelope(self):
        envelope = adsr_envelope(self.duration, self.attack, self.decay, self.sustain, self.release)
        return envelope

    def apply_filter(self, waveform):
        filtered_waveform = low_pass_filter(waveform, self.cutoff_freq, resonance=self.resonance)
        return filtered_waveform

    def generate_audio(self):
        waveform = self.generate_waveform()
        envelope = self.generate_envelope()
        filtered_waveform = self.apply_filter(waveform)
        synth_output = filtered_waveform * envelope
        synth_output_normalized = synth_output / np.max(np.abs(synth_output))
        return synth_output_normalized

class Synthesizer:
    def __init__(self):
        self.voices = []

    def play_note(self, midi_note_number):
        if len(self.voices) < 6:
            voice = Voice(midi_note_number)
            self.voices.append(voice)
            audio = voice.generate_audio()
            sd.play(audio, samplerate=44100, blocksize=2048)

    def stop_note(self, midi_note_number):
        self.voices = [voice for voice in self.voices if voice.midi_note_number != midi_note_number]

    def apply_chorus(self, audio):
        # Implement the chorus effect here
        pass



freq = 440  # Frequency in Hz (A4 note)
duration = 1  # Duration in seconds
waveform = sawtooth_wave(freq, duration)
cutoff_freq = 2000  # Cutoff frequency in Hz
filtered_waveform = low_pass_filter(waveform, cutoff_freq)

attack = 0.1  # Attack time in seconds
decay = 0.2  # Decay time in seconds
sustain = 0.6  # Sustain level (0 to 1)
release = 0.5  # Release time in seconds
envelope = adsr_envelope(duration, attack, decay, sustain, release)

synth_output = filtered_waveform * envelope

# Normalize the output to the range [-1, 1]
synth_output_normalized = synth_output / np.max(np.abs(synth_output))

# Play the synthesized sound
sd.play(synth_output_normalized, samplerate=44100)
sd.wait()

def play_note(midi_note_number):
    freq = 440 * (2**((midi_note_number - 69) / 12))
    duration = 1  # Duration in seconds
    waveform = sawtooth_wave(freq, duration)
    cutoff_freq = 2000  # Cutoff frequency in Hz
    filtered_waveform = low_pass_filter(waveform, cutoff_freq)

    attack = 0.1  # Attack time in seconds
    decay = 0.2  # Decay time in seconds
    sustain = 0.6  # Sustain level (0 to 1)
    release = 0.5  # Release time in seconds
    envelope = adsr_envelope(duration, attack, decay, sustain, release)

    synth_output = filtered_waveform * envelope
    synth_output_normalized = synth_output / np.max(np.abs(synth_output))

    sd.play(synth_output_normalized, samplerate=44100, blocksize=2048)
    sd.wait

KEY_TO_MIDI = {
    pygame.locals.K_z: 60,  # C4s
    pygame.locals.K_s: 61,  # C#4
    pygame.locals.K_x: 62,  # D4
    pygame.locals.K_d: 63,  # D#4
    pygame.locals.K_c: 64,  # E4
    pygame.locals.K_v: 65,  # F4
    pygame.locals.K_g: 66,  # F#4
    pygame.locals.K_b: 67,  # G4
    pygame.locals.K_h: 68,  # G#4
    pygame.locals.K_n: 69,  # A4
    pygame.locals.K_j: 70,  # A#4
    pygame.locals.K_m: 71,  # B4
    pygame.locals.K_q: 72,  # C5
}

pygame.init()
pygame.midi.init()

# Set up the display
window_size = (800, 600)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Simple Synthesizer')

synth = Synthesizer()

# Main event loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in KEY_TO_MIDI:
                midi_note_number = KEY_TO_MIDI[event.key]
                synth.play_note(midi_note_number)
        elif event.type == pygame.KEYUP:
            if event.key in KEY_TO_MIDI:
                midi_note_number = KEY_TO_MIDI[event.key]
                synth.stop_note(midi_note_number)

pygame.quit()

