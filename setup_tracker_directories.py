import os
import cv2
import os.path as path
from math import log10
from os import linesep
from trackformatconverter import CVATDocument, my_json_to_mot_16_dets


def get_filename(path):
    base = os.path.basename(path)
    return os.path.splitext(base)[0]


def get_into_dir(directory_name, from_dir=os.path.curdir):
    if not os.path.exists(os.path.join(from_dir, directory_name)):
        os.mkdir(directory_name)
    os.chdir(directory_name)


def make_deepsort_directory(videopath, cvatxmlpath, detectionspath, directorypath):

    if not path.exists(directorypath):
        os.mkdir(directorypath)

    # Make Detection Folder
    if not path.exists(path.join(directorypath, "det")):
        os.mkdir(path.join(directorypath, "det"))

    os.chdir(path.join(directorypath, "det"))
    my_json_to_mot_16_dets(detectionspath, "det.txt")

    os.chdir(directorypath)

    # Make Groundtruth Folder
    if not path.exists(path.join(directorypath, "gt")):
        os.mkdir("gt")

    os.chdir("gt")
    doc = CVATDocument(cvatxmlpath)
    doc.parse()
    doc.to_mot16_gt()

    os.chdir(directorypath)
    if not path.exists(path.join(directorypath, "img1")):
        os.mkdir("img1")

    os.chdir("img1")

    (width, height, fps, seq_length) = make_image_directory(videopath)

    # Write some Information about the directory
    os.chdir(directorypath)
    seqinfo = open("seqinfo.ini", "w")

    lines = ["[Sequence]",
             "name=BA",
             "imDir=img1",
             "frameRate=" + str(int(fps)),
             "seqLength=" + str(int(seq_length)),
             "imWidth=" + str(int(width)),
             "imHeight=" + str(int(height)),
             "imExt=.jpg"]

    # Add newline symbol to every line but the last
    for i in range(0, len(lines) - 1):
        lines[i] = lines[i] + linesep

    seqinfo.writelines(lines)


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


def setup_smot_tracker(cvatdoc, path_to_video, path_to_smot_data, skip_img_dir_if_exists=False):

    current_path = os.path.curdir

    abs_smot_data_path = os.path.abspath(path_to_smot_data)
    abs_path_to_video = os.path.abspath(path_to_video)

    os.chdir(abs_smot_data_path)
    video_name = get_filename(path_to_video)

    get_into_dir(video_name)
    img_dir_name = "img"

    if not (os.path.exists(os.path.join(os.curdir, img_dir_name)) and skip_img_dir_if_exists):
        get_into_dir(img_dir_name)

    make_image_directory(abs_path_to_video)
    os.chdir(os.pardir)
    cvatdoc.to_smot_itl_format(video_name + ".itl")


if __name__ == "__main__":
    cvatdoc = CVATDocument()
    cvatdoc.MOT_to_CVAT_parsetree("./data/mot_fmt_results/panorama_tracker_TS_10_5.txt", delimiter='\t')
    setup_smot_tracker(cvatdoc, '/home/flo/Videos/TS_10_5.mp4', '/home/flo/Workspace/OtherTrackers/smot/smot_data/',
                   skip_img_dir_if_exists=True)
