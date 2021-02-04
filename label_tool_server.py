import os
os.environ['PATH'] = r".\bin" + ";" + os.environ['PATH']

from flask import Flask, abort, make_response, render_template, url_for, request, send_from_directory
from io import BytesIO

import openslide
from openslide import ImageSlide, open_slide
from openslide.deepzoom import DeepZoomGenerator
from optparse import OptionParser
import re
from unicodedata import normalize
from label_tool import LabelTool
import json

DEEPZOOM_SLIDE = None
DEEPZOOM_FORMAT = 'jpeg'
DEEPZOOM_TILE_SIZE = 254
DEEPZOOM_OVERLAP = 1
DEEPZOOM_LIMIT_BOUNDS = True
DEEPZOOM_TILE_QUALITY = 75
SLIDE_NAME = 'slide'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('DEEPZOOM_TILER_SETTINGS', silent=True)


class PILBytesIO(BytesIO):
    def fileno(self):
        '''Classic PIL doesn't understand io.UnsupportedOperation.'''
        raise AttributeError('Not supported')

def load_slide(file):
    slidefile = file
    if slidefile is None:
        raise ValueError('No slide file specified')
    config_map = {
        'DEEPZOOM_TILE_SIZE': 'tile_size',
        'DEEPZOOM_OVERLAP': 'overlap',
        'DEEPZOOM_LIMIT_BOUNDS': 'limit_bounds',
    }
    opts = dict((v, app.config[k]) for k, v in config_map.items())
    slide = open_slide(slidefile)
    left = slide.properties["mirax.NONHIERLAYER_3_LEVEL_0_SECTION.COMPRESSED_STITCHING_ORIG_SLIDE_SCANNED_AREA_IN_PIXELS__LEFT"]
    top = slide.properties["mirax.NONHIERLAYER_3_LEVEL_0_SECTION.COMPRESSED_STITCHING_ORIG_SLIDE_SCANNED_AREA_IN_PIXELS__TOP"]
    
    app.slides = {
        SLIDE_NAME: DeepZoomGenerator(slide, **opts),
        'left': left,
        'top': top
    }
    try:
        mpp_x = slide.properties[openslide.PROPERTY_NAME_MPP_X]
        mpp_y = slide.properties[openslide.PROPERTY_NAME_MPP_Y]
        app.slide_mpp = (float(mpp_x) + float(mpp_y)) / 2
        return app.slide_mpp
    except (KeyError, ValueError):
        app.slide_mpp = 0
        return 0

@app.route('/')
def index():
    label_info = label_tool.get_all_slide_info()
    label_classes = label_tool.get_label_classes()
    return render_template('label-tool.html', label_info=label_info,
            label_classes=label_classes)

@app.route('/get_slide_info/<id>')
def getSlideInfo(id):
    file = label_tool.get_slide_file(id)
    mpp = load_slide(file)
    info = {}
    info['slide'] = url_for('dzi', slug=SLIDE_NAME)
    info['mpp'] = str(mpp)
    return info

@app.route('/old')
def oldHtml():
    slide_url =  url_for('dzi', slug=SLIDE_NAME)
    associated_urls = dict((name, url_for('dzi', slug=slugify(name)))
            for name in app.associated_images)
    return render_template('test.html', slide_url=slide_url,
            associated=associated_urls, properties=app.slide_properties,
            slide_mpp=app.slide_mpp)

@app.route('/get_dir_config', methods=['get'])
def getDirConfig():
    return label_tool.get_dir_config()

@app.route('/set_dir_config', methods=['post'])
def setDirConfig():
    label_tool.set_dir_config(request.form)
    return "Saved successfully"

@app.route('/get_label_classes', methods=['get'])
def getLabelClasses():
    return json.dumps(label_tool.get_label_classes())

@app.route('/set_label_classes', methods=['post'])
def setLabelClasses():
    data = request.get_data()
    label_tool.set_label_classes(json.loads(data.decode("utf-8")))
    return "Saved successfully"

@app.route('/get_label_boxes/<id>', methods=['get'])
def getLabelBoxes(id):
    return label_tool.get_label_boxes(id, app.slides['left'], app.slides['top'])

@app.route('/save_label_boxes', methods=['post'])
def saveLabelBoxes():
    data = request.get_data()
    label_tool.save_label_boxes(json.loads(data.decode("utf-8")), app.slides['left'], app.slides['top'])
    return "Saved successfully"

@app.route('/<slug>.dzi')
def dzi(slug):
    format = app.config['DEEPZOOM_FORMAT']
    try:
        resp = make_response(app.slides[slug].get_dzi(format))
        resp.mimetype = 'application/xml'
        return resp
    except KeyError:
        # Unknown slug
        abort(404)

@app.route('/<slug>_files/<int:level>/<int:col>_<int:row>.<format>')
def tile(slug, level, col, row, format):
    format = format.lower()
    if format != 'jpeg' and format != 'png':
        # Not supported by Deep Zoom
        abort(404)
    try:
        tile = app.slides[slug].get_tile(level, (col, row))
    except KeyError:
        # Unknown slug
        abort(404)
    except ValueError:
        # Invalid level or coordinates
        abort(404)
    buf = PILBytesIO()
    tile.save(buf, format, quality=app.config['DEEPZOOM_TILE_QUALITY'])
    resp = make_response(buf.getvalue())
    resp.mimetype = 'image/%s' % format
    return resp

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def slugify(text):
    text = normalize('NFKD', text.lower()).encode('ascii', 'ignore').decode()
    return re.sub('[^a-z0-9]+', '-', text)

if __name__ == '__main__':
    # Load config file
    app.config.from_pyfile('./app_config.py')
    # Load slide config file
    try:
        slide_config = app.config['SLIDE_CONFIG']
        label_tool = LabelTool(slide_config)
    except IndexError:
        if app.config['SLIDE_CONFIG'] is None:
            parser.error('No slide config file specified')

    app.run(host=app.config['HOST'], port=app.config['PORT'], threaded=True)
