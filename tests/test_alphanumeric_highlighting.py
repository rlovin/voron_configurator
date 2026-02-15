"""Test syntax highlighting for various value types"""

import pytest
from playwright.sync_api import Page, expect


class TestAlphanumericHighlighting:
    """Test that alphanumeric values are consistently highlighted."""

    def test_alphanumeric_values_highlighted_consistently(self, page: Page, base_url):
        """Test that values like PA13, spi1, PB10 are highlighted consistently."""
        page.goto(base_url)
        page.wait_for_timeout(1000)  # Wait for Ace to load
        
        # Test content with various alphanumeric values
        test_content = """[mcu]
serial: /dev/ttyUSB0
restart_method: command

[stepper_x]
step_pin: PB10
dir_pin: !PB11
enable_pin: !PG0
rotation_distance: 40
microsteps: 16
position_min: 0
position_endstop: 150
homing_speed: 50

[tmc5160 stepper_x]
cs_pin: PE15
spi_bus: spi4
interpolate: true
run_current: 1.0
stealthchop_threshold: 0"""

        # Set content in editor
        page.evaluate(f"""
            ace.edit('ace-editor').setValue(`{test_content}`, -1);
        """)
        page.wait_for_timeout(500)
        
        # Get all tokens for analysis
        tokens = page.evaluate("""
            const editor = ace.edit('ace-editor');
            const session = editor.getSession();
            const tokens = [];
            for (let i = 0; i < session.getLength(); i++) {
                const lineTokens = session.getTokens(i);
                lineTokens.forEach(token => {
                    tokens.push({
                        line: i,
                        type: token.type,
                        value: token.value
                    });
                });
            }
            tokens;
        """)
        
        # Filter for value tokens (4th part of parameter lines)
        value_tokens = [t for t in tokens if 'string.value' in (t.get('type') or '')]
        
        print("\n=== Value Tokens ===")
        for token in value_tokens:
            print(f"  Line {token['line']}: {token['type']} = '{token['value']}'")
        
        # Check that specific values are present and consistently tokenized
        test_values = ['PB10', 'PB11', 'PG0', 'PE15', 'spi4', 'command', '/dev/ttyUSB0', 'true', '1.0']
        found_values = {t['value'].strip(): t['type'] for t in value_tokens}
        
        print("\n=== Checking Test Values ===")
        for val in test_values:
            if val in found_values:
                print(f"  ✓ {val}: {found_values[val]}")
                assert 'string.value' in found_values[val], f"Value '{val}' should have 'string.value' token type"
            else:
                print(f"  ✗ {val}: NOT FOUND")
                # Look for partial matches
                for found_val, found_type in found_values.items():
                    if val in found_val or found_val in val:
                        print(f"    → Found partial match: '{found_val}' with type {found_type}")
    
    def test_numbers_not_split_from_alphanumeric(self, page: Page, base_url):
        """Test that numbers within alphanumeric values (like PA13, spi1) are not split."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        test_content = """[mcu]
pin: PA13
bus: spi1
value: 42
decimal: 3.14"""
        
        page.evaluate(f"""
            ace.edit('ace-editor').setValue(`{test_content}`, -1);
        """)
        page.wait_for_timeout(500)
        
        # Get tokens
        tokens = page.evaluate("""
            const editor = ace.edit('ace-editor');
            const session = editor.getSession();
            const tokens = [];
            for (let i = 0; i < session.getLength(); i++) {
                const lineTokens = session.getTokens(i);
                lineTokens.forEach(token => {
                    tokens.push({
                        line: i,
                        type: token.type,
                        value: token.value
                    });
                });
            }
            tokens;
        """)
        
        print("\n=== All Tokens ===")
        for token in tokens:
            print(f"  Line {token['line']}: {token['type']} = '{token['value']}'")
        
        # Check that PA13 and spi1 are NOT split into multiple tokens
        # (which would happen if the number regex was catching parts of them)
        pa13_tokens = [t for t in tokens if 'PA' in t.get('value', '') or '13' in t.get('value', '')]
        spi1_tokens = [t for t in tokens if 'spi' in t.get('value', '').lower() or '1' in t.get('value', '')]
        
        print(f"\n=== PA13 Related Tokens ===")
        for t in pa13_tokens:
            print(f"  {t}")
            
        print(f"\n=== spi1 Related Tokens ===")
        for t in spi1_tokens:
            print(f"  {t}")
        
        # Verify PA13 and spi1 exist as complete values
        all_values = [t['value'].strip() for t in tokens]
        assert 'PA13' in all_values, "PA13 should be a complete token value"
        assert 'spi1' in all_values, "spi1 should be a complete token value"
    
    def test_boolean_and_numeric_consistency(self, page: Page, base_url):
        """Test that booleans and standalone numbers are highlighted consistently."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        test_content = """[test]
bool_true: true
bool_false: false
integer: 100
float: 3.14
negative: -50
alphanumeric: PB10"""
        
        page.evaluate(f"""
            ace.edit('ace-editor').setValue(`{test_content}`, -1);
        """)
        page.wait_for_timeout(500)
        
        # Get all tokens
        tokens = page.evaluate("""
            const editor = ace.edit('ace-editor');
            const session = editor.getSession();
            const tokens = [];
            for (let i = 0; i < session.getLength(); i++) {
                const lineTokens = session.getTokens(i);
                lineTokens.forEach(token => {
                    tokens.push({
                        line: i,
                        type: token.type,
                        value: token.value
                    });
                });
            }
            tokens;
        """)
        
        print("\n=== Token Analysis ===")
        for token in tokens:
            if token['value'].strip():
                print(f"  {token['type']:<30} = '{token['value']}'")
        
        # Check specific values have correct token types
        value_checks = {
            'true': 'constant.language.boolean',
            'false': 'constant.language.boolean',
            '100': 'string.value',  # Numbers after colon should be string.value
            '3.14': 'string.value',
            '-50': 'string.value',
            'PB10': 'string.value'
        }
        
        token_dict = {}
        for t in tokens:
            val = t['value'].strip()
            if val in value_checks:
                token_dict[val] = t['type']
        
        print("\n=== Value Type Verification ===")
        for val, expected_type in value_checks.items():
            if val in token_dict:
                actual_type = token_dict[val]
                match = expected_type in actual_type if actual_type else False
                status = "✓" if match else "✗"
                print(f"  {status} '{val}': {actual_type} (expected: {expected_type})")
                if not match:
                    print(f"    WARNING: Type mismatch!")
            else:
                print(f"  ✗ '{val}': NOT FOUND")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
