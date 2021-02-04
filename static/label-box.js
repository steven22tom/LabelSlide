function labelBox(config) {
    this.id = guid();
    this.classID = null;
    this.shape = this.init(config);
}
labelBox.prototype = {
    init: function(config) {
        this.classID = config.tab;
        config.tab = this.id;
        return new fabric.Rect(config); 
    },
    set: function(key, value) {
        this.shape.set(key, value);
    }
}
