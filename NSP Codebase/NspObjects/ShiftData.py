class ShiftData:

    def __init__(self, day_names, shift_names, track_names, shift_staffing_level_requirements):
        self.day_names = day_names
        self.shift_names = shift_names
        self.track_names = track_names
        # shift_staffing_level_requirements[day][track][shift][skill]
        self.shift_staffing_level_requirements = shift_staffing_level_requirements
        self.number_days = len(day_names)
        self.number_shifts = len(shift_names)
        self.number_tracks = len(track_names)


    def to_dict(self):
        staffing_level = self.shift_staffing_level_requirements
        if not isinstance(staffing_level, list):
            staffing_level = staffing_level.tolist()

        return {
            "__shift_data__": True,
            'day_names': self.day_names,
            'shift_names': self.shift_names,
            'track_names': self.track_names,
            'shift_staffing_level_requirements': staffing_level,
            'number_days': self.number_days,
            'number_shifts': self.number_shifts,
            'number_tracks': self.number_tracks
        }
