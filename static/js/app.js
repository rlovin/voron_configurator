// Voron Configurator - Single File Version

class VoronConfigurator {
    constructor() {
        this.editor = null;
        this.currentConfig = null;
        this.configContent = '';
        this.tabs = new Map();
        this.activeTab = 'main';
        this.tabCounter = 0;
        this.init();
    }

    async init() {
        await this.initAceEditor();
        this.setupEventListeners();
        this.updateInfoPanel();
    }

    async initAceEditor() {
        // Ace is loaded globally, no require needed
        ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.32.0/src-min-noconflict');
        ace.config.set('modePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.32.0/src-min-noconflict');
        ace.config.set('themePath', 'https://cdn.jsdelivr.net/npm/ace-builds@1.32.0/src-min-noconflict');
        
        // Define custom Klipper mode with VSCode-style syntax highlighting
        ace.define('ace/mode/klipper', ['require', 'exports', 'module', 'ace/lib/oop', 'ace/mode/text', 'ace/tokenizer', 'ace/mode/klipper_highlight_rules'], function(require, exports, module) {
            var oop = require('ace/lib/oop');
            var TextMode = require('ace/mode/text').Mode;
            var KlipperHighlightRules = require('ace/mode/klipper_highlight_rules').KlipperHighlightRules;
            
            var Mode = function() {
                this.HighlightRules = KlipperHighlightRules;
            };
            oop.inherits(Mode, TextMode);
            
            exports.Mode = Mode;
        });
        
        // Define Klipper mode with proper highlighting rules
        ace.define('ace/mode/klipper', function(require, exports, module) {
            var oop = require('ace/lib/oop');
            var TextMode = require('ace/mode/text').Mode;
            var TextHighlightRules = require('ace/mode/text_highlight_rules').TextHighlightRules;
            
            var KlipperHighlightRules = function() {
                this.$rules = {
                    'start': [
                        // 1. Comments (highest priority) - Green
                        {token: 'comment', regex: ';.*$'},
                        {token: 'comment', regex: '#.*$'},
                        
                        // 2. Section headers [name] - Blue brackets
                        {token: 'variable', regex: '\\[', next: 'in_section'},
                        
                        // 3. Include [include ...] - Magenta keyword
                        {token: 'keyword', regex: '\\[include\\b', next: 'in_include'},
                        
                        // 4. Key names - match identifier at start of line (handles both = and :)
                        {token: 'support.function', regex: '^\\s*([a-zA-Z_][a-zA-Z0-9_]*)(?=[\\s=:])', next: 'after_key'},
                        
                        // 5. Operators ! and ^ - Magenta
                        {token: 'keyword', regex: '[!\\^]'},
                        
                        // 6. Everything else as text
                        {token: 'text', regex: '\\s+'},
                        {defaultToken: 'text'}
                    ],
                    
                    'in_section': [
                        // Section name - Orange
                        {token: 'string', regex: '[^\\]]+', next: 'section_end'}
                    ],
                    
                    'section_end': [
                        // Closing bracket - Blue
                        {token: 'variable', regex: '\\]', next: 'start'}
                    ],
                    
                    'in_include': [
                        // Include path - Orange
                        {token: 'string', regex: '[^\\]]+', next: 'include_end'}
                    ],
                    
                    'include_end': [
                        // Closing bracket - Blue
                        {token: 'variable', regex: '\\]', next: 'start'}
                    ],
                    
                    'after_key': [
                        // Equals sign or colon - White
                        {token: 'keyword.operator', regex: '[=:]', next: 'value'}
                    ],
                    
                    'value': [
                        // Pin names (PA0, PB10, etc) - Yellow
                        {token: 'constant', regex: '\\b[A-Z][0-9]+\\b'},
                        
                        // Numbers (40, 16, 1.0) - Green
                        {token: 'constant.numeric', regex: '\\b\\d+\\.?\\d*\\b'},
                        
                        // Booleans - Magenta
                        {token: 'keyword', regex: '\\b(?:true|false|yes|no|on|off)\\b'},
                        
                        // Quoted strings - Orange
                        {token: 'string', regex: '"[^"]*"'},
                        {token: 'string', regex: "'[^']*'"},
                        
                        // Variable references {var} - Teal
                        {token: 'variable.parameter', regex: '\\{[^}]+\\}'},
                        
                        // G-code commands G1, M104 - Yellow
                        {token: 'function', regex: '\\b[GM][0-9]+\\b'},
                        
                        // Continue value or end
                        {token: 'text', regex: '\\s+'},
                        {token: 'text', regex: '$', next: 'start'},
                        {defaultToken: 'text'}
                    ]
                };
                
                this.normalizeRules();
            };
            
            oop.inherits(KlipperHighlightRules, TextHighlightRules);
            
            var KlipperMode = function() {
                this.HighlightRules = KlipperHighlightRules;
            };
            oop.inherits(KlipperMode, TextMode);
            
            exports.Mode = KlipperMode;
        });
        
        this.editor = ace.edit('monaco-editor');
        // Use tomorrow_night theme - matches Mainsail's dark theme (#1D1F21 vs #1e1e1e)
        this.editor.setTheme('ace/theme/tomorrow_night');
        // Use custom Klipper mode for VSCode-style syntax highlighting
        this.editor.session.setMode('ace/mode/klipper');
        
        this.editor.setOptions({
            fontSize: 14,
            fontFamily: 'JetBrains Mono, Consolas, monospace',
            showLineNumbers: true,
            showGutter: true,
            highlightActiveLine: true,
            highlightSelectedWord: true,
            enableBasicAutocompletion: true,
            enableLiveAutocompletion: false,
            enableSnippets: false,
            wrap: true,
            showPrintMargin: false,
            scrollPastEnd: false,
            readOnly: false,
            cursorStyle: 'ace',
            animatedScroll: true,
            displayIndentGuides: true,
            fadeFoldWidgets: false,
            showFoldWidgets: true,
            showInvisibles: false,
            behavioursEnabled: true,
        });
        
        this.editor.setValue('; Voron Configurator - Based on LDO Kit Configuration\n; Select options and click Generate to create your printer.cfg', -1);
        
        // Update cursor position on selection change
        this.editor.selection.on('changeCursor', () => {
            const cursor = this.editor.getCursorPosition();
            document.getElementById('cursor-position').textContent = 
                `Ln ${cursor.row + 1}, Col ${cursor.column + 1}`;
        });
        
        // Update file stats on change
        this.editor.on('change', () => {
            this.updateFileStats();
        });
    }

