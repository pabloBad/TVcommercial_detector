class detection:

    def __init__(self, detected_video_name, init_time, end_time):
        self.detected_video_name = detected_video_name
        self.init_time = init_time
        self.end_time = end_time

    def is_in_detection(self, init_time, end_time):
        # Alway gonna have
        if (self.init_time == init_time or self.end_time == end_time):
            return True
        return False

    def extend_detection(self, init_time, end_time):
        if self.is_in_detection(init_time, end_time):
            self.init_time = init_time
            self.end_time = end_time

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
