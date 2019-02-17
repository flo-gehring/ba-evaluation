import json
import sys

import cv2

import argparse


# Some Constants

CORRESPONDENCE = u'correspondence'
MISS = u'miss'
FALSE_POSITIVE = u'false positive'
MISMATCH = u'mismatch'

def get_annotations_for_frame(frame_counter, frames_list):
    if(frames_list[frame_counter]["timestamp"] == frame_counter):
        return frames_list[frame_counter]["annotations"]

    else:
        for frame in frames_list:
            if frame["timestamp"] == frame_counter:
                return frame["annotations"]

def get_bottom_left(x, y, width, heigth):
    return (x + width, y + heigth)



COLOR_SCHEME = {
    MISS: (204, 0, 153),
    FALSE_POSITIVE: (204, 51, 0),
    CORRESPONDENCE: (255, 255, 255),
    MISMATCH: (0, 0, 255)
}


def create_video(path_to_debug, path_to_video, path_to_output=None, inspect=False, stoplist=[]):
    video_capture = cv2.VideoCapture(path_to_video)
    if (video_capture.isOpened()):
        print("\t Success!")
    else:
        print("\t Error, abort.")
        sys.exit()
    print("Opening JSON File...")
    jsonfile = open(path_to_debug, "r")
    if(jsonfile is not None):
        print("\t File loaded, decoding JSON...")
    else:
        print("File could not be opened, does file exist and can be read?")
        sys.exit()

    loaded_json = json.load(jsonfile)
    frames_list = loaded_json[0]["frames"]
    print("JSON decoded, begin video playback..")

    ret, frame = video_capture.read()

    frame_counter = 0
    annotations_for_frame = list()

    all_correspond = True

    error_descriptions = list()

    video_writer = None
    if path_to_output is not None:
        video_writer = cv2.VideoWriter(
            path_to_output,
            cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'),
            float(video_capture.get(cv2.CAP_PROP_FPS)),
            (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    while ret:

        error_descriptions = list()

        annotations_for_frame = get_annotations_for_frame(frame_counter, frames_list)
        all_correspond = True
        halt_for_stoplist = False

        for annotation in annotations_for_frame:
            annotation_class = annotation["class"]
            color = COLOR_SCHEME[annotation_class]

            x = int(annotation["x"])
            y = int(annotation["y"])
            width = int(annotation["width"])
            height = int(annotation["height"])

            if annotation_class != CORRESPONDENCE:
                description = annotation_class + ", id: " + str(len(error_descriptions))
                cv2.putText(frame, str(len(error_descriptions)), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            1, color ,2 ,cv2.LINE_AA)
                error_descriptions.append(description)
                if annotation_class in stoplist:
                    halt_for_stoplist = True

            all_correspond &= (annotation_class == CORRESPONDENCE)
            cv2.rectangle(frame, (x,y), get_bottom_left(x, y, width, height), color)

        description_counter = 1
        for description in error_descriptions:
            cv2.putText(frame, description, (10, description_counter * 40), cv2.FONT_HERSHEY_SIMPLEX, 2,
                        (0,0,0))
            description_counter += 1

        # Show frame and halt for errors or save it as a video
        if video_writer is None:
            frame = cv2.resize(frame, dsize=(1920, 1080), interpolation=cv2.INTER_AREA)
            cv2.imshow('frame', frame)

            if inspect or halt_for_stoplist: # Stop Video playback to inspect error
                while not (all_correspond or cv2.waitKey(1) & 0xFF == ord(' ')):
                    pass

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            video_writer.write(frame)

        ret, frame = video_capture.read()
        frame_counter += 1


    video_capture.release()
    video_writer.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="When given a file like produced by pymot and the corresponding video"
                                                 "the tracking mot_fmt_results are displayed.")


    parser.add_argument("debugfile", help="Path to Inputfile, "
                                       "in visual debug format as given by pymot")

    parser.add_argument("videofile", help="Path to the tracked Video")

    parser.add_argument("--inspect", help="Use this flag if the video should halt another class than a correspondence "
                                          "appears. "
                                          "To select only certain errors, use stoplist argument.",
                        action="store_true")

    parser.add_argument("--stoplist",
                        help="If you're using this option, give positional arguments (filepaths) before optional ones."
                             "List of Errors to stop for, one of " +", ".join(COLOR_SCHEME.keys()[1:]) +
                             ". \n Yes, just enter false positive as two words.",
                        default=list(),
                        nargs='*',
                        type=str)


    args = parser.parse_args()

    if('false' in args.stoplist and 'positive' in args.stoplist):
        args.stoplist.append(FALSE_POSITIVE)
        args.stoplist.remove('false')
        args.stoplist.remove('positive')

    create_video(args.debugfile, args.videofile, path_to_output=None, inspect=args.inspect, stoplist=args.stoplist)



