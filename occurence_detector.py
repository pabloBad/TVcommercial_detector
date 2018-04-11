import numpy as np

from detection import *


def sequence_detector(detected_sequence, min_percentage_sequence_numbers, min_amount_sequence_numbers):
    """Detects a minimun sequence numbers in a detected sequence.

    Arguments:
        detected_sequence {ndarray} -- The detected sequence of minimun distance frames
        min_amount_sequence_numbers {num} -- Indicates the minimun amount of numbers in a sequence
        min_percentage_sequence_numbers {num} --Indicates the minimun sequence number that must be present on the given sequence.

    Returns:
        boolean -- Indicates if the are or not a minimum amount of sequence numbers in the detected sequence.
    """
    # Step 1: Lenght
    if len(detected_sequence) < min_amount_sequence_numbers:
        return False

    # Step 2: Percentage of sequence numbers:

    acc = 0
    sequence_numbers = np.arange(len(detected_sequence))
    unique_frames = []

    for min_dist_frame in detected_sequence:
        if np.isin(min_dist_frame[2], sequence_numbers) and min_dist_frame[2] not in unique_frames:
            unique_frames.append(min_dist_frame[2])
            acc += 1
    
    return acc / len(detected_sequence) > min_percentage_sequence_numbers

def clean_sequence(detected_sequence, max_repeated_elements = 6):

    # Outliers verification
    other_vid_name = [*detected_sequence][0]

    original_video_frames = [frame_tuple[0] for frame_tuple in detected_sequence[other_vid_name]]

    elapsed_video_time = [frame_tuple[1] for frame_tuple in detected_sequence[other_vid_name]]
    min_distance_frames = [frame_tuple[2] for frame_tuple in detected_sequence[other_vid_name]]

    frame_mean = np.mean(original_video_frames, axis=0)
    frame_sd = np.std(original_video_frames, axis=0)

    time_mean = np.mean(elapsed_video_time, axis=0)
    time_sd = np.std(elapsed_video_time, axis=0)

    min_dist_frames_mean = np.mean(min_distance_frames, axis=0)
    min_dist_frames_sd = np.std(min_distance_frames, axis=0)


    cleaned_sequence_no_outliers = [frame_tuple  for frame_tuple in detected_sequence[other_vid_name] 
        if (frame_tuple[0] > frame_mean - 2 * frame_sd and frame_tuple[0] < frame_mean + 2 * frame_sd)
            and (frame_tuple[1] > time_mean - 2 * time_sd and frame_tuple[1] < time_mean + 2 * time_sd)
            and (frame_tuple[2] > min_dist_frames_mean - 2 * min_dist_frames_sd and frame_tuple[2] < min_dist_frames_mean + 2 * min_dist_frames_sd)]

    # Clean repeated sequences of elements :

    if (cleaned_sequence_no_outliers != []):
        # print ("Entre aqui!!", other_vid_name)
        cleaned_sequence_no_repeated = [cleaned_sequence_no_outliers[0]]
        repeated_count = 0
        repeated_element = cleaned_sequence_no_outliers[0]
        # Starts for the second element (i+1)
        for i in range(len(cleaned_sequence_no_outliers) - 1):
            cleaned_sequence_no_repeated.append(cleaned_sequence_no_outliers[i+1])
            
            if (repeated_element[2] == cleaned_sequence_no_outliers[i+1][2]):
                repeated_count += 1
                # print(repeated_count)
                if (repeated_count >= max_repeated_elements):
                    # print (cleaned_sequence_no_outliers)
                    while (repeated_count != 0):
                        cleaned_sequence_no_repeated.pop()
                        repeated_count -= 1
            else : 
                repeated_element = cleaned_sequence_no_outliers[i+1]
                repeated_count = 0

        return {other_vid_name :cleaned_sequence_no_repeated}
    else:
        return {other_vid_name : cleaned_sequence_no_outliers}



def extract_time_from_detected_sequence(detected_sequence):

    # Clean Sequence
    min_frame = np.inf
    min_idx = 0
    for index, element in enumerate(detected_sequence):
        # element[0] -> frame of the analyzed video
        # element[1] -> elapsed time for the beginning of the video
        # element[2] -> min distance frame

        if element[2] < min_frame:
            min_frame = element[2]
            min_idx = index
    return (detected_sequence[min_idx][1], detected_sequence[-1][1], detected_sequence[min_idx][2], detected_sequence[-1][2])


