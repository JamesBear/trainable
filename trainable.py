"""
This script standardizes the model training workflow and logs all the input files/output files/environment info.
"""
import sys
import hashlib
import os
import inspect

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

class TrainableBase:
    def __init__(self):
        print("TrainableBase: initializing..")

    def train(self):
        pass

    def log_all(self):
        pass

    def modify(self):
        pass

class MiniArgParser:
    def __init__(self):
        self.action = ''
        self.options = []
        self.unparsed = []
    
    def parse(self):
        #print('sys.argv:', sys.argv)
        num_args = len(sys.argv)
        if num_args == 1:
            return
        self.action = sys.argv[1]
        i = 2
        
        while i < num_args:
            cur = sys.argv[i]
            if len(cur) >= 2:
                if cur[0] == '-' and cur[1] != '-' and i + 1 < num_args:
                    option_name = cur[1:]
                    option_value = sys.argv[i+1]
                    self.options.append((option_name, option_value))
                    i += 2
                    continue
            elif cur.startswith('--'):
                equal_index = cur.find('=')
                if equal_index >= 0:
                    option_name = cur[2:equal_index]
                    option_value = cur[equal_index+1:]
                else:
                    option_name = cur[2:]
                    option_value = ''
                i += 1
                self.options.append((option_name, option_value))
                continue
            break
        self.unparsed = sys.argv[i:]

        print("Action: ", self.action, ", options: ", self.options, ", unparsed:", self.unparsed)

def GetTrainable():
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    sys.path.insert(0, currentdir)
    from my_trainable import MyTrainable
    trainable = MyTrainable()
    return trainable

if __name__ == '__main__':
    trainable = GetTrainable()
    parser = MiniArgParser()
    parser.parse()

    