import os
# os.environ['PATH'] = "./bin" + ";" + os.environ['PATH']
import glob
from ruamel import yaml
import json
import numpy as np

SLIDE_DIR = '.'
SLIDE_CACHE_SIZE = 10
DEEPZOOM_FORMAT = 'jpeg'
DEEPZOOM_TILE_SIZE = 254
DEEPZOOM_OVERLAP = 1
DEEPZOOM_LIMIT_BOUNDS = True
DEEPZOOM_TILE_QUALITY = 75

class LabelTool():
    def __init__(self, config_file):
        assert config_file, 'no config file'
        self.config_file = config_file
        if os.path.isfile(config_file):
            with open(config_file, 'r', encoding='utf8') as f:
                config = yaml.load(f, Loader=yaml.RoundTripLoader)
                self.slide_dir = config['slide_dir']
                self.label_dir = config['label_dir']
                self.label_classes = config['class']
                self.class_num = len(self.label_classes)
                self.create_file_index()
        else:
            raise AssertionError(f'config file "{config_file}" not found')

    def create_file_index(self):
        self.slide_index = {}
        if not os.path.isdir(self.slide_dir):
            os.makedirs(self.slide_dir)
            print(f'create new slide dir {self.slide_dir}')

        if not os.path.isdir(self.label_dir):
            os.makedirs(self.label_dir)
            print(f'create new label save dir {self.label_dir}')

        slides = sorted(glob.glob(os.path.join(self.slide_dir, '*.mrxs')))
        for file in slides:
            name = os.path.splitext(os.path.split(file)[1])[0]
            slide_info = {}
            slide_info['name'] = name
            slide_info['slide_file'] = file
            label_file = os.path.join(self.label_dir, f'{name}.txt')
            slide_info['label_file'] = label_file
            slide_info['labeled'] = os.path.isfile(label_file)
            self.slide_index[name] = slide_info
        return

    def save_config(self):
        config = {}
        config['slide_dir'] = self.slide_dir
        config['label_dir'] = self.label_dir
        config['class'] = self.label_classes
        with open(self.config_file, 'w', encoding='utf8') as f:
             yaml.dump(config, f, Dumper=yaml.RoundTripDumper)

    # slide dir config and label save dir
    def get_dir_config(self):
        dir = {}
        dir['slide_dir'] = self.slide_dir
        dir['label_dir'] = self.label_dir
        return dir

    def set_dir_config(self, config):
        self.slide_dir = config['slide_dir']
        self.label_dir = config['label_dir']
        self.save_config()
        # recreate the file index
        self.create_file_index()

    def get_all_slide_info(self):
        return self.slide_index

    def get_slide_file(self, id):
        return self.slide_index[id]['slide_file']

    # label classes config
    def get_label_classes(self):
        return self.label_classes

    def set_label_classes(self, config):
        self.label_classes = config
        self.save_config()
    
    def get_label_boxes(self, id, left, top):
        file = self.slide_index[id]['label_file']
        if os.path.isfile(file):
            with open(file, 'r') as f:
                labelBoxes = yaml.load(f, Loader=yaml.RoundTripLoader)
                for box in labelBoxes['boxes']:
                    box['x'] =  round(box['x']) - int(left)
                    box['y'] = round(box['y']) - int(top)
            return json.dumps(labelBoxes)
        else:
            return '{}'

    def save_label_boxes(self, boxes, left, top):
        id = boxes['slide']
        file = self.slide_index[id]['label_file']
        for box in boxes['boxes']:
            box['x'] =  round(box['x']) + int(left)
            box['y'] = round(box['y']) + int(top)
            box['w'] = round(box['w'])
            box['h'] = round(box['h'])
        with open(file, 'w', encoding='utf8') as f:
             yaml.dump(boxes, f, Dumper=yaml.RoundTripDumper)
    
if __name__ == '__main__':
    tool = LabelTool('./config.yaml')
    print(tool.class_num)
    asdf = tool.get_slide_file('C20200175')