    setupEventListeners() {
        document.getElementById('theme-select').addEventListener('change', (e) => {
            this.changeTheme(e.target.value);
        });

        ['printer-select', 'size-select', 'main-board-select', 'toolhead-board-select', 'motors-select', 'extruder-select', 'probe-select']
            .forEach(id => {
                document.getElementById(id).addEventListener('change', () => {
                    this.updateInfoPanel();
                });
            });

        document.getElementById('better-macro-checkbox').addEventListener('change', () => {
            this.updateInfoPanel();
        });

        document.getElementById('generate-btn').addEventListener('click', () => {
            this.generateConfig();
        });

        document.getElementById('download-btn').addEventListener('click', () => {
            this.downloadConfig();
        });

        // LDO Reference Config handlers (independent of other selections)
        document.getElementById('ldo-ref-config-select').addEventListener('change', (e) => {
            this.onReferenceConfigChange(e.target.value);
        });

        document.getElementById('load-ref-config-btn').addEventListener('click', () => {
            this.loadReferenceConfig();
        });

        document.getElementById('open-ref-tab-btn').addEventListener('click', () => {
            this.openReferenceConfigInTab();
        });

        // Initialize reference config dropdown with all available configs
        this.updateReferenceConfigDropdown();
        
        // Setup tab event delegation
        this.setupTabEventListeners();
    }

