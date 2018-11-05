
from trainable import TrainableBase

class MyTrainable(TrainableBase):
    def __init__(self, parser):
        super(MyTrainable, self).__init__(parser)
        print("MyTrainable: initializing..")

    def train(self):
        print("MyTrainable: `train` not implemented..")