# File: check_memory.py
# A simple script to inspect the contents of your MemoryCore databases.
# Corrected for Python 3.9+ f-string compatibility.

print("--- 🧠 NeuraCity Memory Inspector ---")

try:
    from memorycore.memory_manager import get_memory_core

    # Get the singleton instance of the memory manager
    memory = get_memory_core()

    # --- 1. Inspecting Structured Memory (SQLite) ---
    print("\n--- 📝 Checking Structured Memory (Events Log) ---")
    try:
        # Use a direct query to inspect the database contents
        recent_events = memory.structured.conn.cursor().execute(
            "SELECT * FROM events ORDER BY timestamp DESC LIMIT 5"
        ).fetchall()
        
        if not recent_events:
            print("No events found in structured memory.")
        else:
            print(f"Found {len(recent_events)} recent event(s). Latest entry:")
            latest_event = dict(recent_events[0])
            print(f"  - Timestamp: {latest_event['timestamp']}")
            print(f"  - Source:    {latest_event['source']}")
            print(f"  - Type:      {latest_event['type']}")
            print(f"  - Details:   {latest_event['details']}")
            
    except Exception as e:
        print(f"Could not check structured memory: {e}")


    # --- 2. Inspecting Vector Memory (ChromaDB) ---
    print("\n\n--- 🧠 Checking Vector Memory (Conversations & Docs) ---")
    try:
        collection = memory.vector.collection
        
        count = collection.count()
        print(f"Total items in vector memory collection: {count}")
        
        if count > 0:
            print("\nPeeking at the first 5 items...")
            peek_result = collection.peek(limit=5)
            
            # Check if 'documents' key exists and is not empty
            if peek_result and peek_result.get('documents'):
                for i in range(len(peek_result['ids'])):
                    print(f"\nItem {i+1}:")
                    # --- THIS IS THE FIX ---
                    # 1. Get the original document text.
                    original_doc = peek_result['documents'][i]
                    # 2. Perform the replace operation outside the f-string.
                    cleaned_doc = original_doc.replace('\n', ' ')
                    # 3. Use the cleaned variable in the f-string.
                    print(f"  - ID:       {peek_result['ids'][i]}")
                    print(f"  - Document: {cleaned_doc}")
                    print(f"  - Metadata: {peek_result['metadatas'][i]}")
            else:
                print("Peek result is empty or missing 'documents' key.")
        else:
            print("No items found in vector memory.")
            
    except Exception as e:
        print(f"Could not check vector memory: {e}")

except ImportError as e:
    print("\n--- ERROR ---")
    print(f"Could not import MemoryCore: {e}")
    print("Please ensure you are running this script from the project's root 'NeuraCity' directory,")
    print("and that your virtual environment is active.")

finally:
    print("\n--- ✅ Inspection Complete ---")