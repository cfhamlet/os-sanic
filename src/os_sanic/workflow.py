from abc import ABCMeta


class Workflowable(metaclass=ABCMeta):
    def setup(self):
        pass

    def cleanup(self):
        pass
