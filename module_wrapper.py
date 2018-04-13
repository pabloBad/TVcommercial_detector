from os import listdir, makedirs
from os.path import isfile, join, exists, abspath, basename
import numpy as np

from file_functions import list_files_in_folder, cargar_descriptores_comerciales, cargar_descriptor, save_similarity_search_results, load_similarity_search_results

from feature_extractor import extract_video_feature
from similarity_search import similarity_search
from occurence_detector import occurrence_detector

# pylint: disable=W0612

def execute_feature_extraction(
        videos_to_analyze_path,
        other_videos_path,
        rows_of_division=8,
        cols_of_division=8,
        bins=16,
        fps_target=3,
        save_files=True,
        debug=False):

    other_videos_list = list_files_in_folder(other_videos_path)
    videos_to_analyze_list = list_files_in_folder(videos_to_analyze_path)

    if not exists("temp/"):
        makedirs("temp/")

    print("Feature Extraction of files in:", other_videos_path, "\n")
    features_array_other_videos = [extract_video_feature(
        other_video,
        rows_of_division,
        cols_of_division,
        bins,
        fps_target,
        save_files,
        debug=debug)
        for other_video in other_videos_list]

    # print("Feature Extraction of files in:", ruta_television, "\n")
    # list(map(extract_video_feature, videos_television))

    features_array_videos_to_analyze = [extract_video_feature(
        video_to_analyze,
        rows_of_division,
        cols_of_division,
        bins,
        fps_target,
        save_files,
        debug=debug)
        for video_to_analyze in videos_to_analyze_list]

    return (features_array_videos_to_analyze, features_array_other_videos)


def execute_similarity_search(
        analyzed_videos_path,
        comparated_videos_path,
        distance_function_name='manhattan_distance',
        save_results=True,
        debug=False):
    comparated_videos_descriptors_vectors = cargar_descriptores_comerciales(
        comparated_videos_path)

    similarity_search_results_by_video = []

    # For all videos in Analyzed videos path
    for analyzed_video_descriptors_file in list_files_in_folder(analyzed_videos_path):
        print("Processing array of feature vectors for",
              basename(analyzed_video_descriptors_file))
        result = {
            'analyzed_video_name': basename(analyzed_video_descriptors_file),
            'similarity_search_result_tuple': similarity_search(
                basename(analyzed_video_descriptors_file),
                cargar_descriptor(analyzed_video_descriptors_file),
                comparated_videos_descriptors_vectors,
                distance_function_name,
                debug=debug)}
        similarity_search_results_by_video.append(result)
        if save_results:
            save_similarity_search_results(
                result['analyzed_video_name'], result)

    # return np.array(similarity_search_results_by_video)


def execute_occurrence_detector(
        temporal_similarity_search_path: str,
        min_sequence_lenght: int,
        max_difference_between_frames: int,
        max_percentage_repeated_elements: float,
        debug=False):

    # Load files
    
    similarity_search_results_by_video = list(map(load_similarity_search_results, list_files_in_folder(temporal_similarity_search_path, return_basenames= True)))
    occurrences_detected_all_videos = []

    similarity_search_results_by_video = map(
        lambda element: element[()], similarity_search_results_by_video)

    for similarity_search_result in similarity_search_results_by_video:
        # similarity_search_result = {'analyzed_video_name','similarity_search'}
        # similarity_search_result_tuple = ('analyzed_video_frame','elapsed_time', 'other_vid_name', 'min_dist_frame')
        ocurrences_result = occurrence_detector(
            similarity_search_result['similarity_search_result_tuple'],
            min_sequence_lenght,
            max_difference_between_frames,
            max_percentage_repeated_elements,
            debug=debug)

        # occurrence example: [analyzed_video_name, other_video_start_time, other_video_length, other_video_name])
        occurrences_detected_all_videos.append(list(map(lambda ocurrence: [similarity_search_result['analyzed_video_name'], ocurrence[0], ocurrence[1], ocurrence[2]], ocurrences_result)))
    
    return occurrences_detected_all_videos


def save_results(results):
    with open('detecciones.txt', 'w') as f:

        print ("Writting detections in detections.txt")
        for analyzed_video in results:
            for occurence in analyzed_video:

                if ('.npy' in str(occurence[0])):
                    string = ''.join([str(occurence[0][:-4]), '\t', str(
                        occurence[1]), '\t', str(occurence[2]), '\t', str(occurence[3]), '\n'])
                    f.write(string)
                else: 
                    string = ''.join([str(occurence[0][:-4]), '\t', str(
                    occurence[1]), '\t', str(occurence[2]), '\t', str(occurence[3]), '\n'])
                    f.write(string)