    changeTheme(themeId) {
        document.body.dataset.theme = themeId;
        
        // Map app themes to Ace themes that match Mainsail's color scheme
        // Mainsail uses: bg #1e1e1e, primary #2196f3 (material blue)
        // tomorrow_night uses: bg #1D1F21 (very close match)
        const aceThemes = {
            'crimson': 'ace/theme/tomorrow_night',  // Dark blue-grey (closest to Mainsail)
            'forest': 'ace/theme/terminal',           // Dark green-black
            'nebula': 'ace/theme/tomorrow_night',   // Dark blue-grey
            'amber': 'ace/theme/ambiance',          // Dark warm
            'arctic': 'ace/theme/tomorrow_night',   // Dark blue-grey (default - matches Mainsail)
            'voron': 'ace/theme/tomorrow_night'     // Dark blue-grey
        };
        
        const theme = aceThemes[themeId] || 'ace/theme/tomorrow_night';
        if (this.editor) {
            this.editor.setTheme(theme);
        }
        
        // Also update reference tab editors
        this.tabs.forEach((tab) => {
            if (tab.editor) {
                tab.editor.setTheme(theme);
            }
        });
    }

    updateInfoPanel() {
        const printer = document.getElementById('printer-select').selectedOptions[0].text;
        const size = document.getElementById('size-select').value + 'mm';
        const mainBoard = document.getElementById('main-board-select').selectedOptions[0].text;
        const toolheadBoard = document.getElementById('toolhead-board-select').selectedOptions[0].text;
        const motors = document.getElementById('motors-select').selectedOptions[0].text;
        const extruder = document.getElementById('extruder-select').selectedOptions[0].text;
        const probe = document.getElementById('probe-select').selectedOptions[0].text;
        const betterMacro = document.getElementById('better-macro-checkbox').checked;

        document.getElementById('info-printer').textContent = printer;
        document.getElementById('info-size').textContent = size;
        document.getElementById('info-main-board').textContent = mainBoard;
        document.getElementById('info-toolhead').textContent = toolheadBoard;
        document.getElementById('info-motors').textContent = motors;
        document.getElementById('info-extruder').textContent = extruder;
        document.getElementById('info-probe').textContent = probe;
        document.getElementById('info-macros').textContent = betterMacro ? 'Better (Enhanced)' : 'Standard LDO';
    }

