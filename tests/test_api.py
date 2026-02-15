"""API Tests for Voron Configurator"""

import pytest
import json


class TestGenerateConfig:
    """Test the config generation endpoint."""

    def test_generate_basic_config(self, client):
        """Test basic config generation for Voron 2.4."""
        response = client.post('/api/generate', 
            json={
                'printer': 'voron2.4',
                'size': '300',
                'main_board': 'leviathan',
                'toolhead_board': 'nitehawk',
                'motors': 'ldo',
                'probe': 'tap',
                'print_start': 'standard'
            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['config']) > 0
        assert '[mcu]' in data['config']
        assert '[stepper_x]' in data['config']
        assert '[stepper_y]' in data['config']
        assert '[stepper_z]' in data['config']

    def test_generate_trident_config(self, client):
        """Test config generation for Trident."""
        response = client.post('/api/generate',
            json={
                'printer': 'trident',
                'size': '300',
                'main_board': 'leviathan',
                'toolhead_board': 'nitehawk',
                'motors': 'ldo',
                'probe': 'klicky',
                'print_start': 'better'
            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['config']) > 0

    def test_generate_with_different_boards(self, client):
        """Test config generation with different board combinations."""
        boards = ['leviathan', 'octopus_v1', 'octopus_pro', 'spider_v23', 'manta_m8p']
        
        for board in boards:
            response = client.post('/api/generate',
                json={
                    'printer': 'voron2.4',
                    'size': '300',
                    'main_board': board,
                    'toolhead_board': 'nitehawk',
                    'motors': 'ldo',
                    'probe': 'tap',
                    'print_start': 'standard'
                })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['config']) > 0

    def test_leviathan_has_correct_mcu(self, client):
        """Test that Leviathan config uses STM32F446."""
        response = client.post('/api/generate',
            json={
                'printer': 'voron2.4',
                'size': '300',
                'main_board': 'leviathan',
                'toolhead_board': 'nitehawk',
                'motors': 'ldo',
                'probe': 'tap',
                'print_start': 'standard'
            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'STM32F446' in data['config']
        assert 'spi4' in data['config']  # TMC5160 uses SPI4

    def test_generate_missing_required_field(self, client):
        """Test that missing required fields still returns a valid response."""
        # The app is robust and handles missing fields by using defaults
        response = client.post('/api/generate',
            json={
                'printer': 'voron2.4',
                # Missing other required fields - app uses defaults
            })
        
        # App gracefully handles missing fields
        assert response.status_code == 200
        data = json.loads(response.data)
        # May not succeed if critical fields are missing
        assert 'success' in data


class TestReferenceConfigs:
    """Test the LDO reference config endpoints."""

    def test_get_all_reference_configs(self, client):
        """Test that all reference configs are returned."""
        response = client.get('/api/reference-configs')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['configs']) > 0
        
        # Should have configs for both Voron 2.4 and Trident
        config_names = [v['name'] for v in data['configs'].values()]
        assert any('2.4' in name for name in config_names)
        assert any('Trident' in name for name in config_names)

    def test_get_specific_reference_config(self, client):
        """Test fetching a specific reference config."""
        response = client.get('/api/reference-config?printer=voron2.4&board=leviathan&revision=rev_d')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['content']) > 0
        assert '[mcu]' in data['content']

    def test_get_nonexistent_config(self, client):
        """Test fetching a non-existent config returns 404."""
        response = client.get('/api/reference-config?printer=nonexistent&board=unknown&revision=rev_x')
        
        assert response.status_code == 404


class TestMainPage:
    """Test the main page endpoint."""

    def test_main_page_loads(self, client):
        """Test that the main page loads successfully."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Voron Configurator' in response.data
        assert b'monaco-editor' in response.data or b'ace_editor' in response.data


class TestReferenceView:
    """Test the simplified reference config view page."""
    
    def test_reference_view_loads(self, client):
        """Test that the reference view page loads successfully."""
        response = client.get('/reference/voron2.4/leviathan/rev_d')
        
        assert response.status_code == 200
        assert b'LDO Reference Config' in response.data
        assert b'Leviathan Rev D' in response.data
        assert b'reference-editor' in response.data
        assert b'Configuration Info' in response.data
        
    def test_reference_view_shows_error_for_invalid_config(self, client):
        """Test that the reference view shows error for invalid config."""
        response = client.get('/reference/invalid/invalid/invalid')
        
        assert response.status_code == 200
        assert b'Reference Config Not Found' in response.data
        
    def test_reference_view_has_download_button(self, client):
        """Test that the reference view has download functionality."""
        response = client.get('/reference/voron2.4/leviathan/rev_d')
        
        assert response.status_code == 200
        assert b'downloadConfig()' in response.data
        assert b'Download' in response.data
