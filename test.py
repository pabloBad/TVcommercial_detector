from funciones_distancia import *
# Test funciones de distancia:

assert distancia_hamming([1,2,4,5,6], [1,3,5,5,7]) == 3
assert distancia_manhattan([1,2,4,5,6], [1,3,5,5,7]) == 3  
assert distancia_manhattan([1,2,4], [2,6,2]) == 7
assert distancia_hamming([1,2,4], [2,6,2]) == 3

# assert np.all(obtenerVectorCaracteristico("""videos/comerciales/vtr.mpg""", 3, histogramaPorPartes) == np.load('temp/vtr.npy'))