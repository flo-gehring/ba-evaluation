
"""from trackformatconverter import CVATDocument
import numpy
import os
import matplotlib
import matplotlib.scale
import matplotlib.pyplot as plt
import csv

def average_bb_size(cvatdoc):



    :param cvatdoc trackformatconverter.CVATDocument:
    :return:

    box_sizes = list()
    for track in cvatdoc.tracks:

        for frame, box in track.tracked_elements.items():
            box_size = (box.xbr - box.xtl) * (box.ybr - box.ytl)
            if box_size < 0:

                continue
            box_sizes.append(
                box_size
            )


    return box_sizes





cvatdoc = CVATDocument('/home/flo/PycharmProjects/ba-evaluation/data/cvatgt/TS_10_05_ohne_bs.xml')
cvatdoc.parse()
size_list = average_bb_size(cvatdoc)
plt.xlabel('AOI Größe in px^2')
plt.ylabel('Verteilung')

print(min(size_list))
print(max(size_list))
n, bins, patches = plt.hist(size_list)
plt.title('Größenverteilung der AOI\'s für Personen in den Trainingszenen')
plt.grid(True)
plt.show()



s = os.listdir('/home/flo/Downloads/MOT16Labels/train/')
size_list = list()
currentMaxSize = 0
for folder in s:
    path = '/home/flo/Downloads/MOT16Labels/train/' + folder + '/gt/gt.txt'

    with open(path, 'r') as csvfile:

        reader = csv.reader(csvfile)
        for row in reader:
            if(len(row)) < 3:
                break
            else:

                (frame, id, bb_left, bb_top, bb_width, bb_height, consider, obj_type, occlusion_ratio) = row[0:9]
                if consider == '1' and obj_type == '1':
                    size = float(bb_width) * float(bb_height)
                    if size > currentMaxSize:
                        print("New Max:")
                        print (folder)
                        print(size)
                        print(bb_height)
                        print(bb_width)
                        print('---')
                        currentMaxSize = size
                    size_list.append(float(bb_width) * float(bb_height))




print ("Average list:")
print(size_list)

no_biggies = [x for x in size_list if x < 100000]

plt.xlabel('AOI Größe in px^2')
plt.ylabel('Verteilung')
plt.xscale('log')
plt.yscale('log')
print(min(size_list))
print(max(size_list))
n, bins, patches = plt.hist(size_list, bins= [240.0, 500, 1000, 1500, 2000, 5000, 10000, 20000, 40000, 75940.65, 151641.3, 227341.94999999998, 303042.6, 378743.25, 454443.89999999997, 530144.5499999999, 605845.2, 681545.85, 757246.5, 832947.1499999999, 908647.7999999999, 984348.45, 1060049.0999999999, 1135749.75, 1211450.4,
                                              1287151.0499999998, 1362851.7, 1438552.3499999999, 1514253.0])
plt.title('Größenverteilung der AOI\'s für Personen MOT Challenge')


plt.grid(True)
plt.show()

print("Minimum")
print(min(size_list))
print("Median")
print(numpy.median(size_list))


"""