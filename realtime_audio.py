import sounddevice as sd
import numpy as np
import queue
import threading

SAMPLE_RATE = 44100           # Audio sample rate (Hz)
BLOCK_SIZE = 1024             # Block size (lower = lower latency)
CHANNELS = 1                  # 1=mono, 2=stereo

audio_buffer = queue.Queue(maxsize=10)  # Size can be tuned

def audio_callback_indata(indata, frames, time, status):
    try:
        audio_buffer.put_nowait(indata.copy())
    except queue.Full:
        print('Input overflow - buffer full.')

def audio_callback_outdata(outdata, frames, time, status):
    try:
        data = audio_buffer.get_nowait()
        outdata[:] = data
    except queue.Empty:
        print('Output underflow - buffer empty.')
        outdata[:] = np.zeros((frames, CHANNELS), dtype=np.float32)

def main():
    print("Starting real-time audio pass-through. Press Ctrl+C to stop.")
    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, channels=CHANNELS,
            dtype='float32', callback=audio_callback_indata
        ), sd.OutputStream(
            samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, channels=CHANNELS,
            dtype='float32', callback=audio_callback_outdata
        ):
            threading.Event().wait()  # Wait indefinitely
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()