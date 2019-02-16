import cv2
import csv
import random

ID_COLOR_MAP = dict()


print("Use with python2.7 if this does not work. Weird conflict with qt.")


def get_color_by_id(id):
    if id in ID_COLOR_MAP:
        return ID_COLOR_MAP[id]
    else:
        r = int(random.random() * 255)
        g = int(random.random() * 255)
        b = int(random.random() * 255)

        color = (b, g,r)

        if color in ID_COLOR_MAP.values():
            return get_color_by_id(id)
        else:
            ID_COLOR_MAP[id] = color
            return color


def show_tracking(videopath, mot_path, savepath='', show=False, delimiter='\t'):

    videocapture = cv2.VideoCapture(videopath)
    mot_file = open(mot_path, "r")
    window_name = "Video"
    mot_reader = csv.reader(mot_file, delimiter=delimiter)
    videowriter = None
    if savepath != '':
        videowriter = cv2.VideoWriter(
            savepath,
            cv2.VideoWriter.fourcc('M', 'J','P', 'G'),
            float(videocapture.get(cv2.CAP_PROP_FPS)),
            (int(videocapture.get(cv2.CAP_PROP_FRAME_WIDTH)), int( videocapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        )
    if show:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    ret, frame = videocapture.read()
    current_frame = 0
    for line in mot_reader:
        read_frame = int(line[0])
        if read_frame != current_frame: # Update Frame and Display

            if videowriter is not None:
                videowriter.write(frame)
            if show:
                cv2.imshow(window_name, frame)
                cv2.waitKey(20)


            ret, frame = videocapture.read()
            current_frame =int(line[0])

        color = get_color_by_id(line[1])
        x = int(float(line[2]))
        y = int(float(line[3]))
        width = int(float(line[4]))
        height = int(float(line[5]))

        cv2.rectangle(frame, (x,y), (x + 40, y - 20), color, thickness=-1)
        cv2.putText(frame, line[1], (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 0))
        cv2.putText(frame, "Frame: " + str(current_frame), (5, 40), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 255))

        cv2.rectangle(frame, (x, y), (x + width, y + height), color)


show_tracking("/home/flo/Videos/TS_10_5.mp4",
              "../data/mot_fmt_results/smot_TS_10_5.txt", show=False, delimiter=',',
              savepath="../data/evaluation_video/smot_TS_10_5_tr.mp4")


