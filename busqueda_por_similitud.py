import numpy as np
import time
import os.path

from funciones_distancia import *
from manejo_archivos import cargar_descriptor, listar_archivos_en_carpeta
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
                descriptor_frame_tv, descriptor_comercial[1]["vector_caracteristico"])
            if (distancia_calculada < frame_minima_distancia[2]):
                frame_minima_distancia = (
                    vector_descriptor_comercial[0],  # Nombre del comercial
                    descriptor_comercial[0],        # Frame del comercial.
                    distancia_calculada)            # Distancia calculada

        # Extraigo los primeros n resultados del ranking y retorno

    # Retornamos solo el comercial y el numero del frame
    return (frame_minima_distancia[0], frame_minima_distancia[1])


def busqueda_por_similitud(vector_descriptor_video_tv, vectores_descriptores_comerciales, debug=False):

    # vector_descriptor_video_tv[0] -> Tiempo desde el inicio del frame
    # vector_descriptor_video_tv[1] -> Vector caracteristico del frame
    tiempo_inicial = time.time()
    print(len(vector_descriptor_video_tv))

    proporcion_aviso = round(len(vector_descriptor_video_tv) /
                             10) if round(len(vector_descriptor_video_tv)/10) != 0 else 1

    ranking_acumulado_por_descriptor = []

    for descriptor in enumerate(vector_descriptor_video_tv):
        # descriptor[0] -> Numero del frame al que se le esta calculando el ranking
        # descriptor[1] -> Objeto con el vector caracteristico + tiempo transcurrido al que se le calculara el frame del comericial con menor distancia.

        ranking_calculado = {
            'num_frame': descriptor[0],
            'tiempo_transcurrido' : descriptor[1]["tiempo_transcurrido"],
            # TODO ELEGIR ENTRE ESTO O EL SIGUIENTE
            # 'ranking_min_dist' : ranking_primeros_n(descriptor[1], vectores_descriptores_comerciales, 5, distancia_manhattan, False)
            'frame_min_distancia': calcular_frames_minima_distancia(descriptor[1]["vector_caracteristico"], vectores_descriptores_comerciales, distancia_euclideana, False)
        }
        ranking_acumulado_por_descriptor.append(ranking_calculado)

        if ((descriptor[0] + 1) % proporcion_aviso) == 0:
            
            print("Procesando distancias comerciales frame",
                  (descriptor[0] + 1),
                  "/",
                  len(vector_descriptor_video_tv),
                  "\t Tiempo tomado:",
                  diferencia_tiempos(tiempo_inicial, time.time()))
            if (debug):
                cmd = input(
                    "Comando? (m -> mostrar distancia calculada, q -> salir, d -> desactivar debug, otro -> omitir)\n")
                if (cmd == 'm'):
                    import pprint
                    pp = pprint.PrettyPrinter(indent=4)
                    pp.pprint(ranking_acumulado_por_descriptor)
                elif (cmd == 'l'):
                    import pprint
                    pp = pprint.PrettyPrinter(indent=4)
                    pprint.pprint(ranking_acumulado_por_descriptor, open('log.txt', 'w'))
                elif (cmd == 'q'):
                    exit()
                elif(cmd == 'd'):
                    debug = False

    return np.array(ranking_acumulado_por_descriptor)

# DEBUG
# RUTA_COMERCIALES = "temp/comerciales/"
# RUTA_TELEVISION = "temp/television/mega-2014_04_10.npy"
# print (cargar_descriptores_comerciales(RUTA_COMERCIALES, listar_archivos_en_carpeta))
# busqueda_por_similitud(cargar_descriptor(RUTA_TELEVISION), cargar_descriptores_comerciales(RUTA_COMERCIALES, listar_archivos_en_carpeta), True)
