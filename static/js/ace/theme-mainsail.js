define("ace/theme/mainsail-css",["require","exports","module"],function(e,t,n){n.exports='
/* Mainsail Theme - Matching reference screenshot exactly */

.ace-mainsail .ace_gutter {
  background: #1e1e1e;
  color: #858585
}

.ace-mainsail .ace_print-margin {
  width: 1px;
  background: #333333
}

.ace-mainsail {
  background-color: #1e1e1e;
  color: #d4d4d4
}

.ace-mainsail .ace_cursor {
  color: #d4d4d4
}

.ace-mainsail .ace_marker-layer .ace_selection {
  background: #264f78
}

.ace-mainsail.ace_multiselect .ace_selection.ace_start {
  box-shadow: 0 0 3px 0px #1e1e1e;
  border-radius: 2px
}

.ace-mainsail .ace_marker-layer .ace_step {
  background: rgba(76, 201, 176, 0.2)
}

.ace-mainsail .ace_marker-layer .ace_bracket {
  margin: -1px 0 0 -1px;
  border: 1px solid #404040
}

.ace-mainsail .ace_marker-layer .ace_active-line {
  background: #2a2d2e
}

.ace-mainsail .ace_gutter-active-line {
  background-color: #2a2d2e
}

.ace-mainsail .ace_invisible {
  color: #808080
}

/* Sections [mcu] - Bright Cyan #4EC9B0 */
.ace-mainsail .ace_tag {
  color: #4ec9b0;
  font-weight: normal
}

/* Comments # - Green #6A9955 */
.ace-mainsail .ace_comment {
  color: #6a9955;
  font-style: normal
}

/* Keys (serial:, kinematics:) - Light Blue #9CDCFE */
.ace-mainsail .ace_keyword {
  color: #9cdcfe
}

/* Values (/dev/serial..., corexy, command) - Salmon #CE9178 */
.ace-mainsail .ace_string {
  color: #ce9178
}

/* Numbers (300, 7500, 5.0) - Light Purple #B5CEA8 */
.ace-mainsail .ace_constant.ace_numeric {
  color: #b5cea8
}

/* Default text */
.ace-mainsail .ace_text {
  color: #d4d4d4
}

/* Selection */
.ace-mainsail .ace_marker-layer .ace_selected-word {
  background: rgba(38, 79, 120, 0.5);
  border: 1px solid rgba(38, 79, 120, 0.8)
}
';

});

define("ace/theme/mainsail",["require","exports","module","ace/lib/dom","ace/theme/mainsail-css"],function(e,t,n){"use strict";
var r=e("../lib/dom");
t.isDark=!0;
t.cssClass="ace-mainsail";
t.cssText=e("./mainsail-css").cssText;
t.$selectionColorConflict=!1;
var i=r.importCssString(t.cssText,t.cssClass);

var s=e("../lib/dom");
});
                (function() {
                    window.require(["ace/theme/mainsail"], function(m) {
                        if (typeof module == "object" && typeof exports == "object" && module) {
                            module.exports = m;
                        }
                    });
                })();
