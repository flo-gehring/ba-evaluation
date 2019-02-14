
from trackformatconverter import CVATDocument
import sys
import os
from trackeval import make_image_directory


def get_filename(path):
    base = os.path.basename(path)
    return os.path.splitext(base)[0]


def get_into_dir(directory_name, from_dir=os.path.curdir):
    if not os.path.exists(os.path.join(from_dir, directory_name)):
        os.mkdir(directory_name)
    os.chdir(directory_name)


def setup_smot_tracker(path_to_cvat_gt, path_to_video, path_to_smot_data, skip_img_dir_if_exists=False):

    cvatdoc = CVATDocument(path_to_cvat_gt)
    cvatdoc.parse()

    current_path = os.path.curdir

    abs_smot_data_path = os.path.abspath(path_to_smot_data)
    abs_path_to_video = os.path.abspath(path_to_video)

    os.chdir(abs_smot_data_path)
    video_name = get_filename(path_to_video)

    get_into_dir(video_name)
    img_dir_name = "img"

    if not os.path.exists(os.path.join(os.curdir, img_dir_name)) or not skip_img_dir_if_exists:
        get_into_dir(img_dir_name)

    make_image_directory(abs_path_to_video)
    os.chdir(os.pardir)
    cvatdoc.to_smot_itl_format(video_name + ".itl")


setup_smot_tracker('/home/flo/CLionProjects/Panorama2Cubemap/data/Annotations/2_TS_10_05.xml', '/home/flo/Videos/TS_10_5.mp4', '/home/flo/Workspace/OtherTrackers/smot/smot_data/')