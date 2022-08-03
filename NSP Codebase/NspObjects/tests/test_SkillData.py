from unittest import TestCase
from NspObjects.SkillData import SkillData


class TestSkillData(TestCase):
    def setUp(self):
        self.skill_data = SkillData(
            skill_id_to_name_map={0: "default"},
            skill_hierarchy={0: []}
        )
        pass


class TestEachFunction(TestSkillData):
    def test_to_dict(self):
        skill_dict = self.skill_data.to_dict()
        print(skill_dict)
        assert str(skill_dict) == "{'__skill_data__': True, 'number_skills': 1, 'skill_id_to_name_map': {0: " \
                                  "'default'}, 'skill_hierarchy': {0: []}} "
        pass
