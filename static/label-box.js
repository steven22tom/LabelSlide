function LabelBoxRectangle(config) {
    this.id = guid();
    this.classID = null;
    this.shape = this.init(config);
    this.type = 'rect';
}
LabelBoxRectangle.prototype = {
    init: function(config) {
        this.classID = config.tab;
        config.tab = this.id;
        return new fabric.Rect(config); 
    },
    set: function(key, value) {
        this.shape.set(key, value);
    }
}

function LabelBoxPolygon(config) {
    this.id = guid();
    this.classID = null;
    this.shape = this.init(config);
    this.type = 'poly';
}
LabelBoxPolygon.prototype = {
    init: function(config) {
        this.classID = config.tab;
        config.tab = this.id;
        return new fabric.Polygon(config.points, config); 
    },
    set: function(key, value) {
        this.shape.set(key, value);
    }
}
