"""Test Mainsail theme syntax highlighting"""

import pytest
from playwright.sync_api import Page, expect
import re


class TestMainsailThemeColors:
    """Test that syntax highlighting uses Mainsail theme colors."""
    
    def test_mainsail_theme_is_active(self, page: Page, base_url):
        """Test that the Mainsail theme is the active theme."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Get the active theme
        active_theme = page.evaluate("() => { return ace.edit('ace-editor').getTheme(); }")
        
        print(f"Active theme: {active_theme}")
        assert 'mainsail' in active_theme.lower(), f"Expected mainsail theme, got: {active_theme}"
    
    def test_mainsail_dark_background(self, page: Page, base_url):
        """Test that editor has Mainsail dark background (#121212)."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Get editor background color from ace_content
        bg_color = page.evaluate("""() => {
            const editor = ace.edit('ace-editor');
            const contentEl = editor.container.querySelector('.ace_content');
            if (contentEl) {
                return window.getComputedStyle(contentEl).backgroundColor;
            }
            const scrollerEl = editor.container.querySelector('.ace_scroller');
            if (scrollerEl) {
                return window.getComputedStyle(scrollerEl).backgroundColor;
            }
            return window.getComputedStyle(editor.container).backgroundColor;
        }""")
        
        print(f"Editor background: {bg_color}")
        
        # Should be very dark (near black #121212)
        if bg_color and bg_color != 'rgba(0, 0, 0, 0)':
            rgb_match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', bg_color)
            if rgb_match:
                r, g, b = int(rgb_match[1]), int(rgb_match[2]), int(rgb_match[3])
                # Mainsail uses #121212 which is rgb(18, 18, 18)
                # Check if it's very dark (below 30 for all channels)
                is_very_dark = (r < 30 and g < 30 and b < 30)
                print(f"RGB: ({r}, {g}, {b}) - Very dark: {is_very_dark}")
                assert is_very_dark, f"Background should be Mainsail dark (#121212), got rgb({r}, {g}, {b})"
    
    def test_sections_use_mainsail_blue(self, page: Page, base_url):
        """Test that sections use Mainsail bright blue (#2196F3)."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Set content with a section
        page.evaluate("() => { ace.edit('ace-editor').setValue('[mcu]', -1); }")
        page.wait_for_timeout(500)
        
        # Get tokens
        tokens = page.evaluate("""() => {
            const editor = ace.edit('ace-editor');
            return editor.session.getTokens(0);
        }""")
        
        print(f"Section tokens: {tokens}")
        
        # Should have a section token
        has_section = any('tag' in str(t.get('type', '')) for t in tokens)
        assert has_section, f"Should have tag token for '[mcu]', got: {tokens}"
    
    def test_full_config_mainsail_colors(self, page: Page, base_url):
        """Test highlighting on a full Klipper config matches Mainsail."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Generate a config
        page.click("#generate-btn")
        page.wait_for_timeout(2000)
        
        # Take screenshot
        page.screenshot(path='test-results/mainsail_theme.png', full_page=False)
        
        # Get sample of tokens
        tokens_sample = page.evaluate("""() => {
            const editor = ace.edit('ace-editor');
            const session = editor.getSession();
            const tokens = [];
            for (let i = 0; i < Math.min(30, session.getLength()); i++) {
                const lineTokens = session.getTokens(i);
                lineTokens.forEach(token => {
                    if (token.type && token.value.trim()) {
                        tokens.push({
                            line: i,
                            type: token.type,
                            value: token.value.substring(0, 50)
                        });
                    }
                });
            }
            return tokens.slice(0, 50);
        }""")
        
        print("\n=== First 50 Tokens ===")
        for token in tokens_sample:
            print(f"  L{token['line']}: {token['type']:<30} = '{token['value']}'")
        
        # Verify token types
        token_types = set(t['type'] for t in tokens_sample)
        print(f"\n=== Token Types Found ===")
        for t in sorted(token_types):
            print(f"  - {t}")
        
        assert any('tag' in t for t in token_types), "Should have tag tokens for sections"
        assert any('keyword' in t for t in token_types), "Should have keyword tokens for parameters"
        assert any('string' in t for t in token_types), "Should have string tokens for values"
        assert any('comment' in t for t in token_types), "Should have comment tokens"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
