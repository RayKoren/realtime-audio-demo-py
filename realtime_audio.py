import sounddevice as sd
import numpy as np
import queue
import threading
import time

# Default values
DEFAULT_SAMPLE_RATE = 44100           # Audio sample rate (Hz)
DEFAULT_BLOCK_SIZE = 1024             # Block size (lower = lower latency)
DEFAULT_CHANNELS = 1                  # 1=mono, 2=stereo

audio_buffer = queue.Queue(maxsize=10)  # Size can be tuned
stop_event = threading.Event()
last_buffer_display = 0  # For throttling buffer display updates

def show_buffer_usage():
    global last_buffer_display
    current_time = time.time()
    # Only update display every 0.5 seconds to avoid flooding the console
    if current_time - last_buffer_display >= 0.5:
        buffer_size = audio_buffer.maxsize
        current_usage = audio_buffer.qsize()
        usage_percent = (current_usage / buffer_size) * 100
        print(f"\rBuffer usage: {usage_percent:.1f}% ({current_usage}/{buffer_size})", end='')
        last_buffer_display = current_time

def audio_callback_indata(indata, frames, time, status):
    try:
        audio_buffer.put_nowait(indata.copy())
        show_buffer_usage()
    except queue.Full:
        print('\nInput overflow - buffer full.')
        show_buffer_usage()

def audio_callback_outdata(outdata, frames, time, status):
    try:
        data = audio_buffer.get_nowait()
        outdata[:] = data
        show_buffer_usage()
    except queue.Empty:
        print('\nOutput underflow - buffer empty.')
        outdata[:] = np.zeros((frames, DEFAULT_CHANNELS), dtype=np.float32)
        show_buffer_usage()

def user_input_thread():
    while not stop_event.is_set():
        user_input = input()
        if user_input.lower() == 'stop':
            stop_event.set()
            break

def list_audio_devices():
    print("\nAvailable audio devices:")
    devices = sd.query_devices()
    default_input, default_output = sd.default.device
    
    for i, device in enumerate(devices):
        is_default_input = i == default_input
        is_default_output = i == default_output
        default_status = []
        if is_default_input:
            default_status.append("default input")
        if is_default_output:
            default_status.append("default output")
        default_str = f" ({', '.join(default_status)})" if default_status else ""
        
        print(f"{i}: {device['name']}{default_str}")
        print(f"   Input channels: {device['max_input_channels']}")
        print(f"   Output channels: {device['max_output_channels']}")
        print(f"   Default sample rate: {device['default_samplerate']}")
        print()

def get_valid_device(inOut):
    devices = sd.query_devices()
    while True:
        try:
            device_id = input(f"Enter {inOut} device number (press Enter for default {inOut} device): ")
            if not device_id:
                return None
            device_id = int(device_id)
            if 0 <= device_id < len(devices):
                return device_id
            print(f"Please enter a number between 0 and {len(devices)-1}")
        except ValueError:
            print("Please enter a valid number.")

def get_valid_sample_rate(device_id=None):
    if device_id is not None:
        default_rate = int(sd.query_devices(device_id)['default_samplerate'])
    else:
        default_rate = DEFAULT_SAMPLE_RATE

    while True:
        try:
            rate = input(f"Enter sample rate (press Enter for default: {default_rate}): ")
            if not rate:
                return default_rate
            rate = int(rate)
            if rate <= 0:
                print("Sample rate must be positive.")
                continue
            return rate
        except ValueError:
            print("Please enter a valid number.")

def get_valid_channels(device_id=None, is_input=True):
    if device_id is not None:
        max_channels = sd.query_devices(device_id)['max_input_channels' if is_input else 'max_output_channels']
    else:
        max_channels = 2  # Assume at least stereo support

    while True:
        try:
            channels = input(f"Enter number of channels (1=mono, 2=stereo) (press Enter for default: {DEFAULT_CHANNELS}): ")
            if not channels:
                return DEFAULT_CHANNELS
            channels = int(channels)
            if channels not in [1, 2]:
                print("Channels must be 1 (mono) or 2 (stereo).")
                continue
            if channels > max_channels:
                print(f"Selected device only supports up to {max_channels} channel(s).")
                continue
            return channels
        except ValueError:
            print("Please enter a valid number.")

def get_valid_block_size():
    while True:
        try:
            block_size = input(f"Enter block size (press Enter for default: {DEFAULT_BLOCK_SIZE}): ")
            if not block_size:
                return DEFAULT_BLOCK_SIZE
            block_size = int(block_size)
            if block_size <= 0:
                print("Block size must be positive.")
                continue
            return block_size
        except ValueError:
            print("Please enter a valid number.")

def main():
    
    # Ask if user wants to adjust settings
    adjust_settings = input("Would you like to adjust audio settings? (y/n, default: n): ").lower() == 'y'
    
    if adjust_settings:
        # List available devices and get user selection
        list_audio_devices()
        input_device = get_valid_device('input')
        output_device = get_valid_device('output')
        
        # Get user's desired parameters
        sample_rate = get_valid_sample_rate(input_device)
        
        # Get channels once and use for both input and output
        channels = get_valid_channels(input_device, is_input=True)
        input_channels = channels
        output_channels = channels
        
        # Only ask for separate output channels if the user wants to
        if input_device != output_device:
            use_same_channels = input("Use same number of channels for output? (y/n, default: y): ").lower() != 'n'
            if not use_same_channels:
                output_channels = get_valid_channels(output_device, is_input=False)
        
        block_size = get_valid_block_size()
    else:
        # Use default values
        input_device = None
        output_device = None
        sample_rate = DEFAULT_SAMPLE_RATE
        input_channels = DEFAULT_CHANNELS
        output_channels = DEFAULT_CHANNELS
        block_size = DEFAULT_BLOCK_SIZE
        
    print("****  Starting real-time audio pass-through. Type 'stop' to end.  ****")
    print(f"\nUsing configuration:")
    print(f"Input device: {sd.query_devices(input_device)['name'] if input_device is not None else 'default'}")
    print(f"Output device: {sd.query_devices(output_device)['name'] if output_device is not None else 'default'}")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Input channels: {input_channels} ({'mono' if input_channels == 1 else 'stereo'})")
    print(f"Output channels: {output_channels} ({'mono' if output_channels == 1 else 'stereo'})")
    print(f"Block size: {block_size}")
    print("Type 'stop' and press Enter to exit.")
    print("\nBuffer usage will be displayed below:")

    try:
        with sd.InputStream(
            device=input_device,
            samplerate=sample_rate, 
            blocksize=block_size, 
            channels=input_channels,
            dtype='float32', 
            callback=audio_callback_indata
        ), sd.OutputStream(
            device=output_device,
            samplerate=sample_rate, 
            blocksize=block_size, 
            channels=output_channels,
            dtype='float32', 
            callback=audio_callback_outdata
        ):
            # Start user input thread
            input_thread = threading.Thread(target=user_input_thread)
            input_thread.start()
            
            # Wait for stop event
            stop_event.wait()
            
            print("\nStopping audio processing...")
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()