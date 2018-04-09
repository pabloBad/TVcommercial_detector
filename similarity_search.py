import numpy as np
import time
import os.path

from funciones_distancia import *
from file_functions import cargar_descriptor, listar_archivos_en_carpeta
from os import listdir, makedirs
from os.path import isfile, join, exists, abspath


def diferencia_tiempos(start, end):
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

def ranking_primeros_n(
        descriptor_frame_tv,
        vectores_descriptores_comerciales,
        primeros_n,
        funcion_distancia,
        debug=False):
    vector_distancias = []
    # Iteramos por cada uno de los comerciales:
    for vector_descriptor_comercial in vectores_descriptores_comerciales:
        # vector_descriptor_comercial[0] -> Nombre del comercial.
        # vector_descriptor_comercial[1] -> Arreglo con los descriptores de cada frame.

        for descriptor_comercial in enumerate(vector_descriptor_comercial[1]):
            # descriptor_comercial[0] -> Numero del frame que se esta procesando
            # descriptor_comercial[1] -> Descriptor del frame
            vector_distancias.append((
                vector_descriptor_comercial[0],  # Nombre del comercial
                descriptor_comercial[0],  # Frame del comercial.
                funcion_distancia(descriptor_frame_tv, descriptor_comercial[1])))  # Distancia calculada.

        # Extraigo los primeros n resultados del ranking y retorno

    # TODO ARREGLAR ESTE QUESO
    return [(tupla[0], tupla[1])
            for tupla in sorted(vector_distancias, key=lambda distancia: distancia[2])[:primeros_n]]


def calcular_frames_minima_distancia(
        descriptor_frame_tv,
        vectores_descriptores_comerciales,
        funcion_distancia,
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

            distancia_calculada = funcion_distancia(
                descriptor_frame_tv, descriptor_comercial[1]["feature_vector"])
            if (distancia_calculada < frame_minima_distancia[2]):
                frame_minima_distancia = (
                    vector_descriptor_comercial[0],  # Nombre del comercial
                    descriptor_comercial[0],        # Frame del comercial.
                    distancia_calculada)            # Distancia calculada

        # Extraigo los primeros n resultados del ranking y retorno

    # Retornamos solo el comercial y el numero del frame
    return (frame_minima_distancia[0], frame_minima_distancia[1])


def similarity_search(analyzed_video_descriptors_vector, comparate_videos_descriptors, debug=False):

    # analyzed_video_descriptors_vector[0] -> Timestamp from the begining of the video
    # analyzed_video_descriptors_vector[1] -> Calculated caracteristic vector of the frame
    tiempo_inicial = time.time()
    print("Detected frames:", len(analyzed_video_descriptors_vector))

    proporcion_aviso = round(len(analyzed_video_descriptors_vector) /
                             10) if round(len(analyzed_video_descriptors_vector)/10) != 0 else 1

    similarity_search_results = []

    for descriptor in enumerate(analyzed_video_descriptors_vector):
        # descriptor[0] -> Numero del frame al que se le esta calculando el ranking
        # descriptor[1] -> Objeto con el vector caracteristico + tiempo transcurrido al que se le calculara el frame del comericial con menor distancia.
        calculated_min_dist_frame = calcular_frames_minima_distancia(descriptor[1]["feature_vector"], comparate_videos_descriptors, distancia_euclideana, False)

        # result_tuple = ('analyzed_video_frame_number','elapsed_time', 'other_vid_name', 'min_dist_frame')
        similarity_search_results.append((descriptor[0], descriptor[1]["elapsed_time"], calculated_min_dist_frame[0], calculated_min_dist_frame[1]))

        if ((descriptor[0] + 1) % proporcion_aviso) == 0:
            
            print("Getting min distance frames on the frame",
                  (descriptor[0] + 1),
                  "/",
                  len(analyzed_video_descriptors_vector),
                  "\t Elapsed Time:",
                  diferencia_tiempos(tiempo_inicial, time.time()))
            if (debug):
                cmd = input("Command? (m -> Show calculated distance, q -> Quit, d -> Disable debugging, l ->Save on log file, * -> Skip)\n")
                if (cmd == 'm'):
                    import pprint
                    pp = pprint.PrettyPrinter(indent=4)
                    pp.pprint(similarity_search_results)
                elif (cmd == 'l'):
                    import pprint
                    pp = pprint.PrettyPrinter(indent=4)
                    pprint.pprint(similarity_search_results, open('log.txt', 'w'))
                elif (cmd == 'q'): exit()
                elif(cmd == 'd'): debug = False

    return np.array(similarity_search_results)

# DEBUG
# RUTA_COMERCIALES = "temp/comerciales/"
# RUTA_TELEVISION = "temp/television/mega-2014_04_10.npy"
# print (cargar_descriptores_comerciales(RUTA_COMERCIALES, listar_archivos_en_carpeta))
# busqueda_por_similitud(cargar_descriptor(RUTA_TELEVISION), cargar_descriptores_comerciales(RUTA_COMERCIALES, listar_archivos_en_carpeta), True)
