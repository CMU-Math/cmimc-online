class BaseGrader:
    def __init__(self, problem):
        self.problem = problem

    def grade(self, submission, score):
        '''
        Assigns a point value to the submission, and updates the
        corresponding score and competitor's total score
        Returns: None
        '''
        raise NotImplementedError()

    def validate(self, user_input):
        '''
        Checks whether the user's input is in an acceptable format
        Returns: bool
        '''
        raise NotImplementedError()