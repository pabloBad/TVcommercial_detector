import numpy as np

def calculate_outputs(sequences: dict) -> list:

    outputs = []
    for other_vid_name in sequences.keys():
        for sequences_array in sequences[other_vid_name]:
            # Default max, min tuples
            min_tuple = sequences_array[0]
            max_tuple = (0, 0, None, None)

            # Find the max time using the number of the frame, other_vid_tuple[0]
            for other_vid_tuple in sequences_array:
                if (int(other_vid_tuple[0]) >= int(max_tuple[0])):
                    max_tuple = other_vid_tuple

            # Format the output
            outputs.append([
                round(min_tuple[1]/1000, 1),
                round((max_tuple[1] - min_tuple[1]) / 1000, 3),
                other_vid_name])

    # Returns others_video detections ordered by their start time.
    return sorted(outputs, key=lambda output_tuple: output_tuple[0])


def group_by_other_vid_name(similarity_search_results: list) -> dict:
    other_vid_dict = {}
    for elem in similarity_search_results:
        if (elem[2] in other_vid_dict.keys()):
            other_vid_dict[elem[2]].append(
                [int(elem[0]), float(elem[1]), int(elem[3])])
        else:
            other_vid_dict[elem[2]] = [
                [int(elem[0]), float(elem[1]), int(elem[3])]]

    return other_vid_dict

def extract_sequences_dict(other_vid_dict: dict, max_difference_between_frames: int, min_sequence_lenght: int, max_percentage_repeated_elements: float) -> dict:

    separated_sequences_dict = {}

    # For each other_video perform a extract_sequences_array:
    for other_vid_name in other_vid_dict.keys():
        separated_sequences_dict[other_vid_name] = extract_sequences_arrays(
            other_vid_dict[other_vid_name], max_difference_between_frames, min_sequence_lenght, max_percentage_repeated_elements)

    return separated_sequences_dict


def extract_sequences_arrays(
    other_vid_array: list, 
    max_difference_between_frames: int, 
    min_sequence_lenght: int,
    max_percentage_repeated_elements: float) -> list:

    # Step 1
    # Cut all the sequences array into sequences subarrays in which elment have short distance 
    # of original video frame. (delta other_vid_array < max_difference_between_frames)
    sequences = []
    new_sequence = []
    i = 0
    while (i < len(other_vid_array) - 1):
        if (other_vid_array[i + 1][0] - other_vid_array[i][0] < max_difference_between_frames):
            new_sequence.append(other_vid_array[i])
        else:
            sequences.append(new_sequence)
            new_sequence = []
        i += 1

    # Step 2: Clean empty subarrays
    no_empty_array_sequences = list(filter(lambda sequence: len(sequence) > min_sequence_lenght, sequences))

    # Step 3: Clean subarrays with a lot of same elements. 
    # Compare distincts elements in the array and calculate a max percentage of repeated elements.
    cleaned_sequences = []
   
    for sequences_subarray in no_empty_array_sequences:
        range_of_frames = list(range(len(sequences_subarray)))

        for other_vid_tuple in sequences_subarray:
            if other_vid_tuple[2] in range_of_frames:
                range_of_frames.remove(other_vid_tuple[2])

        # If the subbarray has less percentage value that the max permited, add to cleaned_sequences
        if (len(range_of_frames) / len(sequences_subarray) < max_percentage_repeated_elements):
            cleaned_sequences.append(sequences_subarray)

    return cleaned_sequences

def occurrence_detector(
        similarity_search_results: list,
        min_sequence_lenght: int,
        max_difference_between_frames: int,
        max_percentage_repeated_elements: float,
        debug=True) -> list:

    # Input:    
    # similarity_search_results: Array of tuples
    # result_tuple = ('analyzed_video_frame','elapsed_time', 'other_vid_name', 'min_dist_frame')
    #                (3172, 952584.9666666667, 'scotiabank', 8),


    # Group by other_vid_name the similarity search results:
    other_vid_dict = group_by_other_vid_name(similarity_search_results)

    # Extract the subsequences:
    all_sequences = extract_sequences_dict(other_vid_dict, max_difference_between_frames, min_sequence_lenght, max_percentage_repeated_elements)

    # Calculate the outputs
    outputs = calculate_outputs(all_sequences)

    # Debug
    if (debug):
        cmd = input('Enter Command:')
        if (cmd == 'm'):
            import pprint
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(outputs)

        if (cmd == 'l'):
            import pprint
            pp = pprint.PrettyPrinter(indent=4)
            f = open('log.txt', 'w')
            pprint.pprint(outputs, f)
        elif (cmd == 'q'):
            exit()
        elif (cmd == 'd'):
            debug = False

    return outputs