    async generateConfig() {
        this.setStatus('Generating configuration...', 'loading');
        
        const config = {
            printer: document.getElementById('printer-select').value,
            size: document.getElementById('size-select').value,
            main_board: document.getElementById('main-board-select').value,
            toolhead_board: document.getElementById('toolhead-board-select').value,
            motors: document.getElementById('motors-select').value,
            probe: document.getElementById('probe-select').value,
            print_start: document.getElementById('better-macro-checkbox').checked ? 'better' : 'standard'
        };

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const data = await response.json();

            if (data.success) {
                this.configContent = data.config;
                this.currentConfig = data;
                this.editor.setValue(this.configContent);
                this.updateFileStats();
                
                document.getElementById('download-btn').disabled = false;
                
                this.setStatus('Configuration generated successfully!', 'success');
                this.showMessage('Configuration generated!', 'success');
            } else {
                throw new Error('Failed to generate configuration');
            }
        } catch (error) {
            console.error('Error:', error);
            this.setStatus('Error generating configuration', 'error');
            this.showMessage('Error: ' + error.message, 'error');
        }
    }

    updateFileStats() {
        const content = this.editor.getValue();
        const lines = content.split('\n').length;
        const chars = content.length;
        
        document.getElementById('line-count').textContent = `${lines} lines`;
        document.getElementById('char-count').textContent = `${chars} chars`;
    }

    async downloadConfig() {
        if (!this.configContent) {
            this.showMessage('No configuration to download', 'error');
            return;
        }

        this.setStatus('Downloading configuration...', 'loading');

        try {
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    config: this.configContent,
                    filename: this.currentConfig?.filename || 'printer.cfg'
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'printer.cfg';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.setStatus('Configuration downloaded', 'success');
                this.showMessage('Configuration downloaded!', 'success');
            } else {
                throw new Error('Download failed');
            }
        } catch (error) {
            console.error('Error:', error);
            this.setStatus('Error downloading configuration', 'error');
            this.showMessage('Error: ' + error.message, 'error');
        }
    }

    setStatus(message, type) {
        const statusEl = document.getElementById('status-text');
        statusEl.textContent = message;
        
        if (type === 'loading') {
            statusEl.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${message}`;
        } else if (type === 'success') {
            statusEl.innerHTML = `<i class="fas fa-check"></i> ${message}`;
        } else if (type === 'error') {
            statusEl.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        }
    }

    showMessage(message, type) {
        document.querySelectorAll('.message').forEach(el => el.remove());
        
        const msgEl = document.createElement('div');
        msgEl.className = `message ${type}`;
        
        const icon = type === 'success' ? 'check-circle' : 'exclamation-circle';
        msgEl.innerHTML = `<i class="fas fa-${icon}"></i> ${message}`;
        
        document.body.appendChild(msgEl);
        
        setTimeout(() => {
            msgEl.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => msgEl.remove(), 300);
        }, 3000);
    }

    // LDO Reference Config Methods (independent of other UI selections)
    async updateReferenceConfigDropdown() {
        try {
            // Fetch ALL configs for both printer types
            const response = await fetch('/api/reference-configs');
            const data = await response.json();
            
            const select = document.getElementById('ldo-ref-config-select');
            const loadBtn = document.getElementById('load-ref-config-btn');
            
            // Clear existing options
            select.innerHTML = '<option value="">-- LDO Reference --</option>';
            
            if (data.success && Object.keys(data.configs).length > 0) {
                Object.entries(data.configs).forEach(([key, config]) => {
                    const option = document.createElement('option');
                    option.value = key;
                    option.textContent = config.name;
                    option.dataset.description = config.description;
                    option.dataset.printer = config.printer_type;
                    option.dataset.board = config.board_type;
                    option.dataset.revision = config.revision;
                    select.appendChild(option);
                });
                select.disabled = false;
            } else {
                select.innerHTML = '<option value="">No configs</option>';
                select.disabled = true;
                loadBtn.disabled = true;
            }
        } catch (error) {
            console.error('Error fetching reference configs:', error);
        }
    }

    onReferenceConfigChange(value) {
        const loadBtn = document.getElementById('load-ref-config-btn');
        const openTabBtn = document.getElementById('open-ref-tab-btn');
        
        if (value) {
            loadBtn.disabled = false;
            openTabBtn.disabled = false;
        } else {
            loadBtn.disabled = true;
            openTabBtn.disabled = true;
        }
    }

    async loadReferenceConfig() {
        const select = document.getElementById('ldo-ref-config-select');
        const selectedKey = select.value;
        
        if (!selectedKey) {
            this.showMessage('Please select a reference config', 'error');
            return;
        }
        
        // Extract printer, board and revision from the selected option's dataset
        const option = select.selectedOptions[0];
        const printer = option.dataset.printer;
        const board = option.dataset.board;
        const revision = option.dataset.revision;
        const configName = option.textContent;
        
        this.setStatus('Loading reference config...', 'loading');
        
        try {
            const response = await fetch(`/api/reference-config?printer=${printer}&board=${board}&revision=${revision}`);
            const data = await response.json();
            
            if (data.success) {
                this.configContent = data.content;
                this.currentConfig = {
                    filename: `ldo-reference-${printer}-${board}-${revision}.cfg`,
                    metadata: {
                        name: data.name,
                        description: data.description
                    }
                };
                
                // Switch to main tab and load content
                this.switchToTab('main');
                this.editor.setValue(this.configContent);
                this.updateFileStats();
                document.getElementById('download-btn').disabled = false;
                
                this.setStatus(`Loaded: ${configName}`, 'success');
                this.showMessage(`Loaded reference: ${configName}`, 'success');
            } else {
                throw new Error(data.error || 'Failed to load config');
            }
        } catch (error) {
            console.error('Error loading reference config:', error);
            this.setStatus('Error loading reference config', 'error');
            this.showMessage('Error: ' + error.message, 'error');
        }
    }

    async openReferenceConfigInTab() {
        const select = document.getElementById('ldo-ref-config-select');
        const selectedKey = select.value;
        
        if (!selectedKey) {
            this.showMessage('Please select a reference config', 'error');
            return;
        }
        
        // Extract config info from the selected option's dataset
        const option = select.selectedOptions[0];
        const printer = option.dataset.printer;
        const board = option.dataset.board;
        const revision = option.dataset.revision;
        const configName = option.textContent;
        
        console.log('Opening reference config:', { printer, board, revision, configName });
        this.setStatus('Opening reference config in new tab...', 'loading');
        
        try {
            const response = await fetch(`/api/reference-config?printer=${printer}&board=${board}&revision=${revision}`);
            const data = await response.json();
            
            console.log('API response:', data.success ? 'Success' : 'Failed');
            
            if (data.success) {
                // Create a new reference config tab with standardized name
                const tabId = this.createReferenceTab(configName, data.content, printer, board, revision);
                console.log('Created tab:', tabId);
                this.showMessage(`Opened ${configName} in new tab`, 'success');
            } else {
                throw new Error(data.error || 'Failed to load config');
            }
        } catch (error) {
            console.error('Error opening reference config in tab:', error);
            this.setStatus('Error opening config', 'error');
            this.showMessage('Error: ' + error.message, 'error');
        }
    }

    async generateConfigFromReference(tabId) {
        const tab = this.tabs.get(tabId);
        if (!tab || !tab.isReference) {
            this.showMessage('No reference config found in this tab', 'error');
            return;
        }
        
        this.setStatus('Generating customized config...', 'loading');
        
        try {
            // Use the reference config as base and apply current selections
            const config = {
                printer: tab.printer,
                size: document.getElementById('size-select').value,
                main_board: tab.board,
                toolhead_board: document.getElementById('toolhead-board-select').value,
                motors: document.getElementById('motors-select').value,
                probe: document.getElementById('probe-select').value,
                print_start: document.getElementById('better-macro-checkbox').checked ? 'better' : 'standard'
            };

            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const data = await response.json();

            if (data.success) {
                // Switch to main tab and show the generated config
                this.switchToTab('main');
                this.editor.setValue(data.config);
                this.configContent = data.config;
                this.currentConfig = data;
                this.updateFileStats();
                
                document.getElementById('download-btn').disabled = false;
                
                this.setStatus('Generated customized config', 'success');
                this.showMessage(`Generated config for ${tab.printer} ${tab.board}!`, 'success');
            } else {
                throw new Error('Failed to generate configuration');
            }
        } catch (error) {
            console.error('Error:', error);
            this.setStatus('Error generating configuration', 'error');
            this.showMessage('Error: ' + error.message, 'error');
        }
    }

    // Tab Management Methods
    setupTabEventListeners() {
        const tabsContainer = document.querySelector('.editor-tabs');
        
        tabsContainer.addEventListener('click', (e) => {
            const tab = e.target.closest('.tab');
            if (!tab) return;
            
            const tabId = tab.dataset.tab;
            
            // Check if close button was clicked
            if (e.target.closest('.tab-close')) {
                e.stopPropagation();
                this.closeTab(tabId);
                return;
            }
            
            // Switch to clicked tab
            this.switchToTab(tabId);
        });
    }

    createReferenceTab(fullName, content, printer, board, revision) {
        this.tabCounter++;
        const tabId = `tab-${this.tabCounter}`;
        const tabName = 'ldo_ref_printer.cfg';
        
        // Store tab data with reference flag
        this.tabs.set(tabId, {
            name: tabName,
            fullName: fullName,
            content: content,
            filename: 'ldo_ref_printer.cfg',
            isReference: true,
            printer: printer,
            board: board,
            revision: revision
        });
        
        // Create tab element with reference indicator
        const tabsContainer = document.querySelector('.editor-tabs');
        const tabElement = document.createElement('div');
        tabElement.className = 'tab reference-tab';
        tabElement.dataset.tab = tabId;
        tabElement.innerHTML = `
            <i class="fas fa-book"></i>
            <span title="${fullName}">${tabName}</span>
            <button class="tab-close"><i class="fas fa-times"></i></button>
        `;
        tabsContainer.appendChild(tabElement);
        
        // Create editor container for this tab with generate button
        const editorContent = document.querySelector('.editor-content');
        const editorWrapper = document.createElement('div');
        editorWrapper.id = `editor-${tabId}`;
        editorWrapper.className = 'tab-content reference-tab-content';
        editorWrapper.dataset.tab = tabId;
        editorWrapper.style.display = 'none';
        
        // Create toolbar with generate button
        const toolbarDiv = document.createElement('div');
        toolbarDiv.className = 'reference-toolbar';
        toolbarDiv.innerHTML = `
            <div class="reference-info">
                <i class="fas fa-info-circle"></i>
                <span>${fullName}</span>
            </div>
            <button class="btn btn-primary btn-sm generate-from-ref-btn" data-tab="${tabId}">
                <i class="fas fa-magic"></i>
                Generate Config
            </button>
        `;
        
        const editorDiv = document.createElement('div');
        editorDiv.className = 'reference-editor';
        editorDiv.style.width = '100%';
        editorDiv.style.height = 'calc(100% - 40px)';
        
        editorWrapper.appendChild(toolbarDiv);
        editorWrapper.appendChild(editorDiv);
        editorContent.appendChild(editorWrapper);
        
        // Add generate button event listener
        toolbarDiv.querySelector('.generate-from-ref-btn').addEventListener('click', () => {
            this.generateConfigFromReference(tabId);
        });
        
        // First make the tab visible, then create the editor
        // This ensures Ace gets proper dimensions
        this.switchToTab(tabId);
        
        // Initialize Ace editor for this tab
        const tabEditor = ace.edit(editorDiv);
        // Use tomorrow_night theme to match Mainsail
        tabEditor.setTheme('ace/theme/tomorrow_night');
        // Use custom Klipper mode for VSCode-style syntax highlighting
        tabEditor.session.setMode('ace/mode/klipper');
        
        tabEditor.setOptions({
            fontSize: 14,
            fontFamily: 'JetBrains Mono, Consolas, monospace',
            showLineNumbers: true,
            showGutter: true,
            highlightActiveLine: true,
            highlightSelectedWord: true,
            wrap: true,
            showPrintMargin: false,
            scrollPastEnd: false,
            readOnly: false,
        });
        
        tabEditor.setValue(content, -1);
        
        // Store editor instance
        this.tabs.get(tabId).editor = tabEditor;
        
        return tabId;
    }

    switchToTab(tabId) {
        // Deactivate current tab
        document.querySelectorAll('.tab.active').forEach(tab => tab.classList.remove('active'));
        document.querySelectorAll('.tab-content.active').forEach(content => {
            content.classList.remove('active');
            content.style.display = 'none';
        });
        
        // Activate new tab
        const tabElement = document.querySelector(`.tab[data-tab="${tabId}"]`);
        if (tabElement) {
            tabElement.classList.add('active');
        }
        
        const contentElement = document.querySelector(`.tab-content[data-tab="${tabId}"]`) || 
                               document.getElementById(`editor-${tabId}`);
        if (contentElement) {
            contentElement.classList.add('active');
            contentElement.style.display = 'block';
        }
        
        this.activeTab = tabId;
        
        // Update current editor reference
        if (tabId === 'main') {
            this.editor = this.editor; // main editor stays the same
        } else if (this.tabs.has(tabId)) {
            this.editor = this.tabs.get(tabId).editor;
        }
        
        // Update stats
        this.updateFileStats();
    }

    closeTab(tabId) {
        if (tabId === 'main') return; // Can't close main tab
        
        const tab = this.tabs.get(tabId);
        if (tab && tab.editor) {
            // Ace uses destroy()
            tab.editor.destroy();
        }
        
        this.tabs.delete(tabId);
        
        // Remove tab element
        const tabElement = document.querySelector(`.tab[data-tab="${tabId}"]`);
        if (tabElement) tabElement.remove();
        
        // Remove editor element
        const editorElement = document.getElementById(`editor-${tabId}`);
        if (editorElement) editorElement.remove();
        
        // Switch to main tab if this was the active tab
        if (this.activeTab === tabId) {
            this.switchToTab('main');
        }
    }

    getActiveTabContent() {
        if (this.activeTab === 'main') {
            return this.editor.getValue();
        } else if (this.tabs.has(this.activeTab)) {
            return this.tabs.get(this.activeTab).editor.getValue();
        }
        return '';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.configurator = new VoronConfigurator();
});
