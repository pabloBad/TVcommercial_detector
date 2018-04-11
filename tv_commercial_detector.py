from os import listdir, makedirs
from os.path import isfile, join, exists, abspath, basename
import numpy as np

from file_functions import listar_archivos_en_carpeta, cargar_descriptores_comerciales, cargar_descriptor, save_similarity_search_results

from feature_extractor import extract_video_feature
from similarity_search import similarity_search
from occurence_detector import occurence_detector

# pylint: disable=W0612

def execute_feature_extraction(
    videos_to_analyze_path, 
    other_videos_path, 
    rows_of_division=8, 
    cols_of_division=8, 
    bins=16, 
    fps_target=3, 
    save_files = True,
    debug=False):

    other_videos_list = listar_archivos_en_carpeta(other_videos_path)
    videos_to_analyze_list = listar_archivos_en_carpeta(videos_to_analyze_path)

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
    distance_function_name = 'manhattan_distance', 
    save_results = True,
    debug=False):
    comparated_videos_descriptors_vectors = cargar_descriptores_comerciales(
        comparated_videos_path)

    similarity_search_results_by_video = []

    # For all videos in Analyzed videos path
    for analyzed_video_descriptors_file in listar_archivos_en_carpeta(analyzed_videos_path):
        print("Processing array of feature vectors for", basename(analyzed_video_descriptors_file))
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
            save_similarity_search_results(result['analyzed_video_name'], result)

    # return np.array(similarity_search_results_by_video)

def execute_occurence_detector(
    similarity_search_results_by_video,
    window_size, 
    min_amount_sequence_numbers, 
    min_percentage_sequence_numbers, 
    skip_frames, 
    debug = False):
    occurrences_detected_all_videos = []

    similarity_search_results_by_video = map(lambda element : element[()], similarity_search_results_by_video)

    for similarity_search_result in similarity_search_results_by_video:
        # print (type(similarity_search_result))
        # similarity_search_result = {'analyzed_video_name','similarity_search'}
        # similarity_search_result_tuple = ('analyzed_video_frame','elapsed_time', 'other_vid_name', 'min_dist_frame')
        occurrences_detected_all_videos.append(
            (similarity_search_result['analyzed_video_name'], 
            occurence_detector(
                similarity_search_result['similarity_search_result_tuple'],
                window_size, 
                min_amount_sequence_numbers, 
                min_percentage_sequence_numbers, 
                skip_frames,
                debug=debug)))

    # occurence (analyzed_video_name, (other_video_name, other_video_start_time, other_video_length))

    results = []

    # Format Results:
    for video_analyzed in occurrences_detected_all_videos:
        for occurrences_array in video_analyzed[1]:
            results.append(
                (video_analyzed[0][:-4], occurrences_array[1], occurrences_array[2], occurrences_array[0]))
    return results

def save_results(results):
    with open('detecciones.txt', 'w') as f:
        for result in results:
            string = ''.join([str(result[0]),'\t', str(result[1]),'\t', str(result[2]), '\t', str(result[3]), '\n'])
            f.write(string)


def print_results(results):
    for result in results:
        print(result[0], '\t', result[1], '\t', result[2], '\t', result[3], '\t')
    return

def main():

    # PATHS: 

    RUTA_COMERCIALES = "videos/comerciales/"
    RUTA_TELEVISION = "videos/television/"

    TEMPORAL_FEATURE_ANALYZED_VIDEO_PATH = "temp/television"
    TEMPORAL_FEATURE_OTHER_VIDEO_PATH = "temp/comerciales"

    DEBUG = False

    # PARAMETERS:

    # Feature Extraction
    ROWS_OF_DIVISION = 10
    COLS_OF_DIVISION = 10
    BINS = 8
    FPS_TARGET = 3
    SAVE_FILES = True

    # Similarity Search

    # Distance options: manhattan_distance, euclidean_distance, chebychev_distance, hamming_distance, chebychev_distance
    DISTANCE_FUNCTION = 'euclidean_distance'
    SAVE_FILES_2 = True

    # Occurrence Detector
    WINDOW_SIZE = 4 * 50  + 30# 3 FPS * 50 frames  
    MIN_AMOUNT_SEQUENCE_NUMBERS = 60 # 25 *  3 FPS = 20 Seconds
    MIN_PERCENTAGE_SEQUENCE_NUMBERS = 0.2
    # SKIP_FRAMES = 3 * 50 
    SKIP_FRAMES = round(WINDOW_SIZE*2/3)
    # MAX_FRAME_DISTANCE_SEPARTION = 5 # Distance between frames of the same detection

    # Paso 1: Procesamos todos los videos al generar los vectores de caracteristicas
    # de cada uno de ellos para posteriormente guarlos:

    # TODO SACAR ESTE COMENTARIO....
    execute_feature_extraction(RUTA_TELEVISION, RUTA_COMERCIALES, ROWS_OF_DIVISION, COLS_OF_DIVISION, BINS, FPS_TARGET, SAVE_FILES, debug=False)

    # Paso 2: Hacemos la busqueda por similitud mediante el calculo de un ranking de
    # frames similares entre un frame del video de television y todos los frames de
    # todos los comerciales, usando funciones de distancia de caracteristicas.
    execute_similarity_search(TEMPORAL_FEATURE_ANALYZED_VIDEO_PATH, TEMPORAL_FEATURE_OTHER_VIDEO_PATH, DISTANCE_FUNCTION, SAVE_FILES_2, debug = False)

    # Paso 3: Ejecutamos la deteccion de apariciones...

    


    save_results(execute_occurence_detector(
        [np.load('temp/similarity_search/mega-2014_04_10.npy')],
        WINDOW_SIZE, 
        MIN_AMOUNT_SEQUENCE_NUMBERS,
        MIN_PERCENTAGE_SEQUENCE_NUMBERS,
        SKIP_FRAMES,
        debug=True))

    # print ([np.load('temp/similarity_search/mega-2014_04_10.npy')])

    # from subprocess import call
    # call(["python", "evaluar_v2.py","detecciones.txt"])
    # print(type(np.load('temp/similarity_search/mega-2014_04_10.npy')))
main()
