import numpy as np
from os import listdir
from os.path import isfile, join, abspath, exists, basename

# ------------------------------------------------------------------------------------------------
# ----------------------------------- Manipulacion de Archivos -----------------------------------
# ------------------------------------------------------------------------------------------------


def listar_archivos_en_carpeta(ruta, debug=True):
    archivos = [abspath(join(ruta, f))
                for f in listdir(ruta) if isfile(join(ruta, f))]
    if (debug):
        print("Archivos encontrados en", ruta, ":\n", archivos, '\n')
    return archivos


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
            for vector_caracteristicas in listar_archivos_en_carpeta(ruta)]

    # return list(map(lambda abs_path: (basename(abs_path).split('.')[0], cargar_descriptor(abs_path)), listar_archivos_en_carpeta(ruta)))
