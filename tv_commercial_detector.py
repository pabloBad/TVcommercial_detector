from os import listdir, makedirs
from os.path import isfile, join, exists, abspath, basename

from manejo_archivos import listar_archivos_en_carpeta, cargar_descriptores_comerciales, cargar_descriptor
from extractor_caracteristicas import extarer_caracteristicas
from busqueda_por_similitud import busqueda_por_similitud


def ejecutar_extraccion_caracteristicas(ruta_television, ruta_comerciales, debug = False):

    videos_comerciales = listar_archivos_en_carpeta(ruta_comerciales)
    videos_television = listar_archivos_en_carpeta(ruta_television)

    if not exists("temp/"):
        makedirs("temp/")

    print("Extrayendo caracteristicas de comerciales:\n")
    list(map(extarer_caracteristicas, videos_comerciales))

    print ("Extrayendo caracteristicas de las grabaciones de tv:\n")
    list(map(extarer_caracteristicas, videos_television))

def ejecutar_busqueda_por_similitud(ruta_temporal_television, ruta_temporal_comerciales, debug=False):
    vectores_descriptores_comerciales = cargar_descriptores_comerciales(ruta_temporal_comerciales)
    resultados_busqueda_por_similitud = []
    for archivo_vector_caracteristicas_television in listar_archivos_en_carpeta(ruta_temporal_television):
        print("Procesando el vector descriptor del video", basename(archivo_vector_caracteristicas_television))

        ranking_por_video = {
            'nombre_video_tv' : basename(archivo_vector_caracteristicas_television),
            'resultados_busqueda' : busqueda_por_similitud(cargar_descriptor(archivo_vector_caracteristicas_television), vectores_descriptores_comerciales, debug=True)
            }
        resultados_busqueda_por_similitud.append(ranking_por_video)
        # if (debug) :
        #     i = 0
        #     for key in resultados_busqueda_por_similitud[-1].keys():
        #         print (resultados_busqueda_por_similitud[-1][key])
        #         if i == 100: 
        #             break

        if False:
            break

    return resultados_busqueda_por_similitud

def main():
    RUTA_COMERCIALES = "videos/comerciales/"
    RUTA_TELEVISION = "videos/television/"

    RUTA_TEMPORAL_COMERCIALES = "temp/comerciales"
    RUTA_TEMPORAL_TELEVISION = "temp/television"
    
    DEBUG = False

    # Paso 1: Procesamos todos los videos al generar los vectores de caracteristicas 
    # de cada uno de ellos para posteriormente guarlos:
    
    #TODO SACAR ESTE COMENTARIO....
    # ejecutar_extraccion_caracteristicas(RUTA_TELEVISION, RUTA_COMERCIALES, DEBUG)

    # Paso 2: Hacemos la busqueda por similitud mediante el calculo de un ranking de 
    # frames similares entre un frame del video de television y todos los frames de 
    # todos los comerciales, usando funciones de distancia de caracteristicas.
    ejecutar_busqueda_por_similitud(RUTA_TEMPORAL_TELEVISION,RUTA_TEMPORAL_COMERCIALES, True )

    
main()


