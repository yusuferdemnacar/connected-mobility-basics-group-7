import random
from lecture_slot import LectureSlot

class Course:
    def __init__(self, id: int, lecture_slot: LectureSlot) -> None:
        self.id = id
        self.lecture_slot = lecture_slot
    
    @staticmethod
    def generate_random_course(id: int, available_lecture_slots: list) -> 'Course':
        if not available_lecture_slots:
            raise ValueError("No available lecture slots to assign to the course.")
        lecture_slot_slot = random.choice(available_lecture_slots)
        return Course(id, lecture_slot_slot)

if __name__ == "__main__":
    pass