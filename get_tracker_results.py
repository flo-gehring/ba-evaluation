from scipy.io import loadmat
from trackformatconverter import Track, CVATDocument, Box
from os.path import splitext, split
from setup_tracker_directories import get_into_dir
import os


def get_file_name(path):
    return splitext(split(path)[1])[0]

def track_from_itlf_entry(itlf_entry):
    track_obj = Track()
    current_frame_index = itlf_entry['t_start'][0][0][0]
    track_length = itlf_entry['length'][0][0][0]
    data_entry = itlf_entry['data']

    frame_coords = dict()
    for x,y in data_entry:
        x_list = x.tolist()
        y_list = y.tolist()
        for i in range(0, track_length):
           frame_coords[i + current_frame_index] = (x_list[i], y_list[i])

    return frame_coords


def get_smot_tracker_data(path_to_mat, cvat_object):
    """
    Loads a Mat file as produced by the smot tracker and returns a CVAT Document.
    :param path_to_mat:
    :return trackformatconverter.CVATDocument:
    """
    tracking_result = loadmat(path_to_mat)

    itlf = tracking_result['itlf'][0][0]

    frame_coords = list()

    for data in itlf['data']:
        for i in range(0, data.size):
            frame_coords.append(list())
            track_i = data[0:data.size][i]
            for f in range(0, len(track_i[0])):
                x = track_i[0][f]
                y = track_i[1][f]
                #print(str(x) + ", " + str(y))
                frame_coords[i].append((x, y))

    track_starts = list()
    for start in itlf['t_start']:
        for i in range(0, start.size):
            track_starts.append(list())
            track_i = start[0:start.size][i]
            for f in range(0, len(track_i[0])):
                s = track_i[0]
                # print(str(x) + ", " + str(y))
                track_starts[i].append(s)

    occluded_list = list()
    for occluded in itlf['omega']:
        for i in range(0, occluded.size):
            occluded_i = occluded[i]
            occluded_list.append(occluded_i)

    cvat_output = CVATDocument()
    # We now need to restore the detections!
    for i in range(0, len(track_starts)):
        cvat_output.tracks.append(Track())
        current_track = cvat_output.tracks[-1]

        start_frame = track_starts[i][0].tolist()[0]

        track_coords = frame_coords[i]
        track_occluded = occluded_list[i]

        for frame_offset in range(0, len(track_coords)):
            box = Box()
            x, y = track_coords[frame_offset]
            x = float(x)
            y = float(y)
            cvat_output.max_frame = max(cvat_output.max_frame, start_frame + len(track_coords))
            frame_num = start_frame + frame_offset
            xtl, ytl, xbr, ybr = (0, 0, 0, 0)
            for track in cvat_object.tracks:
                if frame_num in track.tracked_elements and track.tracked_elements[frame_num].point_in_box(x, y):
                    correct_box = track.tracked_elements[frame_num]
                    box.attributes = correct_box.attributes
                    break
            else: # No Box found, make 20 by 40 box
                box.attributes['xtl'] = x - 10
                box.attributes['ytl'] = y - 20
                box.attributes['xbr'] = x + 10
                box.attributes['ybr'] = x + 20
                box.attributes['occluded'] = "0"
            current_track.tracked_elements[frame_num] = box

    return cvat_output


def create_smot_mot_fmt_dir(
        gt_data_path="/home/flo/PycharmProjects/ba-evaluation/data/cvatgt/Video2.xml",
        matlab_result='/home/flo/Workspace/OtherTrackers/smot/smot_data/Video2/ihtls/Video2_ihtls_fn.mat',
        mot_fmt_path='/home/flo/PycharmProjects/ba-evaluation/data/mot_fmt_results/Video2.txt'):
    # "/home/flo/CLionProjects/Panorama2Cubemap/data/Annotations/2_TS_10_05.xml"
    cvat_doc = CVATDocument(gt_data_path)
    cvat_doc.parse()
    # '/home/flo/Workspace/OtherTrackers/smot/smot_data/TS_10_5/ihtls/TS_10_5_ihtls_fn.mat'
    output_doc = \
        get_smot_tracker_data(matlab_result, cvat_doc)

    output_doc.to_format("MOT16", mot_fmt_path)



def create_evaluation_test_directory(eval_root, path_to_mot_fmt_result, path_to_gt,
                                     tracker_name, sequence_name, bystander_path=None):
    """
    Sets up a directory structure like:

    ---------
    Layout for ground truth data
    "eval_root"/groundtruths/"sequence_name"/gt/gt.txt
    ...
    Layout for test data
    "eval_root"/"tracker_name"/"sequence_name".txt
    <TEST_ROOT>/<SEQUENCE_2>.txt
    :param eval_root: Directory where all the evaluation data is stored
    :param path_to_mot_fmt_result:  Result of the tracker, stored in MOT16 Format
    :param path_to_gt: Path to the GT, stored in the xml format OpenCVAT produces.
    :param tracker_name: Name of the Tracker.
    :param sequence_name: Name of the video
    :return None: Side Effects: Creations of several Directories.
    """
    bystander_doc = None
    if bystander_path is not None:
        bystander_doc = CVATDocument(bystander_path)
        bystander_doc.parse()


    abs_result_path = os.path.abspath(path_to_mot_fmt_result)
    abs_gt_path = os.path.abspath(path_to_gt)

    os.chdir(eval_root)

    get_into_dir('groundtruths')
    if os.path.exists(sequence_name):
        print("Ground truth Directory with given Sequence Name found, Ground truth setup skipped.")
        os.chdir(os.pardir)
    else:
        print("Creating GT.. ")
        get_into_dir(sequence_name)
        get_into_dir('gt')
        gt_doc = CVATDocument(abs_gt_path)
        gt_doc.parse()
        if bystander_doc is not None:
            gt_doc.delete_bystanders(bystander_doc)
        gt_doc.to_mot16_gt('gt.txt', tab_delimiter=True)
        print("Groundtruth created..")
        os.chdir(eval_root)

    get_into_dir(tracker_name)
    result_doc = CVATDocument()
    result_doc.MOT_to_CVAT_parsetree(abs_result_path)
    if bystander_doc is not None:
        result_doc.delete_bystanders(bystander_doc)
    result_doc.to_mot_metrics_fmt(sequence_name + '.txt')

if __name__ == "__main__":

    #create_smot_mot_fmt_dir()

    cvat_doc = CVATDocument("/home/flo/CLionProjects/Panorama2Cubemap/data/Annotations/2_TS_10_05.xml")
    cvat_doc.parse()
    """
    output_doc = get_smot_tracker_data(
        '/home/flo/Workspace/OtherTrackers/smot/smot_data/TS_10_5/ihtls/TS_10_5_ihtls_fn.mat'
        , cvat_doc)
    output_doc.to_format("MOT16", 'data/mot_fmt_results/smot_TS_10_5.txt')
    """

    data_directory = "/home/flo/PycharmProjects/ba-evaluation/data/"

    create_evaluation_test_directory(data_directory + "eval_root/", data_directory + "mot_fmt_results/smot_Video2.txt",
                        data_directory + "cvatgt/Video2.xml", "DEEPSORT", "Video2",
                        bystander_path="/home/flo/PycharmProjects/ba-evaluation/data/bystanders/Video_2_Bystanders.xml")

