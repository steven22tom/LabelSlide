# LabelSlide
**LabelSlide is a slide annotation tool and label object bounding boxes in virtual slides (generally used in pathology)**

![example](./demo/ex.bmp)
## Feature
LabelSlide is based on B/S structure and written in Python.  
Using [OpenSlide](https://openslide.org/) to read the virtual slides and create DeepZoom Image.  
Then view the zoomable image in browser by [OpenSeadragon](https://openseadragon.github.io/).  
Adding [Fabric.js](http://fabricjs.com/) canvas to draw label box overlaying the OpenSeadragon viewer.  
The webpage build with [Bootstrap](https://getbootstrap.com/)

## Installation

### Build from source 

Python  

```
pip install -r requirements.txt
python label_slide.py
```
access 127.0.0.1:5000 (as default)

**If show error "Could not find module 'libopenslide-0.dll'". Please download [libvips](https://github.com/libvips/libvips/releases) and unzip to bin folder**

## Usage

### Config
There's two config file.

**app_config.py**  
Including **HOST**, **PORT** for the app and the **SLIDE_CONFIG** for slide config (the file path of config.yaml).  
*ps: parameter name must be uppercase*

**config.yaml**  
Containing the following parameters  
slide_dir: the directory where slides are kept.
label_dir: the directory where the annotation will be saved to.  
class: pre-defined classes including id, name and color.  

For example:
```
slide_dir: D:\Dataset\slides
label_dir: D:\Dataset\labels
class:
- id: 0
  name: A
  color: '#2196f3'
- id: 1
  name: B
  color: '#0014a8'
```
*ps: the class id must be integer and the color must be hex format.*  
*All content in config.yaml could be modified from webpage*

### Slide
**In theory**, the tool can read virtual slides in several formats because using OpenSlide:
* [Aperio (.svs, .tif)](https://openslide.org/formats/aperio/)
* [Hamamatsu (.vms, .vmu, .ndpi)](https://openslide.org/formats/hamamatsu/)
* [Leica (.scn)](https://openslide.org/formats/leica/)
* [MIRAX (.mrxs)](https://openslide.org/formats/mirax/)
* [Philips (.tiff)](https://openslide.org/formats/philips/)
* [Sakura (.svslide)](https://openslide.org/formats/sakura/)
* [Trestle (.tif)](https://openslide.org/formats/trestle/)
* [Ventana (.bif, .tif)](https://openslide.org/formats/ventana/)
* [Generic tiled TIFF (.tif)](https://openslide.org/formats/generic-tiff/)

**But only try MIRAX(.mrxs) under development.**  
**If you want to read slide in other formats, you should modify code in label_tool.py by yourself.**

### Annotation
**Only support rect box currently**

**Hotkeys**
Key|Function
--|--
q|View Mode
e|Create new rect box
Ctrl + s|Save
del|Delete the selected rect box

**Annotation file**  
One slide corresponds to one annotation file.  
Take annotation for MIRAX (.mrxs) as an example
```
slide: C20200174
boxes:
- class: 0
  x: 30749
  y: 70121
  w: 468
  h: 434
```
**x,y** is the top left pixel and **w,h** is the region size in the level 0 reference frame(highest resolution)
## Related

* [OpenSlide](https://openslide.org/) 
* [OpenSeadragon](https://openseadragon.github.io/)
* [OpenSeadragonScalebar](https://github.com/usnistgov/OpenSeadragonScalebar)
* [Fabric.js](http://fabricjs.com/)
* [Bootstrap](https://getbootstrap.com/)

## License
[LGPL-2.1 License](LICENSE)
