class TimePeriod:
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

        split_start_time = start_time.split(":")
        self.start_time_hour = int(split_start_time[0])
        self.start_time_minute = int(split_start_time[1])

        split_end_time = end_time.split(":")
        self.end_time_hour = int(split_end_time[0])
        self.end_time_minute = int(split_end_time[1])

        self.start_time_in_minutes = self.start_time_hour * 60 + self.start_time_minute

        self.period_duration_minutes = (self.end_time_hour - self.start_time_hour) * 60 + \
                              (self.end_time_minute - self.start_time_minute)

        self.periods_since_midnight = int(self.start_time_in_minutes / self.period_duration_minutes)

