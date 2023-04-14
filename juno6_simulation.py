import numpy as np
import matplotlib.pyplot as plt

def sawtooth_wave(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    waveform = 2 * (t * freq - np.floor(0.5 + t * freq))
    return waveform

freq = 440  # Frequency in Hz (A4 note)
duration = 1  # Duration in seconds
waveform = sawtooth_wave(freq, duration)

plt.plot(waveform[:1000])
plt.xlabel('Time [samples]')
plt.ylabel('Amplitude')
plt.title('Sawtooth Wave')
plt.show()

from scipy.signal import butter, lfilter

def low_pass_filter(signal, cutoff_freq, sample_rate=44100, order=4):
    nyquist_freq = 0.5 * sample_rate
    normalized_cutoff = cutoff_freq / nyquist_freq
    b, a = butter(order, normalized_cutoff, btype='low', analog=False)
    filtered_signal = lfilter(b, a, signal)
    return filtered_signal

cutoff_freq = 2000  # Cutoff frequency in Hz
filtered_waveform = low_pass_filter(waveform, cutoff_freq)

plt.plot(filtered_waveform[:1000])
plt.xlabel('Time [samples]')
plt.ylabel('Amplitude')
plt.title('Filtered Sawtooth Wave')

def adsr_envelope(duration, attack, decay, sustain, release, sample_rate=44100):
    total_samples = int(duration * sample_rate)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)

    envelope = np.zeros(total_samples)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain, decay_samples)
    envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)

    return envelope

attack = 0.1  # Attack time in seconds
decay = 0.2  # Decay time in seconds
sustain = 0.6  # Sustain level (0 to 1)
release = 0.5  # Release time in seconds
envelope = adsr_envelope(duration, attack, decay, sustain, release)

plt.plot(envelope)
plt.xlabel('Time [samples]')
plt.ylabel('Amplitude')
plt.title('ADSR Envelope')
plt.show()

# Apply the envelope to the filtered waveform
synth_output = filtered_waveform * envelope

plt.plot(synth_output[:1000])
plt.xlabel('Time [samples]')
plt.ylabel('Amplitude')
plt.title('Synthesized Sound')
plt.show()
