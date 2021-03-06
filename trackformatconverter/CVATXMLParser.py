#! /usr/bin/python

import xml.etree.ElementTree as ET
from copy import deepcopy
import json
import csv
from os import linesep
import argparse


class Track:
        def __init__(self):
                self.tracked_elements = dict()

        def from_to_frame(self):
            from_frame = min(self.tracked_elements.keys())
            to_frame = max(self.tracked_elements.keys())

            return (from_frame, to_frame)


class Box:
        def __init__(self, xml_node=None):
            if xml_node is not None:
                self.attributes = deepcopy(xml_node.attrib)
                self.xtl = float(self.attributes['xtl'])
                self.ytl = float(self.attributes['ytl'])
                self.ybr = float(self.attributes['ybr'])
                self.xbr = float(self.attributes['xbr'])

            else:
                self.attributes = dict()

        def point_in_box(self, x, y):
            horizontally_inside = float(self.attributes['xtl']) < x < float(self.attributes['xbr'])
            vertically_inside = float(self.attributes['ytl']) < y < float(self.attributes['ybr'])
            return horizontally_inside and vertically_inside

        def corner_points(self):
            return (self.attributes['xtl'], self.attributes['ytl']), (self.attributes['xbr'], self.attributes['ybr'])

        def top_right_width_height(self):
            xtl = float(self.attributes['xtl'])
            ytl = float(self.attributes['ytl'])
            width = float(self.attributes['xbr']) - xtl
            height = float(self.attributes['ybr']) - ytl
            return (xtl, ytl), (width, height)

        def in_area(self, a_xtl, a_ytl, a_width, a_height):
            to_return = a_xtl <= self.xtl \
                   and a_ytl <= self.ytl \
                   and a_xtl + a_width >= self.xbr \
                   and a_ytl + a_height >= self.ybr
            return to_return




class Polygon:
        def __init__(self, xml_node):
                self.attributes = deepcopy(xml_node.attrib)