def extract_longest_sequence(similarity_search_results, current_index, window_size):
    """
    Extract the sequence with larger set of min distance frames into a window of the similarity search results array to a dictionary. 
    The key of the dictionary are the other video name.

    Arguments:
        similarity_search_results {tuple} -- tuple with the following components:
         ('analyzed_video_frame','elapsed_time', 'other_vid_name', 'min_dist_frame')
        current_index {int} - Current index of the extraction
        windows_size {int} - Size of the 
    Returns:
        [dict] -- Dictionary with the sequences. Example: { 'vid1' : [('analized_video_frame', 'elapsed_time', 'min_dist_frame')]}

    """

    # Analize by window. Save any sequence in dictionary
    sequences = {}
    for search_result in similarity_search_results[current_index:current_index + window_size]:
        # search_result[0] -> analyzed_video_frame
        # search_result[1] -> elapsed_time
        # search_result[2] -> other_vid_name
        # search_result[3] -> min_dist_frame

        if (search_result[2] in sequences):
            sequences[search_result[2]].append(
                (int(search_result[0]), float(search_result[1]), int(search_result[3])))
        else:
            sequences[search_result[2]] = [
                (int(search_result[0]), float(search_result[1]), int(search_result[3]))]

    longest_sequence = []
    longest_sequence_name = ''

    for other_vid_name in sequences:
        if (len(sequences[other_vid_name]) > len(longest_sequence)):
            longest_sequence = sequences[other_vid_name]
            longest_sequence_name = other_vid_name
    return {longest_sequence_name: longest_sequence}


def occurence_detector(
        similarity_search_results,
        window_size,
        min_amount_sequence_numbers,
        min_percentage_sequence_numbers,
        skip_frames,
        debug=True):
    # similarity_search_results: Array of tuples
    # result_tuple = ('analyzed_video_frame','elapsed_time', 'other_vid_name', 'min_dist_frame')
    #                (3172, 952584.9666666667, 'scotiabank', 8),

    detections = []

    # order of the algorithm o(len(similarity_search_results) * window_size)
    for i in range(len(similarity_search_results) - window_size):

        # Skip some frames
        if i % skip_frames != 0:
            pass

        else:
            # Extract all min distance frames of the similarity search results window to a dictionary
            # Not yet processed
            raw_longest_sequence = extract_longest_sequence(similarity_search_results, i, window_size)
             
            cleaned_sequences = raw_longest_sequence 
            cleaned_sequences_tmp = clean_sequence(cleaned_sequences)
            while (cleaned_sequences != cleaned_sequences_tmp):
                cleaned_sequences = cleaned_sequences_tmp
                cleaned_sequences_tmp = clean_sequence(cleaned_sequences_tmp)

            # For each detected sequence by other video name:
            for other_vid_name in cleaned_sequences.keys():

                    if (debug):
                        cmd = input('Enter Command:')
                        if (cmd == 'm'):
                            import pprint
                            print (other_vid_name)
                            pp = pprint.PrettyPrinter(indent=4)
                            pp.pprint(cleaned_sequences[other_vid_name])
                        elif (cmd == 'q'):
                            exit()
                        elif (cmd == 'd'):
                            debug = False
                # if i have a sequence detected, i calculate the time of those and then append it to the detections array
                if (sequence_detector(cleaned_sequences[other_vid_name], min_percentage_sequence_numbers, min_amount_sequence_numbers)):

                    init_time, end_time, init_frame, end_frame = extract_time_from_detected_sequence(
                        cleaned_sequences[other_vid_name])

                    # print (other_vid_name, init_time, end_time)
                    # Add the detection to detection object
                    if len(detections) == 0:
                        detections.append(
                            detection(other_vid_name, init_time, end_time, init_frame, end_frame))
                    else:
                        is_in_detections = False
                        for detection_instance in detections:

                            if (detection_instance.is_in_detection(other_vid_name, init_time, end_time, init_frame, end_frame)):
                                detection_instance.extend_detection(
                                    other_vid_name, init_time, end_time, init_frame, end_frame)
                                is_in_detections = True
                        if not is_in_detections:

                            print (other_vid_name, init_time, end_time, init_frame, end_frame)
                            # input()
                            detections.append(
                                detection(other_vid_name, init_time, end_time, init_frame, end_frame))

    return [detection_instance.get_init_time_and_length() for detection_instance in detections]
