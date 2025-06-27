import numpy as np
import time

class Elevator:
    def __init__(self, tbetween, tfloor, total_floors=7):
        self.total_floors = total_floors
        self.tbetween = tbetween
        self.tfloor = tfloor
        self.last_open = 0
        self.is_moving = False

class InputData:
    def __init__(self, tbetween, tfloor, total_floors, twalk_between, previous_student=None, group_students=10, student_requests=None):
        self.elevator = Elevator(tbetween, tfloor, total_floors)
        self.group_students = group_students

        if previous_student is None:
            self.previous_student = [np.array([])]
        else:
            self.previous_student = previous_student

        self.twalk_between = twalk_between
        self.student_requests = student_requests
        if student_requests is not None:
            self.new_student_requests(student_requests)

    def new_student_requests(self, student_requests):
        student_requests = int(student_requests)
        self.student_requests = student_requests

        if self.previous_student is None or len(self.previous_student) == 0:
            self.previous_student = [np.array([student_requests])]
        elif isinstance(self.previous_student[-1], np.ndarray) and len(self.previous_student[-1]) < self.group_students:
            self.previous_student[-1] = np.append(self.previous_student[-1], student_requests)
        else:
            self.previous_student.append(np.array([student_requests]))

    def get_previous_student(self):
        groups_copy = list(self.previous_student)
        for i, group in enumerate(groups_copy):
            num_missing = self.group_students - len(group)
            if num_missing > 0:
                padding = np.zeros(num_missing)
                groups_copy[i] = np.append(group, padding)
        return groups_copy

    def pop_previous_student(self):
        if self.previous_student:
            self.previous_student.pop(0)

    def back_previous_student(self):
        if not self.previous_student:
            return
        last_group = self.previous_student[-1]
        num_zeros = np.sum(last_group == 0)

        if len(last_group) == 1 or num_zeros == self.group_students - 1:
            self.previous_student.pop()
        else:
            nonzero_indices = np.where(last_group != 0)[0]
            if len(nonzero_indices) > 0:
                self.previous_student[-1][nonzero_indices[-1]] = 0

class TotalWaitElevator:
    def __init__(self, t_floor, t_between, walk_between):
        self.t_floor = t_floor
        self.t_between = t_between
        self.walk_between = walk_between

    def t_use_elevator(self, array_floor):
        count_distinct = np.array([len(np.unique(row[row != 0])) for row in array_floor])
        top = np.max(array_floor, axis=1)
        t_use = np.sum(self.t_floor * count_distinct + 2 * self.t_between * top)
        return t_use

    def t_wait_elevator(self, array_floor, time_last_elevator):
        t_use = self.t_use_elevator(array_floor)
        return max(time_last_elevator + t_use - time.time(), 0)

    def t_use_elevator_self(self, floor_self, array_floor):
        end_floor = array_floor[-1]
        count_floor_before = len(np.unique(end_floor[(end_floor < floor_self) & (end_floor != 0)]))
        t_use = self.t_between * floor_self + count_floor_before * self.t_between
        return t_use

    def t_use_stair(self, floor_self):
        return self.walk_between * floor_self

    def fit(self, array_floor, time_last_elevator, floor_self):
        self.use_elevator = self.t_wait_elevator(array_floor, time_last_elevator) + \
                            self.t_use_elevator_self(floor_self, array_floor)
        self.use_stair = self.t_use_stair(floor_self)
        self.recommend = 1 if self.use_elevator < self.use_stair else 0