class CVATDocument:

        def __init__(self, filepath=''):
            self.tracks = list()
            self.max_frame = 0
            self.doc_tree = None
            if filepath is not '':
                    self.doc_tree = ET.parse(filepath)

        def open_doc(self, filepath):
                self.doc_tree = ET.parse(filepath)

        def parse(self):
            if self.doc_tree is None:
                        raise ValueError("Doc Tree is none")

            root = self.doc_tree.getroot()
            self.max_frame = 0

            for child in root:
                    if child.tag == 'track':
                        new_track = Track()
                        for node in child:
                                frame = int(node.attrib['frame'])
                                self.max_frame = max(self.max_frame, frame)
                                new_track.tracked_elements[frame] = parse_node(node)
                        self.tracks.append(new_track)


        def iterate_frame_wise(self, line_formatter, output_path=''):
            """
            Iterate for framewise over the tracked object and print the strings produced by line_formatter.
            If an output path is given it will be printed to the file, else to the console.
            :param line_formatter:
            :param output_path:
            :return:
            """
            output_file = None
            if not output_path == '':
                output_file = open(output_path, "w")

            for frame in range(0, (self.max_frame + 1)):
                for track in self.tracks:
                    if frame in track.tracked_elements:
                        frame_info = track.tracked_elements[frame].attributes

                        bb_left = float(frame_info['xtl'])
                        bb_top = float(frame_info['ytl'])
                        bb_width = float(frame_info['xbr']) - bb_left
                        bb_height = float(frame_info['ybr']) - bb_top
                        bb_occluded = frame_info['occluded'] == "1"

                        formatted_line = line_formatter(
                                frame,
                                self.tracks.index(track),
                                bb_left, bb_top, bb_width,
                                bb_height, bb_occluded)

                        if output_file is not None:
                                output_file.write(formatted_line)
                        else:
                                print(formatted_line)


        def at_frame_in_region(self, frame, x, y, width, height):
            """
            Returns True if the given coordinates fall into a track on the specified frame.
            :param frame:
            :param x:
            :param y:
            :param width:
            :param height:
            :return:
            """
            for track in self.tracks:
                if frame in track.tracked_elements:
                    element = track.tracked_elements[frame]
                    if element.xtl <= x and element.ytl <= y and element.xbr >= x + width and element.ybr >= y + height:
                        return True
            return False


        def to_format(self, format_id, filepath='',  dets_only=False, include_occluded=True, delimiter=', '):
            """
            MOT Format is used for the Multiple Object Tracking Benchmark.
            Documented on their [Website](https://motchallenge.net/instructions/) under the section Format.
            conf will be 0, x,y and z will always be -1.
            <id> will simply the position of the track in the list.

            <frame>, <id>, <bb_left>, <bb_top>, <bb_width>, <bb_height>, <conf>, <x>, <y>, <z>
            1, 3, 794.27, 247.59, 71.245, 174.88, -1, -1, -1, -1
            1, 6, 1648.1, 119.61, 66.504, 163.24, -1, -1, -1, -1
            1, 8, 875.49, 399.98, 95.303, 233.93, -1, -1, -1, -1
            """
            output_file = None
            if not filepath == '':
                output_file = open(filepath, "w")

            line_format = "{0}" + delimiter + "{1}" + \
                          delimiter + "{2}" + delimiter + "{3}" + delimiter + "{4}" + delimiter + \
                          "{5}" + delimiter + "{6}" + delimiter + \
                          "{7}" + delimiter + "{7}" + delimiter + "{7} \n"
            uniqueId = 0
            if format_id in ["2D MOT 2015", "MOT16", "PETS2017", "MOT17"]:
                        for frame in range(0, (self.max_frame + 1)):
                                for track in self.tracks:
                                        if frame in track.tracked_elements:
                                                frame_info = track.tracked_elements[frame].attributes

                                                if include_occluded or not bool(frame_info['occluded']):

                                                    bb_left = float(frame_info['xtl'])
                                                    bb_top = float(frame_info['ytl'])
                                                    bb_width = float(frame_info['xbr']) - bb_left
                                                    bb_height = float(frame_info['ybr']) - bb_top
                                                    bb_occluded = frame_info['occluded'] == "1"

                                                    formatted_line = line_format.format(
                                                                            frame,
                                                                            -1 if dets_only else self.tracks.index(track),
                                                                            bb_left, bb_top, bb_width,
                                                                            bb_height, int(not bb_occluded), -1)

                                                    if output_file is not None:
                                                            output_file.write(formatted_line)
                                                    else:
                                                        print(formatted_line)

        def to_mot16_gt(self, filepath='', tab_delimiter=False):
            output_file = None
            if not filepath == '':
                output_file = open(filepath, "w")
            for track in self.tracks:
                track_id = self.tracks.index(track)
                for frame in range(0, (self.max_frame + 1)):
                    if frame in track.tracked_elements:

                        frame_info = track.tracked_elements[frame].attributes
                        bb_left = float(frame_info['xtl'])
                        bb_top = float(frame_info['ytl'])
                        bb_width = float(frame_info['xbr']) - bb_left
                        bb_height = float(frame_info['ybr']) - bb_top

                        bb_occluded = frame_info['occluded'] == "1"

                        if tab_delimiter:
                            formatted_line = "{0}\t{1}\t{2}\t{3}\t{4}\t" \
                                             "{5}\t{6}\t{7}\t{7}\t{7} \n".format(frame, track_id, bb_left, bb_top,
                                                                                 bb_width,
                                                                                 bb_height, 0 if bb_occluded else 1, 1)
                        else:
                            formatted_line = "{0}, {1}, {2}, {3}, {4}, " \
                                         "{5}, {6}, {7}, {7}, {7} \n".format(frame, track_id, bb_left, bb_top, bb_width,
                                                                             bb_height, 0 if bb_occluded else 1, 1)
                        if output_file is not None:
                            output_file.write(formatted_line)
                        else:
                            print(formatted_line)

        def to_mot_metrics_fmt(self, doc_path):
            formatter = lambda frame, index, bb_left, bb_top, bb_width, bb_height, bb_occluded: '\t'.join(
                [str(x) for x in [frame, index, bb_left, bb_top, bb_width, bb_height, 1, 1, 0 if bb_occluded else 1, 0]]
            ) + linesep
            self.iterate_frame_wise(formatter, doc_path)

        def sloth_format_json_factory(self, groundtruth=False):
            """
            Produces a JSON Compatible String representing the Groundtruth or Tracking Results.
            :param groundtruth:
            :return:
            """
            sloth_representation = [{'frames': []}]

            sloth_representation[0]['class'] = 'video'
            sloth_representation[0]['filename'] = 'dontcare.mp4'

            frames_list = sloth_representation[0]['frames']

            for frame in range(0, self.max_frame + 1):
                frames_list.append({
                    'timestamp': frame,
                    'frame': frame,
                    'class': 'frame',
                })
                annotation_list = None
                if not groundtruth:
                    frames_list[-1]['hypotheses'] = list()
                    annotation_list = frames_list[-1]['hypotheses']
                else:
                    frames_list[-1]['annotations'] = list()
                    annotation_list = frames_list[-1]['annotations']

                for track in self.tracks:
                    if frame in track.tracked_elements:
                        annotation_list.append(dict())
                        current_annotation = annotation_list[-1]

                        frame_info = track.tracked_elements[frame].attributes
                        bb_left = float(frame_info['xtl'])
                        bb_top = float(frame_info['ytl'])
                        current_annotation['width'] = float(frame_info['xbr']) - bb_left
                        current_annotation['height'] = float(frame_info['ybr']) - bb_top

                        current_annotation['x'] = bb_left
                        current_annotation['y'] = bb_top

                        current_annotation['id'] = self.tracks.index(track)

                        if groundtruth:
                            current_annotation['dco'] = bool(float(frame_info['outside'])) or\
                                                        bool(float(frame_info['occluded']))

            return sloth_representation

        def to_sloth_format(self, groundtruth=False, output_path=''):
            """
            Convenience Function which prints the result of sloth_format_string_factory or saves it to a file
            :param groundtruth:
            :param output_path:
            :return:
            """
            if not output_path == '':
                output_file = open(output_path, "w")

            sloth_representation = self.sloth_format_json_factory(groundtruth=groundtruth)
            json_string = json.dumps(sloth_representation, sort_keys=True, indent=4)

            if not output_path == '':
                output_file.write(json_string)
            else:
                print(json_string)

        def delete_bystanders(self, bystander_document):
            """
            Remove bystanders from the data, so it does not screw up the results.
            :param bystander_document:CVATDocument  with tracks covering the area of the bystanders
            :return: None
            """
            bystander_tracks = bystander_document.tracks
            for bystander_track in bystander_tracks:
                from_frame, to_frame = bystander_track.from_to_frame()

                for track in self.tracks:
                    for cur_frame in range(from_frame, to_frame + 1):
                        bystander_box = bystander_track.tracked_elements[cur_frame]
                        xtl , width_height = bystander_box.top_right_width_height()
                        bystander_x, bystander_y = xtl
                        bystander_width, bystander_height = width_height
                        if cur_frame in track.tracked_elements:
                            box = track.tracked_elements[cur_frame]
                            if box.in_area(bystander_x, bystander_y, bystander_width, bystander_height):
                                del track.tracked_elements[cur_frame]

            self.tracks = [x for x in self.tracks if len(x.tracked_elements) != 0]


        def MOT_to_CVAT_parsetree(self, docpath, delimiter=','):
            num_ids = 0
            map_id_trackindex = dict()

            self.tracks = list()
            self.doc_tree = None
            self.max_frame = -1

            with open(docpath, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=delimiter)
                for row in reader:
                    if len(row) <= 8:

                        break
                    else:
                        (frame, id, bb_left, bb_top, bb_width, bb_height, conf) = row[0:7]

                    frame = int(frame)

                    # get the right track
                    object_track = None
                    if id not in map_id_trackindex:
                        current_track = Track()
                        self.tracks.append(current_track)
                        map_id_trackindex[id] = num_ids
                        num_ids += 1
                    else:
                        current_track = self.tracks[map_id_trackindex[id]]

                    new_box = Box()
                    current_track.tracked_elements[frame] = new_box
                    new_box.xtl = float(bb_top)
                    new_box.ybr = (float(bb_height) + float(bb_top))
                    new_box.xbr = (float(bb_left) + float(bb_width))
                    new_box.ytl = float(bb_top)

                    new_box.attributes['ytl'] = float(bb_top)
                    new_box.attributes['xtl'] = float(bb_left)
                    new_box.attributes['xbr'] = str(float(bb_left) + float(bb_width))
                    new_box.attributes['ybr'] = str(float(bb_height) + float(bb_top))
                    new_box.attributes['occluded'] = "0"

            self.max_frame = int(frame)

        def to_smot_itl_format(self, output_path):
            """
            This converts the internal representation to the .itl Format the SMOT
            (https://bitbucket.org/cdicle/smot/overview) Tracker uses.
            The File consists of the following Parts: At first a single number, representing the number of Tracks.
            Then, for every Track:
                <Id> <start_frame> <end_frame>
                <list of all the top-left x values>
                <list of all the top-left y values>
                <list of all the widths>
                <list of all the heights>
                <list of 0's and 1's, indicating if the object was occluded>

            :param output_path:
            :return:
            """
            doc = open(output_path, "w")

            doc.write(str(len(self.tracks)))
            doc.write(linesep)

            for track in self.tracks:
                from_frame, to_frame = track.from_to_frame()
                id = self.tracks.index(track)

                general_info_string = "{} {} {}" + linesep
                general_info_string = general_info_string.format(id, from_frame, to_frame)
                doc.write(general_info_string)

                x_values = list()
                y_values = list()
                width_values = list()
                height_values = list()
                omega_values = list()

                meta_list = [x_values, y_values, width_values, height_values, omega_values]

                xtl = 0
                ytl = 0
                xbr = 0
                ybr = 0

                for frame in range(from_frame, to_frame + 1):
                    # Update the values if there is data for the object in this frame, else just use the old values
                    # and mark the object as invisible
                    if frame in track.tracked_elements:

                        frame_info = track.tracked_elements[frame].attributes

                        decimal_limiter = "{0:.2f} "

                        xtl = float(frame_info['xtl'])
                        ytl = float(frame_info['ytl'])
                        xbr = float(frame_info['xbr'])
                        ybr = float(frame_info['ybr'])

                        if 'occluded' not in frame_info:
                            omega_values.append("1 ")
                        else:
                            omega_values.append(str(int(frame_info['occluded'] != "1")) + " ")


                    else:
                        omega_values.append("0 ")

                    x_values.append(decimal_limiter.format(xtl))
                    y_values.append(decimal_limiter.format(ytl))
                    width_values.append(decimal_limiter.format(xbr - xtl))
                    height_values.append(decimal_limiter.format(ybr - ytl))

                for l in meta_list:
                    doc.writelines(l)
                    doc.write(linesep)


