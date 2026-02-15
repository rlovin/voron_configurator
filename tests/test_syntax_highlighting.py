"""Test syntax highlighting colors match Mainsail/VSCode"""

import pytest
from playwright.sync_api import Page, expect
import re
import subprocess
import time


class TestSyntaxHighlighting:
    """Test that syntax highlighting uses correct VSCode/Mainsail colors."""
    
    # Expected VSCode colors
    VSCODE_BLUE = 'rgb(86, 156, 214)'      # #569CD6 - Sections, keys
    VSCODE_GREEN = 'rgb(106, 153, 85)'      # #6A9955 - Comments
    VSCODE_ORANGE = 'rgb(206, 145, 120)'    # #CE9178 - Strings
    VSCODE_MAGENTA = 'rgb(197, 134, 192)'   # #C586C0 - Keywords/booleans
    VSCODE_YELLOW = 'rgb(220, 220, 170)'    # #DCDCAA - Pins, G-code
    VSCODE_CYAN = 'rgb(156, 220, 254)'      # #9CDCFE - Variables
    VSCODE_TEAL = 'rgb(78, 201, 176)'      # #4EC9B0 - References {var}
    VSCODE_WHITE = 'rgb(197, 200, 198)'     # #C5C8C6 - Default text
    

    
    def get_element_color(self, page, selector):
        """Get the computed color of an element."""
        return page.evaluate(f"""
            window.getComputedStyle(document.querySelector('{selector}')).color
        """)
    
    def test_comments_are_green(self, page: Page, base_url):
        """Test that comments use VSCode green color."""
        page.goto(base_url)
        
        # Wait for Ace to initialize
        page.wait_for_timeout(1000)
        
        # Set editor content with a comment
        page.evaluate("""
            ace.edit('monaco-editor').setValue('; This is a comment', -1);
        """)
        
        page.wait_for_timeout(500)
        
        # Take screenshot for visual inspection
        page.screenshot(path='test-results/comment_highlighting.png')
        
        # Check comment color
        comment = page.locator('.ace_comment')
        if comment.count() > 0:
            style = page.evaluate("""
                document.querySelector('.ace_comment')?.style?.color || 
                window.getComputedStyle(document.querySelector('.ace_comment')).color
            """)
            print(f"Comment color: {style}")
    
    def test_sections_are_blue(self, page: Page, base_url):
        """Test that section headers use VSCode blue color."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Set content with a section
        page.evaluate("""
            ace.edit('monaco-editor').setValue('[mcu]', -1);
        """)
        
        page.wait_for_timeout(500)
        page.screenshot(path='test-results/section_highlighting.png')
        
        # Check section bracket color
        variable = page.locator('.ace_variable')
        if variable.count() > 0:
            style = page.evaluate("""
                window.getComputedStyle(document.querySelector('.ace_variable')).color
            """)
            print(f"Section/Bracket color: {style}")
    
    def test_keys_are_light_blue(self, page: Page, base_url):
        """Test that config keys use light blue color."""
        page.goto(base_url)
        page.wait_for_timeout(1500)  # Wait for Ace to fully load
        
        # Check if klipper mode is available
        mode_check = page.evaluate("""
            ace.require('ace/mode/klipper') !== undefined
        """)
        print(f"\\nKlipper mode loaded: {mode_check}")
        
        # Set content with a key - after a section header
        test_content = """[stepper_x]
