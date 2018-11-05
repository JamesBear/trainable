
from trainable import TrainableBase

class MyTrainable(TrainableBase):
    def __init__(self):
        super(MyTrainable, self).__init__()
        print("MyTrainable: initializing..")