def parse_node(node):
        if node.tag == 'box':
                return Box(node)
        if node.tag == 'polygon':
                return Polygon(node)


def my_json_to_mot_16_dets(json_filepath, outpath):

    json_file = open(json_filepath)
    rep = json.load(json_file)

    out_file = open(outpath, "w")

    line_format= "{0}, -1, {1}, {2}, {3}, {4},  1, -1, -1, -1" + linesep

    for frame in rep:
        frame_num = frame["frame"]

        for detection in frame["detections"]:

            x = detection["x"]
            y = detection["y"]
            width = detection["width"]
            height = detection["height"]

            formatted_line = line_format.format(frame_num, x, y, width, height)

            out_file.write(formatted_line)


import os


def convert_for_mm(filepath):
    f = open(filepath, "r")
    output = open(filepath[0:-4]+ ".csv", "w")
    csvfile = csv.reader(f, delimiter=',')
    lines_to_write = list()
    for line in csvfile:
        to_write = line[0:6]
        to_write += [1,	1, 1, 0]
        to_write = map(str, to_write)

        lines_to_write.append(("\t".join(to_write)) + os.linesep)

    output.writelines(lines_to_write)






if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", '--informat', help="Specify the format you want to Convert. "
                                              "Default: CVATXML, other option: MOT17",
                        default="CVATXML",
                        type=str)
    parser.add_argument("-t", "--outformat", help="Format to convert to. Default: MOT17, other option: SLOTH",
                        default="MOT17",
                        type=str)
    parser.add_argument("-o", "--outfile", help="Path to your outputfile. If not given, "
                                                "output is printed to the console.", default='')

    parser.add_argument("-g", "--gt", help="When printing to SLOTH Format: Is given File Groundtruth",
                        type=bool, default=False)

    parser.add_argument("--mgt", help="MOT Ground Truth erstellen", action="store_true")

    parser.add_argument("infile", help="Path to the file you want to convert")

    args = parser.parse_args()

    doc = None

    print("InputFile: ", args.infile )
    print("Input Format: " , args.informat)

    print("Output File: " , args.outfile )
    print("Output Fomrat" , args.outformat)
    print("Groundtruth", args.gt)

    if args.infile is not None:
        if args.informat == 'CVATXML':
            doc = CVATDocument(args.infile)
            doc.parse()
        elif args.informat in ['2D MOT 2015', "MOT16", "PETS2017", "MOT17"]\
                or args.informat == "MOT17":
            doc = CVATDocument()
            doc.MOT_to_CVAT_parsetree(args.infile)

        if args.outformat in ["2D MOT 2015", "MOT16", "PETS2017", "MOT17"]:
            doc.to_format(args.outformat, args.outfile, dets_only=args.mgt)

        elif args.outformat == "SLOTH":
            doc.to_sloth_format(groundtruth=args.gt, output_path=args.outfile)




"""
from: 
0, 6, 2721.48, 959.03, 17.84, 57.84, 1, -1, -1, -1 
0, 7, 2884.45, 955.79, 14.05, 44.59, 1, -1, -1, -1

to: 

      names=['FrameId', 'Id', 'X', 'Y', 'Width', 'Height', 'Confidence', 'ClassId', 'Visibility', 'unused'], 

"""