step_pin: PB10"""
        
        page.evaluate(f"""
            ace.edit('monaco-editor').setValue(`{test_content}`, -1);
        """)
        
        page.wait_for_timeout(500)
        page.screenshot(path='test-results/key_highlighting.png')
        
        # Get all tokens for debugging
        tokens = page.evaluate("""
            const editor = ace.edit('monaco-editor');
            const session = editor.getSession();
            const tokens = [];
            for (let i = 0; i < session.getLength(); i++) {
                const lineTokens = session.getTokens(i);
                lineTokens.forEach(token => {
                    tokens.push({line: i, type: token.type, value: token.value});
                });
            }
            tokens;
        """)
        
        print("\\n=== Line Tokens ===")
        for token in tokens:
            print(f"  Line {token['line']}: ({token['type']}) '{token['value']}'")
        
        # Check what mode is active
        active_mode = page.evaluate("""
            const editor = ace.edit('monaco-editor');
            editor.getSession().getMode().$id
        """)
        print(f"\\nActive mode: {active_mode}")
        
        # Check for key highlighting
        support_func = page.locator('.ace_support.ace_function')
        if support_func.count() > 0:
            style = page.evaluate("""
                window.getComputedStyle(document.querySelector('.ace_support.ace_function')).color
            """)
            print(f"\\nKey color: {style}")
        else:
            print("\\nNo ace_support.ace_function elements found!")
            print("Keys may not be getting proper highlighting.")
    
    def test_full_config_highlighting(self, page: Page, base_url):
        """Test highlighting on a full Klipper config."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Generate a config first
        page.click("#generate-btn")
        page.wait_for_timeout(2000)
        
        # Take screenshot of the generated config highlighting
        page.screenshot(path='test-results/full_config_highlighting.png', full_page=False)
        
        # Log all the token types found in the editor
        tokens = page.evaluate("""
            const editor = ace.edit('monaco-editor');
            const session = editor.getSession();
            const tokens = [];
            for (let i = 0; i < session.getLength(); i++) {
                const lineTokens = session.getTokens(i);
                lineTokens.forEach(token => {
                    if (token.type) tokens.push({type: token.type, value: token.value});
                });
            }
            tokens.slice(0, 50); // First 50 tokens
        """)
        
        print("\\n=== Token Types Found ===")
        for token in tokens[:20]:
            print(f"  {token['type']}: {token['value'][:30]}")
    
    def test_list_all_css_colors(self, page: Page, base_url):
        """List all computed colors in the editor for debugging."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Set specific test content to check each token type
        test_lines = [
            "; Comment line",
            "[mcu]",
            "step_pin: PB10",
            "enable: true",
            "speed: 300"
        ]
        
        # Test each line individually
        for line in test_lines:
            page.evaluate(f"""
                ace.edit('monaco-editor').setValue(`{line}`, -1);
            """)
            page.wait_for_timeout(200)
            
            # Get token colors for this line
            token_info = page.evaluate("""
                const editor = ace.edit('monaco-editor');
                const spans = editor.container.querySelectorAll('span.ace_');
                const info = [];
                spans.forEach(span => {
                    const text = span.textContent.trim();
                    const classes = span.className;
                    const color = window.getComputedStyle(span).color;
                    if (text && classes.includes('ace_')) {
                        info.push({
                            text: text,
                            classes: classes.replace('ace_', ''),
                            color: color
                        });
                    }
                });
                info;
            """)
            
            print(f"\\n{line}")
            for token in token_info[:5]:  # Show first 5 tokens
                print(f"  → {token['text']:<15} ({token['classes']:<25}) = {token['color']}")
        
        # Final comprehensive test
        full_content = """; MCU Configuration
[mcu]
serial: /dev/ttyUSB0
restart_method: command

[stepper_x]
step_pin: PB10
dir_pin: !PB11
rotation_distance: 40
position_min: 0
homing_speed: 50"""
        
        page.evaluate(f"""
            ace.edit('monaco-editor').setValue(`{full_content}`, -1);
        """)
        page.wait_for_timeout(500)
        
        # Get unique token class -> color mappings
        color_map = page.evaluate("""
            const editor = ace.edit('monaco-editor');
            const spans = editor.container.querySelectorAll('span[class*="ace_"]');
            const map = {};
            spans.forEach(span => {
                const classes = span.className.match(/ace_\\w+/g);
                const color = window.getComputedStyle(span).color;
                if (classes) {
                    classes.forEach(cls => {
                        if (!map[cls]) map[cls] = color;
                    });
                }
            });
            map;
        """)
        
        print("\\n=== Token Class to Color Mapping ===")
        for cls, color in sorted(color_map.items()):
            print(f"  {cls:<30} = {color}")
        
        page.screenshot(path='test-results/varied_content_highlighting.png')


def test_mainsail_comparison_screenshot(page: Page, base_url):
    """Create a screenshot showing config that should match Mainsail."""
    page.goto(base_url)
    page.wait_for_timeout(1000)
    
    mainsail_like_config = """; MCU configuration
[mcu]
serial: /dev/ttyUSB0
restart_method: command

; Stepper configuration
[stepper_x]
step_pin: PB10
dir_pin: !PB11
enable_pin: !PG0
rotation_distance: 40
microsteps: 16
full_steps_per_rotation: 200
position_min: 0
position_endstop: 150
position_max: 150
homing_speed: 50
homing_retract_dist: 5
second_homing_speed: 10

[tmc5160 stepper_x]
cs_pin: PE15
spi_bus: spi4
interpolate: true
run_current: 1.0
stealthchop_threshold: 0

[extruder]
step_pin: PD4
dir_pin: !PD3
enable_pin: !PD7
heater_pin: PG10
sensor_pin: PA1
pullup_resistor: 4700

[gcode_macro PRINT_START]
gcode:
    G28 ; Home all axes
    G1 Z5 F3000 ; Move to safe height
    ; Purge line
    G1 X10 Y20 F1500
    G1 Z0.28 ; Move to first layer height
    G1 X60 Y20 E10 F1500 ; Extrude purge line"""
    
    page.evaluate(f"""
        ace.edit('monaco-editor').setValue(`{mainsail_like_config}`, -1);
    """)
    
    page.wait_for_timeout(1000)
    page.screenshot(path='test-results/mainsail_comparison.png')
    print("Created test-results/mainsail_comparison.png")
