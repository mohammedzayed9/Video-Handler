# -Automated-Video-Handler
This App is designed to simplify and automate various video processing tasks.  It provides a user-friendly interface for selecting a folder containing video files and performing specific operations on those files.

# Automated Video Handler

This App is designed to simplify and automate various video processing tasks. It provides a user-friendly interface for selecting a folder containing video files and performing specific operations on those files.

## Video Automation App

This application allows you to automate various video processing tasks using Python and PyQt5. It provides a user-friendly interface to select a folder containing videos and perform tasks such as segmentation, format conversion, audio extraction, video resizing, frame extraction, thumbnail generation, and metadata extraction.

## Features

- Segment Videos: Split videos into segments based on a specified ratio.
- Convert Format: Convert videos to a different format, such as AVI, MP4, or MOV.
- Extract Audio: Extract the audio track from videos and save it as an MP3 file.
- Resize Videos: Resize videos to different resolutions, including standard options like 144p, 240p, 360p, 480p, 720p, and 1080p.
- Extract Frames: Extract individual frames from videos and save them as JPEG images.
- Generate Thumbnails: Create thumbnail images from videos.
- Extract Metadata: Retrieve metadata information from videos, such as resolution, frame rate, duration, and codec.

## Usage

1. Select a folder containing the videos you want to process using the "Select Folder" button.
2. Choose the desired tasks to perform on the videos by checking the corresponding checkboxes.
3. Adjust any task-specific settings, such as the segment ratio, output format, resize resolution, etc.
4. Enable the "Extract Metadata" checkbox if you want to extract metadata information from the videos.
5. Click the "Process Videos" button to start the automated video processing.
6. Monitor the processing progress and current task displayed in the application window.
7. Once the processing is complete, a message will be shown indicating the success or any errors encountered.

Note: The processed videos and generated files will be saved in separate folders within the selected folder, based on the chosen tasks.

## Requirements

- Python 3.x
- PyQt5
- OpenCV (cv2)
- moviepy

## Author

Mohammed Zayed

## License

This project is licensed under the MIT License.

## Acknowledgements

- PyQt5: Python bindings for Qt framework
- OpenCV: Computer vision library
- moviepy: Video editing library

