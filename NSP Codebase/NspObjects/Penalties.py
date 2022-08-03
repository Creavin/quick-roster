from enum import Enum


class Penalties(Enum):
    NO_PENALTY = 0
    MINOR_PENALTY = 1
    MAJOR_PENALTY = 3
    MAX_PENALTY = 10

    @staticmethod
    def calculate_skill_penalty(worker_skills, required_skill, skill_hierarchy):
        if required_skill in worker_skills:
            return 0

        skill_substitutes = skill_hierarchy.get(required_skill)
        if skill_substitutes:
            for skill_penalty_pair in skill_substitutes:
                if skill_penalty_pair[0] in worker_skills:
                    return skill_penalty_pair[1]

        return Penalties.MAX_PENALTY.value
