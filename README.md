# realtime-audio-demo-py

A Python program that handles real-time audio input (microphone) and output (speakers) using a buffer. It minimizes latency, avoids buffer overflow/underflow. Utilizes sounddevice (for audio I/O) and a thread-safe queue.Queue as the buffer between input and output streams.

