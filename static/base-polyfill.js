if (typeof(Function.prototype.bind) === "undefined") {
    Function.prototype.bind = function(oThis) {
        if (typeof this !== "function") {
            throw new TypeError("Function.prototype.bind - what is trying to be bound is not callable");
        }
        var aArgs = Array.prototype.slice.call(arguments, 1),
            fToBind = this,
            fNOP = function() {},
            fBound = function() {
                return fToBind.apply(
                    this instanceof fNOP && oThis ? this : oThis,
                    aArgs.concat(Array.prototype.slice.call(arguments))
                );
            };
        fNOP.prototype = this.prototype;
        fBound.prototype = new fNOP();
        return fBound;
    };
}

if(typeof(String.prototype.trim) === "undefined") {
    String.prototype.trim = function() {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}

if(typeof(Array.prototype.choice) === "undefined") {
    Array.prototype.choice = function() {
        if(this.length <= 0){
            return undefined;
        }
        var idx = Math.floor(Math.random() * this.length);
        return (this)[idx];
    };
}

if(typeof(ajax) === "undefined"){
    ajax = typeof($.ajax) === "function" ? $.ajax : function(args) { };
}
