"""Test VSCode Dark+ theme syntax highlighting colors - matching old commit 155e476"""

import pytest
from playwright.sync_api import Page, expect
import re


class TestVSCodeThemeColors:
    """Test that syntax highlighting uses VSCode Dark+ theme colors from old commit."""
    
    def test_tomorrow_night_theme_is_active(self, page: Page, base_url):
        """Test that the tomorrow_night theme is active (from old commit)."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Get the active theme
        active_theme = page.evaluate("() => { return ace.edit('ace-editor').getTheme(); }")
        
        print(f"Active theme: {active_theme}")
        assert 'tomorrow_night' in active_theme.lower(), f"Expected tomorrow_night theme, got: {active_theme}"
    
    def test_sections_use_variable_token(self, page: Page, base_url):
        """Test that section brackets use variable token type (old commit style)."""
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
        
        # Should have variable token for brackets (old commit style)
        has_variable = any('variable' in str(t.get('type', '')) for t in tokens)
        # Should have string token for section name
        has_string = any('string' in str(t.get('type', '')) for t in tokens)
        
        print(f"Has variable (brackets): {has_variable}")
        print(f"Has string (section name): {has_string}")
        
        assert has_variable, f"Should have variable token for brackets '[mcu]', got: {tokens}"
        assert has_string, f"Should have string token for section name, got: {tokens}"
    
    def test_keys_use_support_function_token(self, page: Page, base_url):
        """Test that keys use support.function token type (old commit style)."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Set content with a key
        page.evaluate("() => { ace.edit('ace-editor').setValue('step_pin: PB10', -1); }")
        page.wait_for_timeout(500)
        
        # Take screenshot
        page.screenshot(path='test-results/key_highlighting.png')
        
        # Get tokens
        tokens = page.evaluate("""() => {
            const editor = ace.edit('ace-editor');
            const session = editor.getSession();
            const tokens = [];
            for (let i = 0; i < session.getLength(); i++) {
                const lineTokens = session.getTokens(i);
                lineTokens.forEach(token => {
                    tokens.push({
                        type: token.type,
                        value: token.value
                    });
                });
            }
            return tokens;
        }""")
        
        print("\n=== Tokens for 'step_pin: PB10' ===")
        for token in tokens:
            print(f"  {token['type']:<30} = '{token['value']}'")
        
        # Should have support.function token for key name (old commit style)
        key_token = [t for t in tokens if 'support.function' in (t.get('type') or '')]
        assert len(key_token) > 0, f"Should have support.function token for 'step_pin', got: {tokens}"
    
    def test_pins_use_constant_token(self, page: Page, base_url):
        """Test that pin names use constant token type (old commit style)."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Set content with a pin
        page.evaluate("() => { ace.edit('ace-editor').setValue('pin: PA0', -1); }")
        page.wait_for_timeout(500)
        
        # Get tokens
        tokens = page.evaluate("""() => {
            const editor = ace.edit('ace-editor');
            const session = editor.getSession();
            const tokens = [];
            for (let i = 0; i < session.getLength(); i++) {
                const lineTokens = session.getTokens(i);
                lineTokens.forEach(token => {
                    tokens.push({
                        type: token.type,
                        value: token.value
                    });
                });
            }
            return tokens;
        }""")
        
        print("\n=== Tokens for 'pin: PA0' ===")
        for token in tokens:
            print(f"  {token['type']:<30} = '{token['value']}'")
        
        # Should have constant token for pin (old commit style)
        pin_token = [t for t in tokens if 'constant' in (t.get('type') or '') and 'numeric' not in (t.get('type') or '')]
        assert len(pin_token) > 0, f"Should have constant token for pin 'PA0', got: {tokens}"
    
    def test_numbers_use_constant_numeric_token(self, page: Page, base_url):
        """Test that numbers use constant.numeric token type (old commit style)."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Set content with a number
        page.evaluate("() => { ace.edit('ace-editor').setValue('value: 300', -1); }")
        page.wait_for_timeout(500)
        
        # Get tokens
        tokens = page.evaluate("""() => {
            const editor = ace.edit('ace-editor');
            const session = editor.getSession();
            const tokens = [];
            for (let i = 0; i < session.getLength(); i++) {
                const lineTokens = session.getTokens(i);
                lineTokens.forEach(token => {
                    tokens.push({
                        type: token.type,
                        value: token.value
                    });
                });
            }
            return tokens;
        }""")
        
        print("\n=== Tokens for 'value: 300' ===")
        for token in tokens:
            print(f"  {token['type']:<30} = '{token['value']}'")
        
        # Should have constant.numeric token for number (old commit style)
        num_token = [t for t in tokens if 'constant.numeric' in (t.get('type') or '')]
        assert len(num_token) > 0, f"Should have constant.numeric token for '300', got: {tokens}"
    
    def test_booleans_use_keyword_token(self, page: Page, base_url):
        """Test that booleans use keyword token type (old commit style)."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Set content with a boolean
        page.evaluate("() => { ace.edit('ace-editor').setValue('interpolate: true', -1); }")
        page.wait_for_timeout(500)
        
        # Get tokens
        tokens = page.evaluate("""() => {
            const editor = ace.edit('ace-editor');
            const session = editor.getSession();
            const tokens = [];
            for (let i = 0; i < session.getLength(); i++) {
                const lineTokens = session.getTokens(i);
                lineTokens.forEach(token => {
                    tokens.push({
                        type: token.type,
                        value: token.value
                    });
                });
            }
            return tokens;
        }""")
        
        print("\n=== Tokens for 'interpolate: true' ===")
        for token in tokens:
            print(f"  {token['type']:<30} = '{token['value']}'")
        
        # Should have keyword token for boolean (old commit style)
        bool_token = [t for t in tokens if t.get('type') == 'keyword']
        assert len(bool_token) > 0, f"Should have keyword token for 'true', got: {tokens}"
    
    def test_full_config_old_commit_style(self, page: Page, base_url):
        """Test highlighting matches old commit 155e476 style."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Generate a config
        page.click("#generate-btn")
        page.wait_for_timeout(2000)
        
        # Take screenshot
        page.screenshot(path='test-results/old_commit_style.png', full_page=False)
        
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
        
        print("\n=== First 50 Tokens (Old Commit Style) ===")
        for token in tokens_sample:
            print(f"  L{token['line']}: {token['type']:<30} = '{token['value']}'")
        
        # Verify all expected token types from old commit
        token_types = set(t['type'] for t in tokens_sample)
        print(f"\n=== Token Types Found ===")
        for t in sorted(token_types):
            print(f"  - {t}")
        
        # Should have variable (section brackets)
        has_variable = any('variable' in t for t in token_types)
        assert has_variable, "Should have variable tokens for section brackets"
        
        # Should have string (section names and values)
        has_string = any('string' in t for t in token_types)
        assert has_string, "Should have string tokens"
        
        # Should have support.function (keys)
        has_keys = any('support.function' in t for t in token_types)
        assert has_keys, "Should have support.function tokens for keys"
        
        # Should have comment
        has_comments = any('comment' in t for t in token_types)
        assert has_comments, "Should have comment tokens"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
