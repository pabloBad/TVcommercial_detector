import numpy as np
import time
import os.path

from distance_functions import *
from file_functions import cargar_descriptor, listar_archivos_en_carpeta, save_similarity_search_results
from os import listdir, makedirs
from os.path import isfile, join, exists, abspath


distance_functions_dict = {
        'manhattan_distance' : manhattan_distance,
        'euclidean_distance' : eucliedian_distance,
        'hamming_distance' : hamming_distance,
        'chebychev_distance' : chebychev_distance
    }

def get_time_difference(start, end):
    """Calcula la diferencia de tiempos y la retorna como string formateado

    Arguments:
        start {float} -- Tiempo inicial.
        end {float} -- Tiempo final.

    Returns:
        str -- String formateado con la diferencia de horas.
    """

    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)


# -------------------------------------------------------------------------------------------------
# ----------------------------------- Calculo Ranking por frame -----------------------------------
# -------------------------------------------------------------------------------------------------

def calculate_min_distance_frames(
        descriptor_frame_tv,
        vectores_descriptores_comerciales,
        distance_function,
        debug=False):

    frame_minima_distancia = (None, None, np.finfo(
        float).max)  # Inicializamos la variable

    # Iteramos por cada uno de los comerciales:
    for vector_descriptor_comercial in vectores_descriptores_comerciales:
        # vector_descriptor_comercial[0] -> Nombre del comercial.
        # vector_descriptor_comercial[1] -> Arreglo con los descriptores de cada frame.

        for descriptor_comercial in enumerate(vector_descriptor_comercial[1]):
            # # descriptor_comercial[0] -> Numero del frame que se esta procesando
            # # descriptor_comercial[1] -> Descriptor del frame

            distancia_calculada = distance_function(
                descriptor_frame_tv, descriptor_comercial[1]["feature_vector"])
            if (distancia_calculada < frame_minima_distancia[2]):
                frame_minima_distancia = (
                    vector_descriptor_comercial[0],  # Nombre del comercial
                    descriptor_comercial[0],        # Frame del comercial.
                    distancia_calculada)            # Distancia calculada

        # Extraigo los primeros n resultados del ranking y retorno

    # Retornamos solo el comercial y el numero del frame
    return (frame_minima_distancia[0], frame_minima_distancia[1])


def similarity_search(
    analyzed_video_name,
    analyzed_video_descriptors_vector, 
    comparate_videos_descriptors, 
    distance_function_name, 
    debug=False):

    # analyzed_video_descriptors_vector[0] -> Timestamp from the begining of the video
    # analyzed_video_descriptors_vector[1] -> Calculated caracteristic vector of the frame
    print("Detected frames:", len(analyzed_video_descriptors_vector))

    status_proportion = round(len(analyzed_video_descriptors_vector) /
                             10) if round(len(analyzed_video_descriptors_vector)/10) != 0 else 1

    # Looking for the distance functions in the imported functions
    if (distance_function_name in distance_functions_dict):
        distance_function = distance_functions_dict[distance_function_name]
    else:
        print (distance_function)
        msg = "Distance function not found: " + distance_function_name
        raise KeyError(msg)
    
    similarity_search_results = []

    initial_time = time.time()
    for descriptor in enumerate(analyzed_video_descriptors_vector):
        # descriptor[0] -> Numero del frame al que se le esta calculando el ranking
        # descriptor[1] -> Objeto con el vector caracteristico + tiempo transcurrido al que se le calculara el frame del comericial con menor distancia.
        calculated_min_dist_frame = calculate_min_distance_frames(descriptor[1]["feature_vector"], comparate_videos_descriptors, distance_function, False)

        # result_tuple = ('analyzed_video_frame_number','elapsed_time', 'other_vid_name', 'min_dist_frame')
        similarity_search_results.append((descriptor[0], descriptor[1]["elapsed_time"], calculated_min_dist_frame[0], calculated_min_dist_frame[1]))

        # Print Status
        if ((descriptor[0] + 1) % status_proportion) == 0:
            print("Getting min distance frames on the frame",
                  (descriptor[0] + 1),"/",
                  len(analyzed_video_descriptors_vector),"\t Elapsed Time:",
                  get_time_difference(initial_time, time.time()))

            if (debug):
                cmd = input("Command? (m -> Show calculated distance, q -> Quit, d -> Disable debugging, * -> Skip)\n")
                if (cmd == 'm'):
                    import pprint
                    pp = pprint.PrettyPrinter(indent=4)
                    pp.pprint(similarity_search_results)
                elif (cmd == 'q'): exit()
                elif(cmd == 'd'): debug = False

    print ("End of similarity search. Elapsed time", get_time_difference(initial_time, time.time()))

    return np.array(similarity_search_results)