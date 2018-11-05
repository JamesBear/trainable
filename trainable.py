"""
This script standardizes the model training workflow and logs all the input files/output files/environment info.
"""
import sys
import hashlib
import os
import inspect
import datetime

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

class TrainableBase:
    def __init__(self, parser):
        print("TrainableBase: initializing..")
        self.parser = parser

    def train(self):
        print("TrainableBase: `train` unimplemented..")

    def log_all(self):
        print("TrainableBase: `log_all` unimplemented..")

    def modify(self):
        print("TrainableBase: `modify` unimplemented..")

    def run(self):
        if self.parser.action == 'train':
            self.create_log_file()
            self.train()
            self.log_all()
            self.log_file.close()
        else:
            print('Unimplemented action:', self.parser.action)

    def get_log_dir(self):
        return "trainable_logs"

    def get_log_file_name(self):
        now = datetime.datetime.now()
        time_str = now.strftime('%Y%m%d_%H%M%S.%f.txt')
        time_str = self.parser.action + time_str
        return time_str

    def create_log_file(self):
        log_dir = self.get_log_dir()
        if not os.path.isdir(log_dir):
            os.mkdir(log_dir)
        log_file_name = self.get_log_file_name()
        log_file_path = os.path.join(log_dir, log_file_name)
        self.log_file = open(log_file_path, 'w')
        print("log file created:", log_file_path)


class MiniArgParser:
    def __init__(self):
        self.action = ''
        self.options = {}
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
                    self.options[option_name] = option_value
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
                self.options[option_name] = option_value
                continue
            break
        self.unparsed = sys.argv[i:]

        print("Action: ", self.action, ", options: ", self.options, ", unparsed:", self.unparsed)

def GetTrainable(currentdir, parser):
    sys.path.insert(0, currentdir)
    from my_trainable import MyTrainable
    trainable = MyTrainable(parser)
    return trainable

if __name__ == '__main__':
    parser = MiniArgParser()
    parser.parse()
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    trainable = GetTrainable(currentdir, parser)
    os.chdir(currentdir)
    trainable.run()

    