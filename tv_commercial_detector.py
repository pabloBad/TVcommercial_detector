from os import listdir, makedirs
from os.path import isfile, join, exists, abspath, basename
import numpy as np

from manejo_archivos import listar_archivos_en_carpeta, cargar_descriptores_comerciales, cargar_descriptor
from extractor_caracteristicas import extarer_caracteristicas
from busqueda_por_similitud import similarity_search
from apparition_detector import apparition_detector


def execute_feature_extraction(ruta_television, ruta_comerciales, debug=False):

    videos_comerciales = listar_archivos_en_carpeta(ruta_comerciales)
    videos_television = listar_archivos_en_carpeta(ruta_television)

    if not exists("temp/"):
        makedirs("temp/")

    print("Extrayendo caracteristicas de comerciales:\n")
    list(map(extarer_caracteristicas, videos_comerciales))

    print("Extrayendo caracteristicas de las grabaciones de tv:\n")
    list(map(extarer_caracteristicas, videos_television))


def execute_similarity_search_one_video(analyzed_video_name, analyzed_video_descriptors, comparate_videos_descriptors, debug=False):
    return {'analyzed_video_name': analyzed_video_name,
            'similarity_search_result_tuple': similarity_search(analyzed_video_descriptors, comparate_videos_descriptors, debug=True)}


def execute_similarity_search(analyzed_videos_path, comparated_videos_path, debug=False):
    comparated_videos_descriptors_vectors = cargar_descriptores_comerciales(
        comparated_videos_path)

    similarity_search_results_by_video = []

    for analyzed_video_descriptors_file in listar_archivos_en_carpeta(analyzed_videos_path):
        print("Procesando el vector descriptor del video",
              basename(analyzed_video_descriptors_file))
        similarity_search_results_by_video.append(
            execute_similarity_search_one_video(basename(analyzed_video_descriptors_file), cargar_descriptor(analyzed_video_descriptors_file), comparated_videos_descriptors_vectors, debug=debug))

        # TODO eliminar esta linea de codigo.....
        if (True):
            break
    return np.array(similarity_search_results_by_video)


def execute_apparition_detector_one_video(similarity_search_result_tuple):
    # window size = 120 -> aprox 40 seconds of window
    return apparition_detector(similarity_search_result_tuple, 120, 20, 0.4, 30)



def execute_apparition_detector(similarity_search_results_by_video):
    for similarity_search_result in similarity_search_results_by_video:
        # similarity_search_result = {'analyzed_video_name','similarity_search'}
        # similarity_search_result_tuple = ('analyzed_video_frame','elapsed_time', 'other_vid_name', 'min_dist_frame')
        execute_apparition_detector_one_video(
            similarity_search_result['similarity_search_result_tuple'])
    return


def main():
    RUTA_COMERCIALES = "videos/comerciales/"
    RUTA_TELEVISION = "videos/television/"

    RUTA_TEMPORAL_COMERCIALES = "temp/comerciales"
    analyzed_videos_path = "temp/television"

    DEBUG = False

    # Paso 1: Procesamos todos los videos al generar los vectores de caracteristicas
    # de cada uno de ellos para posteriormente guarlos:

    # TODO SACAR ESTE COMENTARIO....
    # execute_feature_extraction(RUTA_TELEVISION, RUTA_COMERCIALES, DEBUG)

    # Paso 2: Hacemos la busqueda por similitud mediante el calculo de un ranking de
    # frames similares entre un frame del video de television y todos los frames de
    # todos los comerciales, usando funciones de distancia de caracteristicas.
    # results = execute_similarity_search(
    #     analyzed_videos_path, RUTA_TEMPORAL_COMERCIALES, False)

    # np.save("temp/test_1.npy", results)
    # Paso 3: Ejecutamos la deteccion de apariciones...

    execute_apparition_detector(np.load('temp/test_1.npy'))


main()
