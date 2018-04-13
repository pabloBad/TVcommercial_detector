from module_wrapper import execute_feature_extraction,execute_occurrence_detector, execute_similarity_search, save_results

def main():

    # PATHS:
    ANALYZED_VIDEO_PATH = "videos/comerciales/"
    OTHER_VIDEO_PATH = "videos/television/"

    TEMPORAL_FEATURE_ANALYZED_VIDEO_PATH = "temp/television"
    TEMPORAL_FEATURE_OTHER_VIDEO_PATH = "temp/comerciales"

    TEMPORAL_SIMILARITY_SEARCH_PATH = "temp/similarity_search"

    DEBUG = False

    # PARAMETERS:

    # Feature Extraction
    ROWS_OF_DIVISION = 6
    COLS_OF_DIVISION = 6
    BINS = 16
    FPS_TARGET = 3
    SAVE_FILES = True

    # Similarity Search

    # Distance options: manhattan_distance, euclidean_distance, chebychev_distance, hamming_distance, chebychev_distance
    DISTANCE_FUNCTION = 'manhattan_distance'
    SAVE_FILES_2 = True

    # Occurrence Detector
    MIN_SEQUENCE_LENGHT = 20
    MAX_DIFFERENCE_BETWEEN_FRAMES = 7
    MAX_PERCENTAGE_REPEATED_ELEMENTS = 0.66

    # Step 1: Perform a feature extraction of all frames of all videos on the specified folders:
    execute_feature_extraction(ANALYZED_VIDEO_PATH, OTHER_VIDEO_PATH, ROWS_OF_DIVISION, COLS_OF_DIVISION, BINS, FPS_TARGET, SAVE_FILES, debug=False)

    # Step 2: Perform the similarity search between the analyzed videos and the others videos:
    execute_similarity_search(TEMPORAL_FEATURE_ANALYZED_VIDEO_PATH, TEMPORAL_FEATURE_OTHER_VIDEO_PATH, DISTANCE_FUNCTION, SAVE_FILES_2, debug = False)

    # Step 3: Execute the occurrence 
    ocurrences_detected = execute_occurrence_detector(TEMPORAL_SIMILARITY_SEARCH_PATH, MIN_SEQUENCE_LENGHT, MAX_DIFFERENCE_BETWEEN_FRAMES, MAX_PERCENTAGE_REPEATED_ELEMENTS, debug=DEBUG)

    # Extra steps...

    # Step 4: Write dettections
    save_results (ocurrences_detected)

    # Step 5:Execute evaluar_v2.py
    from subprocess import call
    call(["python", "evaluar_v2.py","detecciones.txt"])

main()
