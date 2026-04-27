"""What happens without thread.join()? Main races ahead."""
import threading, time

def download(name):
    print(f"  {name} downloaded!")

# t = threading.Thread(target=download, args=("file.zip",))
# t.start()
# print("  Main: All done!")
# time.sleep(3)

print("\n=== With join ===")
t = threading.Thread(target=download, args=("file.zip",))
t.start()
t.join()
print("  Main: All done!")
