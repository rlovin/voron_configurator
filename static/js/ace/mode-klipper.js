ace.define("ace/mode/klipper_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

var KlipperHighlightRules = function() {
    this.$rules = {
        "start": [
            // Comments - ace_comment (green)
            {token: "comment", regex: /^[#;].*$/},
            
            // Section headers [name] - ace_tag (cyan)
            {token: "tag", regex: /^\[[^\]]+\]/},
            
            // Key names (before = or :) - ace_keyword (light blue)
            {token: "keyword", regex: /^\s*([a-zA-Z_][a-zA-Z0-9_]*)(?=[=:])/, next: "after_key"},
            
            // Everything else
            {defaultToken: "text"}
        ],
        
        "after_key": [
            // Separator
            {token: "text", regex: /[=:]/, next: "value"}
        ],
        
        "value": [
            // Skip whitespace
            {token: "text", regex: /\s+/, next: "value"},
            
            // End of line
            {token: "text", regex: /$/, next: "start"},
            
            // Everything in value is ace_string (salmon/orange)
            {defaultToken: "string", next: "value"}
        ]
    };
    
    this.normalizeRules();
};

oop.inherits(KlipperHighlightRules, TextHighlightRules);

exports.KlipperHighlightRules = KlipperHighlightRules;
});

ace.define("ace/mode/klipper",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/klipper_highlight_rules"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var KlipperHighlightRules = require("./klipper_highlight_rules").KlipperHighlightRules;

var Mode = function() {
    this.HighlightRules = KlipperHighlightRules;
};
oop.inherits(Mode, TextMode);

(function() {
    this.$id = "ace/mode/klipper";
}).call(Mode.prototype);

exports.Mode = Mode;
});
