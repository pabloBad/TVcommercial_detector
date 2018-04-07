import cv2
import numpy as np
import os.path
import time

from matplotlib import pyplot as plt


def vectorIntensidades(frame):
    # frame = cv2.resize(frame, (size_x, size_y))
    pass

# ---------------------------------------------------------------------------------------------
# ----------------------------- Extraccion Vector Caracteristicas -----------------------------
# ---------------------------------------------------------------------------------------------


def calcular_histograma(frame, bins=16):
    """Calcula el histograma del frame entregado. Retorna un arreglo en donde cada valor esta representado como un subarreglo del padre.

    Arguments:
        frame {[ndarray]} -- Frame al cual se le calculara el histograma

    Keyword Arguments:
        bins {int} -- Numero de bins del histograma a calcular (default: {16})

    Returns:
        [ndarray] -- Arreglo con el histograma
    """

    return cv2.calcHist([frame], [0], None, [bins], [0, 256])


def normalizarVector(v):
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


def histogramaPorPartes(frame, filas=4, columnas=4, bins=16, debug=False):
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

    roi_height = int(frame.shape[0] / filas)
    roi_width = int(frame.shape[1] / columnas)

    hists_concatenados = []

    if debug:
        histogramas = []
        frames = []

    for x in range(0, filas):
        for y in range(0, columnas):
            # Calculamos el histograma del roi actual:
            frame_actual = frame[x*roi_height:(x+1) *
                                 roi_height, y*roi_width:(y+1)*roi_width]
            histr = normalizarVector(
                calcular_histograma(frame_actual, bins=bins))
            hists_concatenados.append(histr.flatten())
            if debug:
                histogramas.append(histr)
                frames.append(frame_actual)

    # Codigo para debugear e imprimir histogramas
    if debug:
        cmd = input(
            "Comando? (m -> mostrar frame, q -> salir, d -> desactivar debug, otro -> omitir)\n")

        if (cmd == 'm'):
            fig1 = plt.figure(1)
            plt.subplot(121)
            for enum_frame in list(enumerate(frames)):
                plt.subplot(filas, columnas, enum_frame[0] + 1)
                plt.imshow(enum_frame[1], cmap='gray',
                           interpolation='nearest')

            fig2 = plt.figure(2)
            plt.subplot(122)
            for enum_hists in list(enumerate(histogramas)):
                plt.subplot(filas, columnas, enum_hists[0] + 1)
                plt.plot(enum_hists[1])
            plt.show()
            map(print, frames)
            print("Histogramas Concatenados\n", np.array(
                hists_concatenados, dtype="float").flatten())
        if (cmd == 'q'):
            exit()
        elif (cmd == 'd'):
            debug = False

    return np.array(hists_concatenados, dtype="float").flatten()


# -------------------------------------------------------------------------------------
# ----------------------------- Funciones Manejo Archivos -----------------------------
# -------------------------------------------------------------------------------------

def abrir_video(ruta):
    """Abre un video utilizando un objeto cv2. Retorna una tupla con el objeto con el video, la cantidad de frames y de fps.

    Arguments:
        ruta {String} -- Ruta al archivo.

    Raises:
        Exception -- Archivo no existe.

    Returns:
        (cv2.VideoCapture, total_frames, fps_video) -- Tupla contenedora de: objeto lector del video, total de frames del video y fps promedio del video.
    """

    if (not os.path.isfile(ruta)):
        raise Exception("Archivo no encontrado: " + ruta)

    cap = cv2.VideoCapture(ruta)
    return cap


def guardar_descriptor(ruta_video, vector_de_descriptores):
    """Guarda el descriptor calculado binarizandolo (con numpy) en la ruta temp/ + tipo_video/ + video.npy

    Arguments:
        ruta_video {String} -- Ruta completa hacia el video
        vector_de_descriptores {ndarray} -- Arreglo de vectores carcteristicos que sera guardado en la ruta
    """

    if not os.path.exists("temp/" + os.path.basename(os.path.dirname(ruta_video))):
        os.makedirs("temp/" + os.path.basename(os.path.dirname(ruta_video)))
    np.save("temp/" + os.path.basename(os.path.dirname(ruta_video)) + '/' + os.path.basename(ruta_video).split(".")
            [0] + ".npy", vector_de_descriptores)

# -------------------------------------------------------------------------------------------
# ----------------------------- Extractor Caracteristicas Video -----------------------------
# -------------------------------------------------------------------------------------------


def extarer_caracteristicas(ruta_video, frames_cada_segundo=3, funcion_vector_caracteristico=histogramaPorPartes, FPS_video_manual=None, debug=False):
    """
    Extrae los descriptores de los frames del video segun el numero de frames por segundo deseados.
    Finaliza guardando el tiempo transcurrido desde el inicio del video mas el vector caracteristico de 
    cada frame  en un archivo .dat en el directorio temp/

    Arguments:
        ruta_video {string} -- Ruta del video.
        frames_cada_segundo {[type]} -- Numero de Frames objetivo que se quieren procesar por cada segundo del video.
        funcion_vector_caracteristico {function} -- Funcion que extraera el vector caracteristico de cada frame procesado.
        FPS_video_manual {number} -- Entrega el fps con la que se considerara el video y lo reemplaza por el entregado con cv2.
        debug {boolean} -- Indica si se mostraran frames de prueba.
    """

    video = abrir_video(ruta_video)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    
    # Indica cuantos frames seran leidos por segundo.
    frames_objetivo = int(fps/frames_cada_segundo)

    # Inicializamos variables
    vector_de_descriptores = []
    tiempo_inicio = time.time()

    # Calculamos numero de fps por procesar:
    # formula : fps/frames_cada_segundo * frames_totales
    # Si FPS_video_manual es entregado como parametro, utilizamos este en vez de la
    if (FPS_video_manual != None):
        fps_totales_por_procesar = (
            (FPS_video_manual / frames_cada_segundo) * total_frames)
    else:
        fps_totales_por_procesar = ((fps / frames_cada_segundo) * total_frames)

    proporcion_frames_imprimir = round(fps_totales_por_procesar / float(10))

    for i in range(total_frames):
        ret, frame = video.read()
        # Leemos el frame si corresponde, de lo contrario lo ignoramos.
        if i % frames_objetivo == 0:
            # Transformar frame a escala de grises
            frame_gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            vector_de_descriptores.append(
                {
                    # Tiempo transcurrido entre el frame y el inicio del video en milisegundos.
                    "tiempo_transcurrido": video.get(cv2.CAP_PROP_POS_MSEC),
                    # Vector caracteristico del frame-
                    "vector_caracteristico": funcion_vector_caracteristico(frame_gris, debug=debug)
                })

            # Imprimimos estado del procesamiento
            if i % proporcion_frames_imprimir == 0:
                print("Video:", os.path.basename(ruta_video).split(".")[0], "\tPorcentaje de Avance:", round(
                    (i/fps_totales_por_procesar) * 1000, 3), "%", "\tTiempo tomado:", diferencia_tiempos(tiempo_inicio, time.time()))

    print("Finalizado procesamiento video:",  os.path.basename(ruta_video).split(
        ".")[0], "\tTiempo total:", diferencia_tiempos(tiempo_inicio, time.time()), '\n')

    # Guardamos los descriptores y terminamos la extraccion
    guardar_descriptor(ruta_video, np.array(vector_de_descriptores))
    return 
