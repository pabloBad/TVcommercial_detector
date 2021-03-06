import numpy as np
from os import listdir, makedirs
from os.path import isfile, join, abspath, exists, basename, dirname
import cv2

# ------------------------------------------------------------------------------------------------
# ----------------------------------- Manipulacion de Archivos -----------------------------------
# ------------------------------------------------------------------------------------------------


def list_files_in_folder(path, debug=True, return_basenames=False):
    files = [abspath(join(path, f))
                for f in listdir(path) if isfile(join(path, f))]
    if (debug):
        print("Founded files in", path, ":\n", [
              basename(file_name) for file_name in files], '\n')
    if (return_basenames):
        return [basename(file_name) for file_name in files]

    return files

def cargar_descriptor(ruta):
    if (exists(ruta)):
        return np.load(ruta)
    else:
        msg = "Ruta no encontrada: " + ruta
        raise ValueError(msg)


def cargar_descriptores_comerciales(ruta):
    """Retorna el nombre de los comerciales mas un arreglo con el vector contenedor de los descriptores, localizados en la ruta entregada como parametro.
    Elimina el tiempo transcurrido.

    Arguments:
        ruta {string} -- Ruta hacia los videos comerciales
        lector_rutas {function} -- Funcion encargada de leer todos los archivos en la ruta entregada y retornarlos como un arreglo

    Returns:
        [tuple] -- Retorna la tupla (nombre_vector_caracteristicas_video, descriptor_video)
    """
    return [(basename(vector_caracteristicas).split('.')[0], cargar_descriptor(vector_caracteristicas))
            for vector_caracteristicas in list_files_in_folder(ruta)]


def open_video(path):
    """Abre un video utilizando un objeto cv2. Retorna una tupla con el objeto con el video, la cantidad de frames y de fps.

    Arguments:
        path {String} -- Ruta al archivo.

    Raises:
        Exception -- Archivo no existe.

    Returns:
        (cv2.VideoCapture, total_frames, fps_video) -- Tupla contenedora de: objeto lector del video, total de frames del video y fps promedio del video.
    """

    if (not isfile(path)):
        msg = "File not found: " + path
        raise Exception(msg)
    return cv2.VideoCapture(path)


def save_feature_vector_array(video_path, feature_vector_array):
    """Guarda el descriptor calculado binarizandolo (con numpy) en la ruta temp/ + tipo_video/ + video.npy

    Arguments:
        ruta_video {String} -- Ruta completa hacia el video
        feature_vector_array {ndarray} -- Arreglo de vectores carcteristicos que sera guardado en la ruta
    """

    if not exists("temp/" + basename(dirname(video_path))):
        makedirs("temp/" + basename(dirname(video_path)))

    np.save("temp/" + basename(dirname(video_path)) + '/' + basename(video_path).split(".")
            [0] + ".npy", feature_vector_array)


def save_similarity_search_results(analyzed_video_name, similarity_search_result):
    """Stores similarity search results

    Arguments:
        analyzed_video_name {String} -- Analyzed video name
        similarity_search_result {ndarray} -- Arreglo de vectores carcteristicos que sera guardado en la ruta
    """

    if not exists("temp/similarity_search"):
        makedirs("temp/similarity_search")
    print("Saving results on temp/similarity_search/" + analyzed_video_name)
    np.save("temp/similarity_search/" +
            analyzed_video_name, similarity_search_result)

def load_similarity_search_results(filename):
    return np.load("temp/similarity_search/" + filename)
