"""
This script standardizes the model training workflow and logs all the input files/output files/environment info.
"""
import sys
import hashlib
import os
import inspect
import datetime
from collections import OrderedDict
import getpass
import socket
import json
import traceback
from subprocess import check_output
import uuid

__version__='0.1.1'

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def file_info(fname):
    return str(os.path.getsize(fname))+','+md5(fname)

class TrainableBase:
    def __init__(self, parser):
        print("TrainableBase: initializing..")
        self.start_time = datetime.datetime.now()
        self.parser = parser
        self.info = OrderedDict()
        self.app_name = self.get_app_name()
        self.info_sys()

    def get_app_name(self):
        return ''

    def train(self):
        if 'c' in self.parser.options:
            os.system(self.parser.options['c'])
        elif 'f' in self.parser.options:
            os.system(self.parser.options['f'])
        else:
            print("TrainableBase: don't know how to train under current options.")

    def info_sys(self):
        self.info['argv'] = self.parser.argv
        self.info['os.name'] = os.name
        self.info['user'] = getpass.getuser()
        self.info['hostname'] = socket.gethostname()
        self.info['trainable_version'] = __version__
        self.info['cwd.original'] = os.getcwd()
        self.info['start_time'] = self.start_time.strftime('%Y/%m/%d %H:%M:%S.%f')
        self.info['uuid'] = str(uuid.uuid4())
        if self.app_name != '':
            self.info['app_name'] = self.app_name

    def info_git(self):
        try:
            self.info['git_controlled'] = True
            git_hash = check_output('git rev-parse HEAD').decode('utf-8').strip()
            git_branch = check_output('git rev-parse --abbrev-ref HEAD').decode('utf-8').strip()
            self.info['git_hash'] = git_hash
            self.info['git_branch'] = git_branch
        except:
            self.info['git_controlled'] = False

    def info_end(self):
        end_time = datetime.datetime.now()
        self.info['end_time'] = end_time.strftime('%Y/%m/%d %H:%M:%S.%f')
        self.info['total_seconds'] = (end_time - self.start_time).total_seconds()

    def log_all(self):
        self.info_end()
        content = json.dumps(self.info, indent=4)
        self.log_file.write(content)

    def modify(self):
        print("TrainableBase: `modify` unimplemented..")

    def get_files_info(self, list_of_files):
        info_list = OrderedDict()
        for f in list_of_files:
            if os.path.exists(f):
                file_hash = file_info(f)
            else:
                file_hash = ''
            info_list[f] = file_hash

        return info_list

    def info_input_files(self):
        file_list = self.get_input_files()
        if file_list != None:
            self.info['input_files'] = self.get_files_info(file_list)

    def info_output_files(self):
        file_list = self.get_output_files()
        if file_list != None:
            self.info['output_files'] = self.get_files_info(file_list)


    def info_parameters(self):
        paras = self.get_parameters()
        if paras != None:
            self.info['parameters'] = paras

    def get_input_files(self):
        return None

    def get_output_files(self):
        return None

    def get_parameters(self):
        return None


    def run(self):
        if self.parser.action == 'train':
            self.create_log_file()
            self.info_git()
            try:
                self.train()
                self.info_parameters()
                self.info_input_files()
                self.info_output_files()
            except Exception as error:
                self.info['error'] = str(error)
                self.info['error_stack'] = traceback.format_exc()
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
        self.argv = sys.argv
        num_args = len(sys.argv)
        if num_args == 1:
            return
        self.action = sys.argv[1]
        i = 2
        self.target = ''
        if i < num_args and not sys.argv[i].startswith('-'):
            self.target = sys.argv[i]
            i += 1

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

        print("Action: ", self.action, ", target:", self.target, ", options: ", self.options, ", unparsed:", self.unparsed)

def GetTrainable(currentdir, parser):
    sys.path.insert(0, currentdir)
    if parser.target == '':
        modulename = 'my_trainable'
    else:
        modulename = 'my_trainable_' + parser.target

    new_module = __import__(modulename)
    trainable = new_module.MyTrainable(parser)
    return trainable

if __name__ == '__main__':
    parser = MiniArgParser()
    parser.parse()
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    trainable = GetTrainable(currentdir, parser)
    os.chdir(currentdir)
    trainable.run()
