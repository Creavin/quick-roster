from NspObjects.Penalties import Penalties

# improve by having function look up penalties
penalties = {Penalties.NO_PENALTY.value: "NO_PENALTY",
             Penalties.MINOR_PENALTY.value: "MINOR_PENALTY",
             Penalties.MAJOR_PENALTY.value: "MAJOR_PENALTY",
             Penalties.MAX_PENALTY.value: "MAX_PENALTY"}


class SkillData:
    def __init__(self, skill_id_to_name_map, skill_hierarchy):
        self.number_skills = len(skill_id_to_name_map)
        self.skill_id_to_name_map = skill_id_to_name_map
        self.skill_hierarchy = skill_hierarchy

    def to_dict(self):
        skill_hierarchy = {int(k): self.arrays_to_tuples(v) for k, v in self.skill_hierarchy.items()}
        return {
            "__skill_data__": True,
            'number_skills': self.number_skills,
            'skill_id_to_name_map': self.skill_id_to_name_map,
            'skill_hierarchy': skill_hierarchy
        }

    @classmethod
    def arrays_to_tuples(self, array_of_arrays):
        tuples = []
        for array in array_of_arrays:
            tuple = (int(array[0]), penalties[array[1]])
            tuples.append(tuple)
        return tuples
