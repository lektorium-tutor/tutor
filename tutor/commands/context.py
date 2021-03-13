# pylint: disable=too-few-public-methods
class Context:
    def __init__(self, root):
        self.root = root

    @staticmethod
    def docker_compose(root, config, *command):
        raise NotImplementedError
