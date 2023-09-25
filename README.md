# Folder_Synchronizer_OneWay

## Operating System:

- Windows 10 Pro (Version 22H2)

## Compiler:

- Python 3.9

## Apps Used:

- Pycharm Community edition

## Libraries:

* pip 23.2.1
* setuptools 68.2.2 - notable libraries used:
* watchdog 3.0.0

## How to use:

1. Open your PyCharm, download the necessary libraries and copy the script 

2. Create/Select two folders

3. Create/Select a text file for logging purposes (optional)

4. Run the script and provide paths for the two folders, logging file and synchronization interval (command format: python name_of_your_project.py folder_path(source)(string) folder_path(destination)(string) synchronization_interval(optional)(integer)

Results: The script will start the synchronization in a one way manner from source to destination

## How does the script work

1. Parsing Command-Line Arguments: The ConsoleArguments class is defined to parse command-line arguments. It defines four required arguments: src_folder (source folder path), dst_folder (destination folder path), log_file (path to the log file), and an optional --interval argument to set the synchronization interval. These arguments are specified when running the script.

2. Logger Setup: The script sets up a logger to record messages. It configures both a console handler (for displaying messages on the console) and a file handler (for writing messages to a log file). The log messages include timestamps, log levels (INFO, DEBUG, etc.), and the actual log message content.

3. List of Changes: The changes list is initialized as an empty list. This list will be used to keep track of file system changes (e.g., file creation, modification, deletion, movement) that need to be synchronized between the source and destination folders.

4. FolderSyncer Class: The FolderSyncer class is defined to handle folder synchronization. It is initialized with the source and destination folder paths.
  *The __enter__ method starts a file system observer from the Watchdog library and returns the FolderSyncer instance.
  *The __run__ method is the main loop of the synchronization process. It continuously checks for changes in the source folder and performs the necessary actions to synchronize files and directories with the destination folder.
  *The __exit__ method stops the file system observer when the with block is exited.

5. EventHandler Class: The EventHandler class is a subclass of FileSystemEventHandler from the Watchdog library. It overrides methods to handle specific file system events (e.g., on_moved, on_created, on_deleted, on_modified) and adds the corresponding change to the changes list.

6. Folder Synchronization: The script uses an instance of the FolderSyncer class to monitor and synchronize the source and destination folders. The with block ensures that the file system observer is properly started and stopped.

Overall, this script provides a basic framework for real-time folder synchronization, monitoring changes in the source folder, and applying those changes to the destination folder. The script is configured using command-line arguments, and log messages are generated to track the synchronization process and any detected file system events.
	

		

