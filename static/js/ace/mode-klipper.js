ace.define("ace/mode/klipper_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

var KlipperHighlightRules = function() {
    this.$rules = {
        "start": [
            // Section headers [section_name]
            {
                token: "keyword.section",
                regex: /^\[[^\]]+\]/,
                next: "start"
            },
            // Comments starting with #
            {
                token: "comment",
                regex: /^#.*/,
                next: "start"
            },
            // Parameter lines: parameter_name: value
            // Capture the whole line and tokenize parts
            {
                regex: /^(\w+)(:)(\s*)(.*)$/,
                token: ["variable.parameter", "punctuation.separator", "text", "string.value"],
                next: "start"
            },
            // Standalone boolean values
            {
                token: "constant.language.boolean",
                regex: /\b(?:true|false)\b/,
                next: "start"
            },
            // Standalone numbers (with word boundaries to avoid matching within alphanumeric values)
            {
                token: "constant.numeric",
                regex: /\b-?\d+\.?\d*\b/,
                next: "start"
            },
            // Operators ^ and !
            {
                token: "keyword.operator",
                regex: /[\^!]/,
                next: "start"
            },
            // Default fallback
            {
                defaultToken: "text"
            }
        ]
    };
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
