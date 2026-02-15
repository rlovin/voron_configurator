"""UI/End-to-End Tests for Voron Configurator using Playwright"""

import pytest
from playwright.sync_api import Page, expect


class TestMainPage:
    """Test the main page and basic UI elements."""

    def test_page_title(self, page: Page, live_server):
        """Test that the page title is correct."""
        page.goto(live_server.url)
        expect(page).to_have_title("Voron Configurator")

    def test_editor_visible(self, page: Page, live_server):
        """Test that the Ace editor is visible on page load."""
        page.goto(live_server.url)
        
        # Check that the editor container is present
        editor = page.locator("#monaco-editor")
        expect(editor).to_be_visible()
        
        # Check that Ace editor has initialized (should have content)
        ace_editor = page.locator(".ace_editor")
        expect(ace_editor).to_be_visible()

    def test_sidebars_visible(self, page: Page, live_server):
        """Test that both sidebars are visible."""
        page.goto(live_server.url)
        
        left_sidebar = page.locator(".sidebar-left")
        right_sidebar = page.locator(".sidebar-right")
        
        expect(left_sidebar).to_be_visible()
        expect(right_sidebar).to_be_visible()

    def test_generate_button_exists(self, page: Page, live_server):
        """Test that the generate button is present."""
        page.goto(live_server.url)
        
        generate_btn = page.locator("#generate-btn")
        expect(generate_btn).to_be_visible()
        expect(generate_btn).to_contain_text("Generate Config")


class TestConfigGeneration:
    """Test config generation through the UI."""

    def test_generate_config_updates_editor(self, page: Page, live_server):
        """Test that clicking generate updates the editor content."""
        page.goto(live_server.url)
        
        # Select options
        page.select_option("#printer-select", "voron2.4")
        page.select_option("#size-select", "300")
        page.select_option("#main-board-select", "leviathan")
        page.select_option("#toolhead-board-select", "nitehawk")
        page.select_option("#probe-select", "tap")
        
        # Click generate
        page.click("#generate-btn")
        
        # Wait for the status to show success
        status_bar = page.locator(".status-bar")
        expect(status_bar).to_contain_text("Configuration generated successfully", timeout=10000)
        
        # Check that editor contains the generated config
        ace_editor = page.locator(".ace_editor")
        expect(ace_editor).to_contain_text("[mcu]")
        expect(ace_editor).to_contain_text("[stepper_x]")

    def test_different_printer_types(self, page: Page, live_server):
        """Test generating configs for different printer types."""
        page.goto(live_server.url)
        
        printers = ['voron2.4', 'trident']
        
        for printer in printers:
            page.select_option("#printer-select", printer)
            page.select_option("#main-board-select", "leviathan")
            page.click("#generate-btn")
            
            # Wait for generation
            status_bar = page.locator(".status-bar")
            expect(status_bar).to_contain_text("Configuration generated successfully", timeout=10000)
            
            # Verify config was generated
            ace_editor = page.locator(".ace_editor")
            expect(ace_editor).to_contain_text("[mcu]")


class TestReferenceConfigs:
    """Test LDO reference config functionality."""

    def test_reference_config_dropdown_populated(self, page: Page, live_server):
        """Test that the reference config dropdown has options."""
        page.goto(live_server.url)
        
        # Wait for dropdown to be populated via AJAX
        page.wait_for_timeout(1000)
        
        select = page.locator("#ldo-ref-config-select")
        options = select.locator("option")
        
        # Should have at least 6 options (configs loaded dynamically)
        count = options.count()
        assert count > 6

    def test_load_reference_config_in_main(self, page: Page, live_server):
        """Test loading a reference config into the main editor."""
        page.goto(live_server.url)
        
        # Wait for dropdown to populate
        page.wait_for_timeout(1000)
        
        # Select a reference config
        page.select_option("#ldo-ref-config-select", "voron2.4_leviathan_rev_d")
        
        # Click load button (not tab button)
        page.click("#load-ref-config-btn")
        
        # Wait for config to load
        page.wait_for_timeout(2000)
        
        # Check that editor contains reference config
        ace_editor = page.locator(".ace_editor")
        expect(ace_editor).to_contain_text("[mcu]")

    def test_open_reference_config_in_new_tab(self, page: Page, live_server):
        """Test opening a reference config in a new tab."""
        page.goto(live_server.url)
        
        # Wait for dropdown to populate
        page.wait_for_timeout(1000)
        
        # Select a reference config
        page.select_option("#ldo-ref-config-select", "voron2.4_leviathan_rev_d")
        
        # Click open in new tab button
        page.click("#open-ref-tab-btn")
        
        # Wait for tab to appear
        page.wait_for_timeout(2000)
        
        # Check that a new tab was created
        tabs = page.locator(".tab")
        expect(tabs).to_have_count(2)  # Main + 1 reference tab
        
        # Check for reference tab
        ref_tab = page.locator(".reference-tab")
        expect(ref_tab).to_be_visible()


class TestThemeSwitching:
    """Test theme switching functionality."""

    def test_theme_dropdown_exists(self, page: Page, live_server):
        """Test that the theme dropdown is present."""
        page.goto(live_server.url)
        
        theme_select = page.locator("#theme-select")
        expect(theme_select).to_be_visible()

    def test_switch_theme(self, page: Page, live_server):
        """Test switching themes."""
        page.goto(live_server.url)
        
        # Get initial body data-theme
        initial_theme = page.evaluate("document.body.dataset.theme")
        
        # Switch to a different theme
        page.select_option("#theme-select", "forest")
        
        # Check that body data-theme changed
        new_theme = page.evaluate("document.body.dataset.theme")
        assert new_theme == "forest"


class TestInfoPanel:
    """Test the right sidebar info panel."""

    def test_info_panel_updates_on_selection(self, page: Page, live_server):
        """Test that the info panel updates when selections change."""
        page.goto(live_server.url)
        
        # Change printer
        page.select_option("#printer-select", "trident")
        
        # Check info panel updated
        info_printer = page.locator("#info-printer")
        expect(info_printer).to_contain_text("Trident")
        
        # Change board
        page.select_option("#main-board-select", "octopus_v1")
        
        # Check info panel updated
        info_board = page.locator("#info-main-board")
        expect(info_board).to_contain_text("Octopus")


class TestDownload:
    """Test the download functionality."""

    def test_download_button_disabled_initially(self, page: Page, live_server):
        """Test that download button is disabled before config generation."""
        page.goto(live_server.url)
        
        download_btn = page.locator("#download-btn")
        expect(download_btn).to_be_disabled()

    def test_download_button_enabled_after_generation(self, page: Page, live_server):
        """Test that download button is enabled after generating config."""
        page.goto(live_server.url)
        
        # Generate a config
        page.click("#generate-btn")
        
        # Wait for generation
        status_bar = page.locator(".status-bar")
        expect(status_bar).to_contain_text("Configuration generated successfully", timeout=10000)
        
        # Check download button is enabled
        download_btn = page.locator("#download-btn")
        expect(download_btn).to_be_enabled()
