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
            // This matches keys at the start of a line (possibly indented)
            {token: "keyword", regex: /^\s*([a-zA-Z_][a-zA-Z0-9_]*)(?=[=:])/, next: "after_key"},
            
            // Indented lines that aren't keys (continuation of multi-line values)
            // These should be highlighted as string values
            {token: "string", regex: /^\s+.+$/, next: "start"},
            
            // Empty lines
            {token: "text", regex: /^$/},
            
            // Everything else as text
            {defaultToken: "text"}
        ],
        
        "after_key": [
            // Separator (= or :) - use operator token for better visibility
            {token: "keyword.operator", regex: /[=:]/, next: "value"}
        ],
        
        "value": [
            // Skip whitespace at the start of value
            {token: "text", regex: /^\s+/, next: "value"},
            
            // End of line - go back to start
            // If the next line is indented, it will be caught by the indented line rule in start
            {token: "text", regex: /$/, next: "start"},
            
            // Everything else in the value is highlighted as string (salmon/orange)
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
