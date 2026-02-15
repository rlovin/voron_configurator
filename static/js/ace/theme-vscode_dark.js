define("ace/theme/vscode_dark-css",["require","exports","module"],function(e,t,n){n.exports='
/* VSCode Dark+ Theme for Ace Editor */

.ace-vscode-dark .ace_gutter {
  background: #1e1e1e;
  color: #858585
}

.ace-vscode-dark .ace_print-margin {
  width: 1px;
  background: #333333
}

.ace-vscode-dark {
  background-color: #1e1e1e;
  color: #d4d4d4
}

.ace-vscode-dark .ace_cursor {
  color: #aeafad
}

.ace-vscode-dark .ace_marker-layer .ace_selection {
  background: #264f78
}

.ace-vscode-dark.ace_multiselect .ace_selection.ace_start {
  box-shadow: 0 0 3px 0px #1e1e1e;
  border-radius: 2px
}

.ace-vscode-dark .ace_marker-layer .ace_step {
  background: rgb(198, 219, 174)
}

.ace-vscode-dark .ace_marker-layer .ace_bracket {
  margin: -1px 0 0 -1px;
  border: 1px solid #d4d4d4
}

.ace-vscode-dark .ace_marker-layer .ace_active-line {
  background: #2a2d2e
}

.ace-vscode-dark .ace_gutter-active-line {
  background-color: #2a2d2e
}

.ace-vscode-dark .ace_invisible {
  color: #d4d4d4
}

.ace-vscode-dark .ace_keyword,
.ace-vscode-dark .ace_meta,
.ace-vscode-dark .ace_storage,
.ace-vscode-dark .ace_storage.ace_type,
.ace-vscode-dark .ace_support.ace_type {
  color: #569cd6
}

.ace-vscode-dark .ace_keyword.ace_operator {
  color: #d4d4d4
}

.ace-vscode-dark .ace_constant.ace_character,
.ace-vscode-dark .ace_constant.ace_language,
.ace-vscode-dark .ace_constant.ace_numeric,
.ace-vscode-dark .ace_keyword.ace_other.ace_unit,
.ace-vscode-dark .ace_support.ace_constant,
.ace-vscode-dark .ace_variable.ace_parameter {
  color: #b5cea8
}

.ace-vscode-dark .ace_constant.ace_other {
  color: #d4d4d4
}

.ace-vscode-dark .ace_invalid {
  color: #f44747;
  background-color: #1e1e1e
}

.ace-vscode-dark .ace_invalid.ace_deprecated {
  color: #f44747;
  background-color: #1e1e1e
}

.ace-vscode-dark .ace_fold {
    background-color: #c586c0;
    border-color: #d4d4d4
}

.ace-vscode-dark .ace_entity.ace_name.ace_function,
.ace-vscode-dark .ace_support.ace_function,
.ace-vscode-dark .ace_support.ace_function.ace_misc.css,
.ace-vscode-dark .ace_meta.ace_tag {
  color: #dcdcaa
}

.ace-vscode-dark .ace_support.ace_class,
.ace-vscode-dark .ace_support.ace_type {
  color: #4ec9b0
}

.ace-vscode-dark .ace_markup.ace_underline {
    text-decoration: underline
}

.ace-vscode-dark .ace_string {
  color: #ce9178
}

.ace-vscode-dark .ace_comment {
  font-style: italic;
  color: #6a9955
}

.ace-vscode-dark .ace_entity.ace_name.ace_tag,
.ace-vscode-dark .ace_entity.ace_other.ace_attribute-name,
.ace-vscode-dark .ace_meta.ace_tag,
.ace-vscode-dark .ace_string.ace_regexp,
.ace-vscode-dark .ace_variable {
  color: #569cd6
}

.ace-vscode-dark .ace_variable.ace_language {
  color: #569cd6
}

/* Custom token classes for Klipper mode */
.ace-vscode-dark .ace_section {
  color: #569cd6;
  font-weight: bold
}

.ace-vscode-dark .ace_parameter {
  color: #9cdcfe
}

.ace-vscode-dark .ace_boolean {
  color: #569cd6
}

.ace-vscode-dark .ace_operator {
  color: #d4d4d4
}
';

});

define("ace/theme/vscode_dark",["require","exports","module","ace/lib/dom","ace/theme/vscode_dark-css"],function(e,t,n){"use strict";
var r=e("../lib/dom");
t.isDark=!0;
t.cssClass="ace-vscode-dark";
t.cssText=e("./vscode_dark-css").cssText;
t.$selectionColorConflict=!1;
var i=r.importCssString(t.cssText,t.cssClass);

var s=e("../lib/dom");
});
                (function() {
                    window.require(["ace/theme/vscode_dark"], function(m) {
                        if (typeof module == "object" && typeof exports == "object" && module) {
                            module.exports = m;
                        }
                    });
                })();
