class detection:

    def __init__(self, detected_video_name, init_time : int, end_time, init_frame, end_frame):
        self.detected_video_name = detected_video_name

        self.init_time = init_time
        self.end_time = end_time

        self.init_frame = init_frame
        self.end_frame = end_frame

    def is_in_detection(self, detected_video_name, init_time, end_time, init_frame, end_frame):

        return (self.detected_video_name == detected_video_name and 
                (self.init_time <= init_time and self.init_frame <= init_frame 
                or self.end_time >= end_time and self.end_frame >= end_frame))

                # and abs(self.init_time - init_time) < diff 
                # and abs(self.end_time - end_time) < diff)


    def extend_detection(self, detected_video_name, init_time, end_time, init_frame, end_frame):
        if (self.detected_video_name == detected_video_name):
            # print ("self: ", self.detected_video_name, self.init_time, end_time, self.init_frame, self.end_frame)
            # print ("new: ", detected_video_name, init_time, end_time, init_frame, end_frame)

            if (self.init_time >= init_time and self.init_frame >= init_frame):
                self.init_time = init_time
                self.init_frame = init_frame
                # print ("mod_init", init_time, init_frame)
            if (self.end_time <= end_time and self.end_frame <= end_frame):
                self.end_time = end_time
                self.end_frame = end_frame
                # print ("mod_end", end_time, end_frame)

                
            # print ('\n')
    def get_detection_timestamp(self):
        return self.detected_video_name, self.init_time, self.end_time

    def get_detection_seconds(self, round_time = True):
        if round_time:
            return self.detected_video_name, round(self.init_time / 1000, 1), round(self.end_time/1000, 1)
        return self.detected_video_name, self.init_time / 1000, self.end_time/1000

    def get_init_time_and_length(self, round_time = True):
        if round_time:
            return self.detected_video_name, round(self.init_time / 1000, 1), round((self.end_time - self.init_time)/1000, 1)
        return self.detected_video_name, self.init_time / 1000, (self.end_time - self.init_time)/1000
