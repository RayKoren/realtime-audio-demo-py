# Real-time Audio Pass-through

A Python program that provides real-time audio pass-through with configurable settings. This program allows you to route audio from an input device (like a microphone) to an output device (like speakers) with minimal latency.

## Features

- Real-time audio pass-through with minimal latency
- Configurable audio settings:
  - Input/output device selection
  - Sample rate
  - Number of channels (mono/stereo)
  - Block size (affects latency)
- Buffer monitoring to track audio processing
- Graceful exit with 'stop' command

## Requirements

- Python 3.x
- Required packages:
  - sounddevice
  - numpy

## Installation

1. Clone this repository
2. Install the required packages:
```bash
pip install sounddevice numpy
```

## Usage

Run the program:
```bash
python realtime_audio.py
```

The program will:
1. Ask if you want to adjust audio settings
2. If yes, allow you to:
   - Select input and output devices
   - Set sample rate
   - Choose number of channels (mono/stereo)
   - Configure block size
3. If no, use default settings:
   - Default input/output devices
   - 44100 Hz sample rate
   - Mono (1 channel)
   - 1024 samples block size

During operation:
- Buffer usage is displayed in real-time
- Type 'stop' and press Enter to exit the program

## Default Settings

- Sample Rate: 44100 Hz
- Channels: 1 (mono)
- Block Size: 1024 samples
- Buffer Size: 10 blocks

## Notes

- Lower block sizes result in lower latency but may cause more underruns/overruns
- The program shows buffer usage to help monitor audio processing stability
- Use 'stop' command to gracefully exit the program