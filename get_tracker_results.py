import numpy as np
from scipy.io import loadmat
from trackformatconverter import Track, CVATDocument, Box
import json


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


def get_smot_tracker_data(path_to_mat, outfilepath, cvat_object):
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



cvat_doc = CVATDocument("/home/flo/CLionProjects/Panorama2Cubemap/data/Annotations/2_TS_10_05.xml")
cvat_doc.parse()
output_doc = get_smot_tracker_data('/home/flo/Workspace/OtherTrackers/smot/smot_data/TS_10_5/ihtls/TS_10_5_ihtls_fn.mat', "", cvat_doc)
output_doc.to_format("MOT16", 'smot_TS_10_5.txt')
