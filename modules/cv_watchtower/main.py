import threading
from .utils.config import CAMERA_STREAMS
from .processing.stream_processor import StreamProcessor

def start_stream_processing(camera_id, stream_source):
    """Wrapper function to create and run a StreamProcessor instance."""
    processor = StreamProcessor(camera_id, stream_source)
    processor.run()

if __name__ == "__main__":
    print("[Watchtower Main] Initializing NeuraCity Computer Vision Watchtower...")
    
    threads = []
    
    # Create and start a new thread for each camera stream
    for cam_id, source in CAMERA_STREAMS.items():
        print(f"[Watchtower Main] Creating thread for camera: {cam_id}")
        thread = threading.Thread(
            target=start_stream_processing,
            args=(cam_id, source),
            daemon=True  # Allows main thread to exit even if streams are running
        )
        threads.append(thread)
        thread.start()
        
    # Keep the main thread alive to allow daemon threads to run
    for thread in threads:
        thread.join()
        
    print("[Watchtower Main] All streams have finished. Exiting.")