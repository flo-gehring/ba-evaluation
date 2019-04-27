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

def create_dets(infile, skip_frames=0, bystanderfile=None):
    files = list()
    if type(infile) is list:
        for filename in infile:
            files.append(open(filename))
    else:
        files.append(open(infile))

    json_objects = [json.load(f) for f in files]

    bystander_doc = None
    if bystanderfile is not None:
        bystander_doc = CVATDocument(bystanderfile)
        bystander_doc.parse()



    unified = dict()
    for det_files in json_objects:
        for entry in det_files:
            frame_no = entry['frame']
            if frame_no not in unified:
                unified[frame_no] = list()

            for detection in entry['detections']:

                #Skip if Detection is not a person
                if 'classID' in detection and detection['classID'] != 0:
                    continue

                # Skip if detection is bystander
                if bystander_doc is not None and bystander_doc.at_frame_in_region(frame_no,
                                                                                  detection['x'],
                                                                                  detection['y'],
                                                                                  detection['width'],
                                                                                  detection['height']):
                    print("Skipped Bystander")
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


def create_gt(infile, bystander_path=None):
    gt_doc = CVATDocument(infile)
    gt_doc.parse()

    dir_name = get_filename(infile)
    get_into_dir(dir_name)

    bystander_doc = None
    if bystander_path is not None:
        bystander_doc = CVATDocument(bystander_path)
        bystander_doc.parse()


    for frame in range(0, gt_doc.max_frame + 1):

        objects_in_frame = list()

        for track in gt_doc.tracks:
            if frame in track.tracked_elements:
                frame_info = track.tracked_elements[frame].attributes

                # Skip occluded
                if not frame_info['occluded'] == "1":
                    bb_left = frame_info['xtl']
                    bb_top = frame_info['ytl']
                    bb_right = frame_info['xbr']
                    bb_bottom = frame_info['ybr']

                    # Skip bystanders
                    if bystander_doc is not None:
                        if bystander_doc.at_frame_in_region(frame,
                                                        float(bb_left), float(bb_top),
                                                        float(bb_right) - float(bb_left),
                                                        float(bb_top) - float(bb_right)):
                            print("skip bystander")
                            continue

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
    '/home/flo/PycharmProjects/ba-evaluation/data/cvatgt/TS_10_05_ohne_bs.xml',
    '/home/flo/PycharmProjects/ba-evaluation/data/cvatgt/TS_10_05_t01_ohne_bs.xml',
    '/home/flo/PycharmProjects/ba-evaluation/data/cvatgt/Video2.xml'

]

"""
for i in range(0, len(detections_gt)):
    create_gt(detections_gt[i])
    os.chdir(os.pardir)


"""


detection_files_YOLO_TS_10_05 = {
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/TS_10_5_cubemap.json',
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/TS_10_5_equator_line.json',
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/ts_10_5_yolo_whole_frame.json'

}
detection_files_YOLO_Video2 = [
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/Video2_cubemap.json',
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/Video2_equator_line.json'
    ]
detection_files_YOLE = [
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/TS_10_5_t01_cubemap.json',
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/TS_10_5_t01_equator_line.json'
]

detection_files_MASKRCNN_TS_10_5= [
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/maskrcnn/TS_10_5_whole_frame.json',

    [
        '/home/flo/PycharmProjects/ba-evaluation/data/detections/maskrcnn/TS_10_5_cubemap/0_cubemap_ts_10.json',
        '/home/flo/PycharmProjects/ba-evaluation/data/detections/maskrcnn/TS_10_5_cubemap/1_cubemap_ts_10.json',
        '/home/flo/PycharmProjects/ba-evaluation/data/detections/maskrcnn/TS_10_5_cubemap/2_cubemap_ts_10.json',
        '/home/flo/PycharmProjects/ba-evaluation/data/detections/maskrcnn/TS_10_5_cubemap/3_cubemap_ts_10.json'
    ]
]

detection_files_MASKRCNN_Video2 = [
    '/home/flo/PycharmProjects/ba-evaluation/data/detections/maskrcnn/video2_whole_frame.json'
]


create_dets("/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/608_cubemap_yolo_TS_10_5.json",
            bystanderfile='/home/flo/PycharmProjects/ba-evaluation/data/bystanders/TS_10_05 Bystanders.xml')

def create_files(det_files, bystandefile, dirname):
    get_into_dir(dirname)
    for d in det_files:
        create_dets(d, bystanderfile=bystandefile)
        os.chdir(os.pardir)
    os.chdir(os.pardir)




"""

create_dets('/home/flo/PycharmProjects/ba-evaluation/data/detections/YOLO/ts_10_5_yolo_whole_frame.json',
            bystanderfile='/home/flo/PycharmProjects/ba-evaluation/data/bystanders/TS_10_05 Bystanders.xml')
create_files(detection_files_YOLO_TS_10_05,
             '/home/flo/PycharmProjects/ba-evaluation/data/bystanders/TS_10_05 Bystanders.xml', 'YOLO')
create_files(detection_files_MASKRCNN_TS_10_5,
             '/home/flo/PycharmProjects/ba-evaluation/data/bystanders/TS_10_05 Bystanders.xml', 'Maskrcnn')
create_files(detection_files_YOLO_Video2,
             '/home/flo/PycharmProjects/ba-evaluation/data/bystanders/Video_2_Bystanders.xml', 'YOLO')
create_files(detection_files_MASKRCNN_Video2,
             '/home/flo/PycharmProjects/ba-evaluation/data/bystanders/Video_2_Bystanders.xml', 'Maskrcnn')
"""