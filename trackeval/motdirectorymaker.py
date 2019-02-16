import argparse
import os.path as path
import setup_tracker_directories
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Sets up an directory for the deepsort Tracker. "
                                                 "Most of the functionality is in setup_tracker_directories.py")
    parser.add_argument("videopath")
    parser.add_argument("cvatxmlpath")
    parser.add_argument("detectionspath")
    parser.add_argument("targetdirectory")

    args = parser.parse_args()
    directorypath = path.abspath(args.targetdirectory)

    video_path = args.videopath
    cvat_xml_path = args.cvatxmlpath
    detections_path = args.detectionspath

    setup_tracker_directories.make_deepsort_directory(video_path, cvat_xml_path, detections_path, directorypath)
