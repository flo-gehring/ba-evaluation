import json
import os

from trackformatconverter.CVATXMLParser import CVATDocument


def get_filename(path):
    base = os.path.basename(path)
    return os.path.splitext(base)[0]

def get_into_dir(directory_name, from_dir=os.path.curdir):
    if not os.path.exists(os.path.join(from_dir, directory_name)):
        os.mkdir(directory_name)
    os.chdir(directory_name)

def create_dets(infile, skip_frames=0):
    files = list()
    if type(infile) is list:
        for filename in infile:
            files.append(open(filename))
    else:
        files.append(open(infile))

    json_objects = [json.load(f) for f in files]

    unified = dict()
    for det_files in json_objects:
        for entry in det_files:
            frame_no = entry['frame']
            if frame_no not in unified:
                unified[frame_no] = list()

            for detection in entry['detections']:
                if 'classID' in detection and detection['classID'] != 0:
                    continue

                separator = ' '
                confidence = detection['confidence']
                detection_line = separator.join([
                    'person',
                    str(confidence if confidence < 1 else confidence / 100),
                    str(detection['x']),
                    str(detection['y']),
                    str(detection['x'] + detection['width']),
                    str(detection['y'] + detection['height']),
                    os.linesep

                ])
                unified[frame_no].append(detection_line)

    for f in files:
        f.close()

    if type(infile) is list:
        outfolder = get_filename(infile[0])
    else:
        outfolder = get_filename(infile)

    get_into_dir(outfolder)

    for frame, detections in unified.items():
        frame_str = str(frame)
        current_file = open(frame_str + ".txt", "w")
        current_file.writelines(detections)
        current_file.close()

def line_formatter( frame, id, bb_left, bb_top, bb_width, bb_height, bb_occluded):
    if bb_occluded:
        return ''
    separator = ' '
    separator.join(
        'person',


    )


def create_gt(infile):
    gt_doc = CVATDocument(infile)
    gt_doc.parse()

    dir_name = get_filename(infile)
    get_into_dir(dir_name)

    for frame in range(0, gt_doc.max_frame + 1):

        objects_in_frame = list()

        for track in gt_doc.tracks:
            if frame in track.tracked_elements:
                frame_info = track.tracked_elements[frame].attributes

                if not frame_info['occluded'] == "1":
                    bb_left = frame_info['xtl']
                    bb_top = frame_info['ytl']
                    bb_right = frame_info['xbr']
                    bb_bottom = frame_info['ybr']
                    object_line = ' '.join([
                        'person',
                        bb_left,
                        bb_top,
                        bb_right,
                        bb_bottom,
                        os.linesep
                    ]
                    )
                    objects_in_frame.append(object_line)
        out_file = open(str(frame) + ".txt", 'w')
        out_file.writelines(objects_in_frame)
        out_file.close()






detections_gt = [
    '/home/flo/PycharmProjects/ba-evaluation/data/cvatgt/TS_10_5.xml',
    '/home/flo/PycharmProjects/ba-evaluation/data/cvatgt/TS_10_5_t01_kv.xml',
    '/home/flo/PycharmProjects/ba-evaluation/data/cvatgt/Video2.xml'

]

for d in detections_gt:
    create_gt(d)
    os.chdir(os.pardir)



detection_files_YOLO = [
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/TS_10_5_cubemap.json',
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/TS_10_5_equator_line.json',
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/TS_10_5_t01_cubemap.json',
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/TS_10_5_t01_equator_line.json',
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/Video2_cubemap.json',
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/Video2_equator_line.json'
]
detection_files_MASKRCNN = [
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/maskrcnn/TS_10_5_whole_frame.json',
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/maskrcnn/video2_whole_frame.json',
    [
        '/home/flo/PycharmProjects/ba-evaluation/data/detections/maskrcnn/TS_10_5_cubemap/0_cubemap_ts_10.json',
        '/home/flo/PycharmProjects/ba-evaluation/data/detections/maskrcnn/TS_10_5_cubemap/1_cubemap_ts_10.json',
        '/home/flo/PycharmProjects/ba-evaluation/data/detections/maskrcnn/TS_10_5_cubemap/2_cubemap_ts_10.json',
        '/home/flo/PycharmProjects/ba-evaluation/data/detections/maskrcnn/TS_10_5_cubemap/3_cubemap_ts_10.json'
    ]
]

"""
for d in detection_files_MASKRCNN:
    create_dets(d)
    os.chdir(os.pardir)

"""