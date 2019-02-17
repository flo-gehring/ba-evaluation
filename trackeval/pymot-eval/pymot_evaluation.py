from pymot import MOTEvaluation
from trackformatconverter import CVATDocument
from setup_tracker_directories import get_into_dir
import os.path
from eval_utilities.visualize_evalution import create_video
from formatchecker import *
import json

def get_evaluator(path_to_mot_gt, path_to_mot_tracking_result, path_to_bystanders=None):
    """
    Returns an evaluator for a groundtruth, tracking result pair.
    :param path_to_mot_gt:
    :param path_to_mot_tracking_result:
    :param path_to_bystanders:
    :return:
    """
    abs_gt_path = os.path.abspath(path_to_mot_gt)
    abs_tracking_res_path = os.path.abspath(path_to_mot_tracking_result)

    bystander_doc = None
    if path_to_bystanders is not None:
        bystander_doc = CVATDocument(path_to_bystanders)
        bystander_doc.parse()

    gt_document = setup_mot_doc(abs_gt_path, bystander_doc=bystander_doc)
    gt_json = gt_document.sloth_format_json_factory(groundtruth=True)
    gt_json = gt_json[0]

    result_document = setup_mot_doc(abs_tracking_res_path, bystander_doc)
    result_json = result_document.sloth_format_json_factory(groundtruth=False)
    result_json = result_json[0]

    format_checker = FormatChecker(gt_json, result_json)
    print("Complete: " + str(format_checker.checkForCompleteness()))
    print("Ambiguous IDs:" + str(format_checker.checkForAmbiguousIDs()))
    print("Existing IDs: " + str(format_checker.checkForExistingIDs()))

    evaluator = MOTEvaluation(
        groundtruth=gt_json,
        hypotheses=result_json,
        overlap_threshold=0.2
    )

    return evaluator


def create_pymot_eval_directory(path_to_gt, path_to_result, path_to_target_directory,
                                tracker_name, video_name, path_to_source_vid=None, path_to_bystanders=None):
    """
    Create an Directory which contains all relevant evaluation results.
    If the path to the video source is given, a Video will showing the results will be saved.
    There will be the following Directory Structure:
    <path_to_target_directory>/<tracker_name>/<video_name>/ -> all the files you could ever wish for.
    :param path_to_gt:
    :param path_to_result:
    :param path_to_target_directory:
    :param tracker_name:
    :param video_name:
    :param path_to_source_vid:
    :param path_to_bystanders:
    :return:
    """
    evaluator = get_evaluator(path_to_gt, path_to_result, path_to_bystanders)
    evaluator.evaluate()

    starting_dir = os.curdir
    abs_path_to_td = os.path.abspath(path_to_target_directory)

    os.chdir(abs_path_to_td)
    get_into_dir(tracker_name)
    get_into_dir(video_name)

    evaluator.getRelativeStatistics()

    abs_stat_file = open("absolute_stats.json", 'w')
    rel_stat_file = open("relative_stats.json", "w")
    vis_debug_file = open("visual_debug.json", "w")

    abs_statistics = evaluator.getAbsoluteStatistics()
    relative_statistics = evaluator.getRelativeStatistics()
    visual_debug = evaluator.getVisualDebug()

    abs_stat_file.write(json.dumps(abs_statistics, sort_keys=True, indent=4))
    rel_stat_file.write(json.dumps(relative_statistics, sort_keys=True, indent=4))
    vis_debug_file.write(json.dumps(visual_debug, sort_keys=True, indent=4))

    abs_stat_file.close()
    rel_stat_file.close()
    vis_debug_file.close()

    if path_to_source_vid is not None:
        filename_debug_vid = "debug_" + video_name + ".mp4"
        create_video("visual_debug.json", path_to_source_vid, path_to_output=filename_debug_vid)


def setup_mot_doc(filepath, bystander_doc=None):
    """
    Helper function to make a CVATDoc Object
    :param filepath:
    :param bystander_doc:
    :return:
    """
    filename, extension = os.path.splitext(filepath)

    if extension == '.xml':
        cvat_doc = CVATDocument(filepath)
        cvat_doc.parse()
    else:
        cvat_doc = CVATDocument()
        cvat_doc.MOT_to_CVAT_parsetree(filepath)

    if bystander_doc is not None:
        cvat_doc.delete_bystanders(bystander_doc)

    return cvat_doc


tracker_names = ['DEEPSORT', 'PANORAMA_TRACKER']

for name in tracker_names:

    create_pymot_eval_directory(
        '/home/flo/PycharmProjects/ba-evaluation/data/cvatgt/TS_10_5.xml',
        '/home/flo/PycharmProjects/ba-evaluation/data/mot_fmt_results/' + name.lower() + '_TS_10_5.txt',
        '/home/flo/PycharmProjects/ba-evaluation/data/pymot_eval',
        name,
        'TS_10_5',
        path_to_bystanders='/home/flo/PycharmProjects/ba-evaluation/data/bystanders/TS_10_05 Bystanders.xml',
        path_to_source_vid='/home/flo/PycharmProjects/ba-evaluation/data/videos/TS_10_5.mp4')
