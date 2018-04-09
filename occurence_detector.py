import numpy as np

from detection import *

def sequence_detector(detected_sequence, min_percentage_sequence_numbers):
    """Detects a minimun sequence numbers in a detected sequence.

    Arguments:
        detected_sequence {ndarray} -- The detected sequence of minimun distance frames
        min_percentage_sequence_numbers {num} --Indicates the minimun sequence number that must be present on the given sequence.

    Returns:
        boolean -- Indicates if the are or not a minimum amount of sequence numbers in the detected sequence.
    """

    acc = 0
    sequence_numbers = np.arange(len(detected_sequence))
    unique_frames = []

    for min_dist_frame in detected_sequence:
        if np.isin(min_dist_frame[1], sequence_numbers) and min_dist_frame[1] not in unique_frames:
            unique_frames.append(min_dist_frame[1])
            acc += 1
    return acc / len(detected_sequence) > min_percentage_sequence_numbers

def extract_time_from_detected_sequence(detected_sequence):

    # Clean Sequence
    min_frame=np.inf
    min_idx=0
    for index, element in enumerate(detected_sequence):
        # print (element, element[0], element[1])
        if element[1] < min_frame:
            min_frame=element[1]
            min_idx=index
    return (detected_sequence[min_idx][0], detected_sequence[-1][0])


def occurence_detector(
    similarity_search_results, 
    window_size, 
    min_amount_sequence_numbers, 
    min_percentage_sequence_numbers, 
    skip_frames, 
    debug=True):
    # similarity_search_results: Array of tuples
    # result_tuple = ('analyzed_video_frame','elapsed_time', 'other_vid_name', 'min_dist_frame')
    #         (3172, 952584.9666666667, 'scotiabank', 8),
    #         (3173, 952885.2666666667, 'scotiabank', 9),
    #         (3174, 953185.5666666667, 'scotiabank', 10),

    detections=[]

    # order of the algorithm o(len(similarity_search_results) * window_size)
    for i in range(len(similarity_search_results) - window_size):

        # Skip some frames
        if i % skip_frames != 0:
            pass

        else:
            # Analize by window. Save same sequences in dictionary
            sequences={}
            for search_result in similarity_search_results[i:i + window_size]:
                # search_result[0] -> analyzed_video_frame
                # search_result[1] -> elapsed_time
                # search_result[2] -> other_vid_name
                # search_result[3] -> min_dist_frame

                if (search_result[2] in sequences):
                    sequences[search_result[2]].append(
                        (float(search_result[1]), int(search_result[3])))
                else:
                    sequences[search_result[2]]=[
                        (float(search_result[1]), int(search_result[3]))]

            for other_vid_name in sequences.keys():
                # if i have a sequence detected, i calculate the time of those and then append it to the detections array
                if (len(sequences[other_vid_name]) > min_amount_sequence_numbers and sequence_detector(sequences[other_vid_name], min_percentage_sequence_numbers)):

                    if (debug):
                        cmd=input('Enter Command:')
                        if (cmd == 'm'):
                            import pprint
                            pp=pprint.PrettyPrinter(indent=4)
                            pp.pprint(sequences[other_vid_name])
                        elif (cmd == 'q'): exit()
                        elif (cmd == 'd'): debug=False
                    
                    init_time, end_time = extract_time_from_detected_sequence(sequences[other_vid_name])

                    if len(detections) == 0:
                        detections.append(detection(other_vid_name, init_time, end_time))
                    else: 
                        is_in_detections = False
                        for detection_instance in detections:
                            if (detection_instance.is_in_detection(init_time, end_time)):
                                detection_instance.extend_detection(init_time, end_time)
                                is_in_detections = True
                        if not is_in_detections:
                            detections.append(detection(other_vid_name, init_time, end_time))

    return [detection_instance.get_init_time_and_length() for detection_instance in detections]