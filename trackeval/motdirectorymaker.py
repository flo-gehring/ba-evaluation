import os
import argparse
import cv2
import os.path as path
from math import log10
from os import linesep

from trackformatconverter import CVATDocument, my_json_to_mot_16_dets
import sys


def make_image_directory(videopath):
    vc = cv2.VideoCapture(videopath)

    ret, frame = vc.read()

    counter = 0
    num_digits = 6

    width = vc.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = vc.get(cv2.CAP_PROP_FPS)

    while ret:
        counter += 1
        name = ('0' * ((num_digits - 1) - int(log10(counter)))) + str(counter) + ".jpg"

        cv2.imwrite(name, frame)
        ret, frame = vc.read()

    return width, height, fps, counter


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("videopath")
    parser.add_argument("cvatxmlpath")
    parser.add_argument("detectionspath")
    parser.add_argument("targetdirectory")

    args = parser.parse_args()

    directorypath = path.abspath(args.targetdirectory)

    if not path.exists(directorypath):
        os.mkdir(directorypath)

    # Make Detection Folder
    if not path.exists(path.join(directorypath, "det")):
        os.mkdir(path.join(directorypath, "det"))

    os.chdir(path.join(directorypath, "det"))
    my_json_to_mot_16_dets(args.detectionspath, "det.txt")

    os.chdir(directorypath)

    # Make Groundtruth Folder
    if not path.exists(path.join(directorypath, "gt")):
        os.mkdir("gt")

    os.chdir("gt")
    doc = CVATDocument(args.cvatxmlpath)
    doc.parse()
    doc.to_mot16_gt()

    os.chdir(directorypath)
    if not path.exists(path.join(directorypath, "img1")):
        os.mkdir("img1")

    os.chdir("img1")

    (width, height, fps, seq_length) = make_image_directory(args.videopath)


    # Write some Information about the directory
    os.chdir(directorypath)
    seqinfo = open("seqinfo.ini", "w")

    lines = ["[Sequence]",
             "name=BA",
             "imDir=img1",
             "frameRate=" + str(int(fps)) ,
             "seqLength=" + str(int(seq_length)),
             "imWidth=" + str(int(width)),
             "imHeight=" + str(int(height)),
             "imExt=.jpg"]

    # Add newline symbol to every line but the last
    for i in range(0, len(lines) - 1):
        lines[i] = lines[i] + linesep

    seqinfo.writelines(lines)
