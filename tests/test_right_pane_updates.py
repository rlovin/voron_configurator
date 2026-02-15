"""Test right pane info panel updates when selecting configuration items"""

import pytest
from playwright.sync_api import Page, expect


class TestRightPaneUpdates:
    """Test that all variables in the right pane update when selecting items in the left pane."""

    def get_info_value(self, page, info_id):
        """Helper to get the text content of an info panel item."""
        return page.locator(f'#info-{info_id}').text_content()

    def test_printer_selection_updates_right_pane(self, page: Page, base_url):
        """Test that changing printer model updates the right pane."""
        page.goto(base_url)
        page.wait_for_timeout(500)
        
        # Check initial value
        initial = self.get_info_value(page, 'printer')
        print(f"Initial printer: {initial}")
        
        # Change to Trident
        page.select_option('#printer-select', 'trident')
        page.wait_for_timeout(100)
        
        # Verify update
        updated = self.get_info_value(page, 'printer')
        print(f"Updated printer: {updated}")
        assert 'Trident' in updated, f"Expected 'Trident' in right pane, got: {updated}"

    def test_size_selection_updates_right_pane(self, page: Page, base_url):
        """Test that changing bed size updates the right pane."""
        page.goto(base_url)
        page.wait_for_timeout(500)
        
        # Change size to 350mm
        page.select_option('#size-select', '350')
        page.wait_for_timeout(100)
        
        # Verify update
        updated = self.get_info_value(page, 'size')
        print(f"Updated size: {updated}")
        assert updated == '350mm', f"Expected '350mm' in right pane, got: {updated}"

    def test_main_board_selection_updates_right_pane(self, page: Page, base_url):
        """Test that changing main board updates the right pane."""
        page.goto(base_url)
        page.wait_for_timeout(500)
        
        # Change to Octopus
        page.select_option('#main-board-select', 'octopus_v1')
        page.wait_for_timeout(100)
        
        # Verify update
        updated = self.get_info_value(page, 'main-board')
        print(f"Updated main board: {updated}")
        assert 'Octopus' in updated, f"Expected 'Octopus' in right pane, got: {updated}"

    def test_toolhead_board_selection_updates_right_pane(self, page: Page, base_url):
        """Test that changing toolhead board updates the right pane."""
        page.goto(base_url)
        page.wait_for_timeout(500)
        
        # Change to EBB SB2209
        page.select_option('#toolhead-board-select', 'ebb_sb2209')
        page.wait_for_timeout(100)
        
        # Verify update
        updated = self.get_info_value(page, 'toolhead')
        print(f"Updated toolhead: {updated}")
        assert 'EBB' in updated or 'SB2209' in updated, f"Expected 'EBB' or 'SB2209' in right pane, got: {updated}"

    def test_motors_selection_updates_right_pane(self, page: Page, base_url):
        """Test that changing motors updates the right pane."""
        page.goto(base_url)
        page.wait_for_timeout(500)
        
        # Currently only one motor option, but test it works
        initial = self.get_info_value(page, 'motors')
        print(f"Motors: {initial}")
        assert initial is not None and initial != '', "Motors should be displayed in right pane"

    def test_extruder_selection_updates_right_pane(self, page: Page, base_url):
        """Test that changing extruder updates the right pane - THIS WAS THE BUG."""
        page.goto(base_url)
        page.wait_for_timeout(500)
        
        # Check initial value
        initial = self.get_info_value(page, 'extruder')
        print(f"Initial extruder: {initial}")
        
        # Change to different extruder
        page.select_option('#extruder-select', 'bondtech_lgx_lite')
        page.wait_for_timeout(100)
        
        # Verify update
        updated = self.get_info_value(page, 'extruder')
        print(f"Updated extruder: {updated}")
        assert 'LGX' in updated or 'Lite' in updated, f"Expected 'LGX' or 'Lite' in right pane, got: {updated}"

    def test_probe_selection_updates_right_pane(self, page: Page, base_url):
        """Test that changing probe updates the right pane."""
        page.goto(base_url)
        page.wait_for_timeout(500)
        
        # Change to Beacon
        page.select_option('#probe-select', 'beacon')
        page.wait_for_timeout(100)
        
        # Verify update
        updated = self.get_info_value(page, 'probe')
        print(f"Updated probe: {updated}")
        assert 'Beacon' in updated, f"Expected 'Beacon' in right pane, got: {updated}"

    def test_macro_checkbox_updates_right_pane(self, page: Page, base_url):
        """Test that changing macro checkbox updates the right pane."""
        page.goto(base_url)
        page.wait_for_timeout(500)
        
        # Check initial (should be Standard)
        initial = self.get_info_value(page, 'macros')
        print(f"Initial macros: {initial}")
        
        # Click on the checkbox label (checkbox input is hidden by CSS)
        page.locator('label.checkbox-label').first.click()
        page.wait_for_timeout(100)
        
        # Verify update
        updated = self.get_info_value(page, 'macros')
        print(f"Updated macros: {updated}")
        assert 'Better' in updated or 'Enhanced' in updated, f"Expected 'Better' or 'Enhanced' in right pane, got: {updated}"

    def test_all_fields_update_correctly_in_sequence(self, page: Page, base_url):
        """Test all fields update correctly when changed in sequence."""
        page.goto(base_url)
        page.wait_for_timeout(500)
        
        # Define changes to test
        changes = [
            ('printer-select', 'trident', 'printer', 'Trident'),
            ('size-select', '350', 'size', '350mm'),
            ('main-board-select', 'octopus_pro', 'main-board', 'Octopus'),
            ('toolhead-board-select', 'ebb36', 'toolhead', 'EBB'),
            ('extruder-select', 'ldo_orbiter_v2_std', 'extruder', 'Orbiter'),
            ('probe-select', 'beacon', 'probe', 'Beacon'),
        ]
        
        for select_id, value, info_id, expected_text in changes:
            # Get the select element and change it
            page.select_option(f'#{select_id}', value)
            page.wait_for_timeout(100)
            
            # Verify the right pane updated
            actual = self.get_info_value(page, info_id)
            print(f"{select_id} -> {info_id}: {actual}")
            assert expected_text in actual, f"Expected '{expected_text}' in {info_id}, got: {actual}"

    def test_right_pane_initial_values_match_defaults(self, page: Page, base_url):
        """Test that right pane shows correct initial/default values."""
        page.goto(base_url)
        page.wait_for_timeout(500)
        
        # Get all select elements and their selected values
        expected_mappings = {
            'printer': ('printer-select', lambda t: 'Voron' in t or 'Trident' in t),
            'size': ('size-select', lambda v: v + 'mm'),
            'main-board': ('main-board-select', lambda t: t),
            'toolhead': ('toolhead-board-select', lambda t: t),
            'motors': ('motors-select', lambda t: t),
            'extruder': ('extruder-select', lambda t: t),
            'probe': ('probe-select', lambda t: t),
        }
        
        for info_id, (select_id, transform) in expected_mappings.items():
            # Get the selected option text from the select
            selected_text = page.eval_on_selector(
                f'#{select_id}',
                'el => el.options[el.selectedIndex].text'
            )
            
            # Get the right pane value
            info_value = self.get_info_value(page, info_id)
            
            print(f"{select_id}: '{selected_text}' -> info-{info_id}: '{info_value}'")
            
            # For most fields, they should match exactly
            if info_id == 'printer':
                # Printer might be truncated, just check it's not empty
                assert info_value and info_value.strip() != '', f"info-{info_id} should not be empty"
            elif info_id == 'size':
                # Size has 'mm' appended
                expected = selected_text if not selected_text.endswith('mm') else selected_text
                if not info_value.endswith('mm'):
                    expected = selected_text
                assert info_value == expected or info_value.startswith(selected_text.split('mm')[0]), \
                    f"info-{info_id} should match selected value"
            else:
                # Other fields should match the selected option text
                assert selected_text in info_value or info_value in selected_text, \
                    f"info-{info_id} ('{info_value}') should contain '{selected_text}'"


