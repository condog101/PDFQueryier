import os


class Drive:
    def __init__(self, path=r'/Users/connordaly/papers'):
        self.path = path
        self.get_folders()

    def get_folders(self, subsets=['pdf']):
        self.files = []
        for filename in os.listdir(self.path):
            f = os.path.join(self.path, filename)
            # checking if it is a file
            if os.path.isfile(f):
                if any([x in filename for x in subsets]):
                    self.files.append(f)
