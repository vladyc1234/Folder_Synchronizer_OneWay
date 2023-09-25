import logging
import pathlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import shutil
import argparse

class ConsoleArguments:
    def __init__(self):
        # Create an ArgumentParser
        self.parser = argparse.ArgumentParser(description='Example script with command-line arguments')

        # Add arguments
        self.parser.add_argument('src_folder', type=str, help='Path to the source folder')
        self.parser.add_argument('dst_folder', type=str, help='Path to the destination folder')
        self.parser.add_argument('log_file', type=str, help='Path to the log file')
        self.parser.add_argument('--interval', type=int, default=3,
                            help='Set how often synchronization should be performed periodically')

        # Parse the command-line arguments
        self.args = self.parser.parse_args()

# Define object that handles console arguments
console_arguments = ConsoleArguments()


# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the logger's global level to DEBUG

# Create a console handler and set its level to display messages on the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Set the console handler's level to INFO

# Create a file handler to log messages to a file
if pathlib.Path(console_arguments.args.log_file) not in pathlib.Path("E:").iterdir():
    open(console_arguments.args.log_file, "w")

file_handler = logging.FileHandler(console_arguments.args.log_file)
file_handler.setLevel(logging.INFO)  # Set the file handler's level to DEBUG

# Create a formatter to define the log message format
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Set the formatter for both handlers
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# List of files to sync to
# Example: [["move", [path (string), path]],
#           ["create", path],
#           ["delete", path],
#           ["modify", path]]
changes = []

# Define the main application code
class FolderSyncer(object):
    def __init__(self, src, dst):
        # Define paths
        self.source_path = src
        self.destination_path = dst
        self.interval = console_arguments.args.interval  # Interval in seconds
        self.last_action_time = time.time()
        logger.debug(f"\nSource path:\t\t{self.source_path}\n"
                      f"Destination path:\t{self.destination_path}")
        # Make a file system observer
        self.observer = Observer()
        # Schedule it with our EventHandler(), the path, and recursive
        self.observer.schedule(EventHandler(), str(self.source_path), recursive=True)
        # If we are completely synced
        self.synced = False

    def __enter__(self):
        logging.debug("Entered the Folder Syncer")
        # Start the observer
        self.observer.start()
        # Must return self for context managers
        return self

    def run(self):
        while True:
            self.current_time = time.time()
            if self.current_time - self.last_action_time >= self.interval:
                for item in self.source_path.iterdir():
                    if item.is_file():
                        # Write the file's contents
                        (self.destination_path / str(item).replace(str(self.source_path), "")[1:]).write_bytes(
                            pathlib.Path(str(item)).read_bytes()
                        )
                    # Else, it's a directory
                    else:
                        try:
                            # Copy folder recursively
                            shutil.copytree(item, self.destination_path / str(item).replace(str(self.source_path), "")[1:])
                        except FileExistsError:
                            pass
                    logging.debug(f"Finished handling {item}")
                self.last_action_time = self.current_time

            if len(changes) > 0:
                # Remove first change from queue
                change = changes.pop(0)
                # We are still handling changes, so we are not synced
                self.synced = False
                logging.debug(f"Handling {change[0]} from {change[1]}")
                # Handle change here, pretend to do something
                if change[0] == "move":
                    (self.destination_path / change[1][0].replace(str(self.source_path), "")[1:]).replace(
                        self.destination_path / change[1][1].replace(str(self.source_path), "")[1:]
                    )
                elif change[0] == "create":
                    # If it's a file
                    if pathlib.Path(change[1]).is_file():
                        # Write the file's contents
                        (self.destination_path / change[1].replace(str(self.source_path), "")[1:]).write_bytes(
                            pathlib.Path(change[1]).read_bytes()
                        )
                    # Else, it's a directory
                    else:
                        (self.destination_path / change[1].replace(str(self.source_path), "")[1:]).mkdir(exist_ok=True)
                elif change[0] == "delete":
                    try:
                        # Try to remove as file
                        (self.destination_path / change[1].replace(str(self.source_path), "")[1:]).unlink()
                    except PermissionError:
                        # It's a directory, so remove it as a directory
                        (self.destination_path / change[1].replace(str(self.source_path), "")[1:]).rmdir()
                    except FileNotFoundError:
                        pass
                elif change[0] == "modify":
                    try:
                        (self.destination_path / change[1].replace(str(self.source_path), "")[1:]).write_bytes(
                            pathlib.Path(change[1]).read_bytes()
                        )
                    except PermissionError:
                        pass
                logging.info(f"Finished handling {change[0]} from {change[1]}, {len(changes)} changes left!")
            else:
                if not self.synced:
                    self.synced = True
                    logging.info("You are all completely synced!")
                    time.sleep(1)

    def __exit__(self, exc_type, exc_value, traceback):
        logging.warning("Exited the Folder Syncer")
        # Stop the observer
        self.observer.stop()
        # Join the observer to the current thread
        self.observer.join()


# Define an event handler
class EventHandler(FileSystemEventHandler):
    def on_moved(self, event):
        super(EventHandler, self).on_moved(event)
        what = "directory" if event.is_directory else "file"
        logging.debug(f"Moved {what}: from {event.src_path} to {event.dest_path}")
        changes.append(["move", [event.src_path, event.dest_path]])

    def on_created(self, event):
        super(EventHandler, self).on_created(event)
        what = "directory" if event.is_directory else "file"
        logging.debug(f"Created {what}: {event.src_path}")
        changes.append(["create", event.src_path])

    def on_deleted(self, event):
        super(EventHandler, self).on_deleted(event)
        what = "directory" if event.is_directory else "file"
        logging.debug(f"Deleted {what}: {event.src_path}")
        changes.append(["delete", event.src_path])

    def on_modified(self, event):
        super(EventHandler, self).on_modified(event)
        what = "directory" if event.is_directory else "file"
        logging.debug(f"Modified {what}: {event.src_path}")
        changes.append(["modify", event.src_path])

with FolderSyncer(pathlib.Path(console_arguments.args.src_folder), pathlib.Path(console_arguments.args.dst_folder)) as folder_syncer:
    folder_syncer.run()