"""
This script standardizes the model training workflow and logs all the input files/output files/environment info.
"""
import sys

class TrainableBase:
    def __init__(self):
        pass

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



if __name__ == '__main__':
    trainable = TrainableBase()
    parser = MiniArgParser()
    parser.parse()

    