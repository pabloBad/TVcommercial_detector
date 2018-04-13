import cv2
import numpy as np
import os.path
import time

from matplotlib import pyplot as plt
from file_functions import save_feature_vector_array, open_video

# ---------------------------------------------------------------------------------------------
# ----------------------------- Feature Vector Extraction -----------------------------
# ---------------------------------------------------------------------------------------------

def normalize_vector(v):
    """Normaliza un vector numpy de una dimension y luego lo retorna.

    Arguments:
        vector {ndarray} -- Vector de entrada por normalizar.

    Returns:
        ndarray -- Vector con los valores normalizados
    """
    norm = np.linalg.norm(v, ord=1)
    if norm == 0:
        norm = np.finfo(v.dtype).eps
    return v/norm


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


def histogram_by_parts(frame, rows_of_division, cols_of_division, bins, debug=False):
    """
    Divide un frame en la cantidad de filas y columnas dadas, para que en cada uno de los
    subframes calcule su vector histograma, los contatene en un solo gran vector y luego lo retorna.

    Arguments:
        frame {[ndarray]} -- Frame por procesar.

    Keyword Arguments:
        filas {int} -- Numero de filas en la que se desea dividir el frame (default: {4})
        columnas {int} -- Numero de columnas en la que se desea dividir el frame (default: {4})
        bins {int} -- Numero de bins que tendra el histograma de cada subframe (default: {16})
        debug {bool} -- Indica si se mostraran las imagenes para hacer debug (default: {True})

    Returns:
        ndarray(uint) -- Arreglo con los histogramas de cada subframe concatenados.
    """
    roi_height = int(frame.shape[0] / rows_of_division)
    roi_width = int(frame.shape[1] / cols_of_division)

    hists_concatenados = []

    if debug:
        histogramas = []
        frames = []

    for x in range(0, rows_of_division):
        for y in range(0, cols_of_division):
            # Obtains the current ROI:
            current_frame = frame[x*roi_height:(x+1) *
                                 roi_height, y*roi_width:(y+1)*roi_width]
            # Calculate the normalized histogram for this ROI
            histr = normalize_vector(cv2.calcHist([current_frame], [0], None, [bins], [0, 256]))

            hists_concatenados.append(histr.flatten())
            if debug:
                histogramas.append(histr)
                frames.append(current_frame)

    # Debug: Print histograms
    if debug:
        cmd = input(
            "Command? (m -> Show frame hists, q -> Quit, d -> Disable debug, * -> Skip)\n")

        if (cmd == 'm'):
            fig1 = plt.figure(1)
            plt.subplot(121)
            for enum_frame in list(enumerate(frames)):
                plt.subplot(rows_of_division, cols_of_division, enum_frame[0] + 1)
                plt.imshow(enum_frame[1], cmap='gray',
                           interpolation='nearest')

            fig2 = plt.figure(2)
            plt.subplot(122)
            for enum_hists in list(enumerate(histogramas)):
                plt.subplot(rows_of_division, cols_of_division, enum_hists[0] + 1)
                plt.plot(enum_hists[1])
            plt.show()
            map(print, frames)
            print("Concatenated histograms value\n", np.array(
                hists_concatenados, dtype="float").flatten())

        elif (cmd == 'q'): exit()
        elif (cmd == 'd'): debug = False

    return np.array(hists_concatenados, dtype="float").flatten()


# -------------------------------------------------------------------------------------------
# ----------------------------- Extractor Caracteristicas Video -----------------------------
# -------------------------------------------------------------------------------------------

def extract_video_feature(
    video_path, 
    rows_of_division , 
    cols_of_division, 
    bins,
    fps_target=3, 
    save_results = True, 
    debug=False):
    """
    Extrae los descriptores de los frames del video segun el numero de frames por segundo deseados.
    Finaliza guardando el tiempo transcurrido desde el inicio del video mas el vector caracteristico de 
    cada frame  en un archivo .dat en el directorio temp/

    Arguments:
        video_path {string} -- Ruta del video.
        fps_target {[type]} -- Numero de Frames objetivo que se quieren procesar por cada segundo del video.
        feature_vector_function {function} -- Funcion que extraera el vector caracteristico de cada frame procesado.
        save_feature_vectors {number} -- Indica si se guardaran los feature vectors o se utilizaran en memoria.
        debug {boolean} -- Indica si se mostraran frames de prueba.
    """

    video = open_video(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    video_detected_fps = int(video.get(cv2.CAP_PROP_FPS))
    # Indica cuantos frames seran leidos por segundo.
    fps = int(video_detected_fps/fps_target)

    # Inicializamos variables
    feature_vector_array = []
    start_time = time.time()

    print("Starting feature vector extraction for:", os.path.basename(video_path))

    for i in range(total_frames):
        ret, frame = video.read()
        # Skip no relevant frames (3 frames per second)
        if i % fps == 0:
            # Transform frame into grayscale and then, blurry
            grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred_frame = cv2.blur(grey_frame,(10,10)) 

            feature_vector_array.append(
                {
                    # Timestamp in miliseconds between start of the video and this frame
                    "elapsed_time": video.get(cv2.CAP_PROP_POS_MSEC),
                    # Calculated feature vector
                    "feature_vector": histogram_by_parts(blurred_frame, rows_of_division, cols_of_division, bins, debug=debug)
                })
               
    print("End of video processing. Elapsed time:", get_time_difference(start_time, time.time()), '\n')

    if (save_results):
        save_feature_vector_array(video_path, np.array(feature_vector_array))
    return np.array(feature_vector_array) 