from .optimization import OptimizationGrader

'''
=====================    Problem Statement    =======================
Given an integer $n$, compute $n^2$.
Input Format:
The input consists of a positive integer $n$.
Output format:
Output the integer $n^2$.
Subtasks:
1. $1 \le n \le 10$
2. $1 \le n \le 1000$
3. $1 \le n \le 10^6$
4. $1 \le n \le 10^9$
Scoring:
For each task, you will receive 1 point for a correct answer and 0 for an incorrect answer.
Sample Input:
4
Sample Output:
16
===========    Grader data (formatted as JSON object)   ==============
[Inputs for each task are 4, 17, 1003, and 1000000000]
Grader data for Task 1:
{
    "answer": 16,
}
Grader data for Task 2:
{
    "answer": 289,
}
Grader data for Task 3:
{
    "answer": 1006009,
}
Grader data for Task 4:
{
    "answer": 1000000000000000000
}
'''

class SquareIt(OptimizationGrader):
    # Returns the number of points that the submission should receive.
    # If the input is invalid, return None (this is temporary,
    # later it will return a more detailed error message).
    #
    # Some variables you can use:
    # self.num_tasks = number of tasks in problem
    # self.task_number = 1-indexed task number
    # self.task_data = custom task grader_data that you can set (JSON object, treat it as a Python dictionary)
    def grade_task(self, user_input):
        answer = self.task_data["answer"]
        weight = self.task_data["weight"]
        try:
            i = int(user_input)
            if i == answer:
                return 1
            else:
                return 0
        except ValueError:
            return None

    # Returns True if raw1 is strictly better than raw2
    # raw1 might be None (for invalid submissions), but raw2 is never None
    def better(self, raw1, raw2):
        if raw1 is None:
            return False
        return raw1 > raw2

    # raw_points might be None, but best_raw_points is never None
    def normalize(self, raw_points, best_raw_points):
        if raw_points is None or raw_points == 0:
            return 0
        return raw_points / best_raw_points