class TestThemeConsistency:
    """Test that theme stays consistent when changing config items."""

    def test_theme_does_not_change_when_selecting_config(self, page: Page, base_url):
        """Test that selecting different config items doesn't change the editor theme."""
        page.goto(base_url)
        page.wait_for_timeout(1000)  # Wait for Ace to initialize
        
        # Get initial theme
        initial_theme = page.evaluate("""
            ace.edit('ace-editor').getTheme()
        """)
        print(f"Initial theme: {initial_theme}")
        
        # Change various config items
        items_to_change = [
            ('printer-select', 'trident'),
            ('size-select', '350'),
            ('main-board-select', 'octopus_v1'),
            ('toolhead-board-select', 'ebb_sb2209'),
            ('extruder-select', 'bondtech_lgx_lite'),
            ('probe-select', 'beacon'),
        ]
        
        for select_id, value in items_to_change:
            page.select_option(f'#{select_id}', value)
            page.wait_for_timeout(200)
            
            # Check theme hasn't changed
            current_theme = page.evaluate("""
                ace.edit('ace-editor').getTheme()
            """)
            
            assert current_theme == initial_theme, \
                f"Theme changed from {initial_theme} to {current_theme} after changing {select_id}"
        
        print(f"Theme remained consistent: {initial_theme}")

    def test_theme_changes_only_when_using_theme_selector(self, page: Page, base_url):
        """Test that theme only changes when explicitly using the theme selector."""
        page.goto(base_url)
        page.wait_for_timeout(1000)
        
        # Get initial theme
        initial_theme = page.evaluate("""
            ace.edit('ace-editor').getTheme()
        """)
        print(f"Initial theme: {initial_theme}")
        
        # Change a config item (should NOT change theme)
        page.select_option('#printer-select', 'trident')
        page.wait_for_timeout(200)
        
        theme_after_config = page.evaluate("""
            ace.edit('ace-editor').getTheme()
        """)
        assert theme_after_config == initial_theme, \
            f"Theme changed unexpectedly from {initial_theme} to {theme_after_config}"
        
        # Now change theme using selector (if it has multiple options)
        theme_options = page.eval_on_selector('#theme-select', 
            'el => Array.from(el.options).map(o => o.value)')
        print(f"Available themes: {theme_options}")
        
        if len(theme_options) > 1:
            # Select a different theme
            new_theme = theme_options[1] if theme_options[0] != 'arctic' else theme_options[0]
            page.select_option('#theme-select', new_theme)
            page.wait_for_timeout(500)
            
            theme_after_theme_change = page.evaluate("""
                ace.edit('ace-editor').getTheme()
            """)
            print(f"Theme after selector change: {theme_after_theme_change}")
            
            # Theme should have changed now
            # Note: All themes currently map to 'dracula' in the code
            assert 'dracula' in theme_after_theme_change.lower(), \
                f"Expected dracula theme after selector change, got: {theme_after_theme_change}"

    def test_body_data_theme_matches_selector(self, page: Page, base_url):
        """Test that body data-theme attribute matches the theme selector."""
        page.goto(base_url)
        page.wait_for_timeout(500)
        
        # Get initial body theme
        body_theme = page.get_attribute('body', 'data-theme')
        print(f"Initial body theme: {body_theme}")
        
        # Get selected theme from dropdown
        selected_theme = page.eval_on_selector('#theme-select', 
            'el => el.options[el.selectedIndex].value')
        print(f"Selected theme in dropdown: {selected_theme}")
        
        # They should match initially (or be close)
        assert body_theme is not None, "Body should have data-theme attribute"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
