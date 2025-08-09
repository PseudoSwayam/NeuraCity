import threading
import time
from .utils.config import CAMERA_STREAMS
from .processing.stream_processor import StreamProcessor

def start_stream_processing(camera_id, stream_source):
    """
    Wrapper function to create and run a StreamProcessor instance.
    Includes robust error handling for each thread.
    """
    print(f"[Thread-{camera_id}] Starting processor for source: '{stream_source}'")
    try:
        processor = StreamProcessor(camera_id, stream_source)
        processor.run()
    except Exception as e:
        # Log any unexpected error that might crash a single stream processor thread
        print(f"[Thread-{camera_id}] FATAL ERROR: The processor has crashed.")
        print(f"[Thread-{camera_id}] Exception: {e}", exc_info=True)
    finally:
        print(f"[Thread-{camera_id}] Processor has stopped.")

if __name__ == "__main__":
    print("[Watchtower Main] Initializing NeuraCity Computer Vision Watchtower...")
    
    threads = []
    
    # --- This is your original, correct pattern: starting all threads as daemons ---
    for cam_id, source in CAMERA_STREAMS.items():
        print(f"[Watchtower Main] Configuring thread for camera: {cam_id}")
        thread = threading.Thread(
            target=start_stream_processing,
            args=(cam_id, source),
            daemon=True  # Daemon threads allow the main program to exit cleanly.
        )
        threads.append(thread)
        thread.start()
        
    print(f"[Watchtower Main] All {len(threads)} stream processing threads have been launched.")

    # This loop allows the daemon threads to run in the background indefinitely.
    # It also handles a graceful shutdown when you press Ctrl+C.
    try:
        # Give the camera streams a moment to initialize before the main loop starts
        time.sleep(2) 
        
        while True:
            # Check if any threads have unexpectedly died
            if not any(t.is_alive() for t in threads):
                print("[Watchtower Main] All processor threads have stopped unexpectedly. Shutting down.")
                break
            # This sleep is crucial. It prevents this 'while' loop from using 100% CPU.
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n[Watchtower Main] Shutdown signal (Ctrl+C) received. Exiting.")
        
    print("[Watchtower Main] Program has finished.")