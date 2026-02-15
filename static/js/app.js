// Voron Configurator - Ace Editor Version

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
        ace.require("ace/ext/language_tools");
        
        this.editor = ace.edit("ace-editor");
        // Use Mainsail theme - matches actual Mainsail editor colors
        this.editor.setTheme("ace/theme/mainsail");
        // Use custom Klipper mode for VSCode-style syntax highlighting
        this.editor.session.setMode("ace/mode/klipper");
        
        this.editor.setOptions({
            enableBasicAutocompletion: true,
            enableLiveAutocompletion: false,
            enableSnippets: true,
            showPrintMargin: false,
            highlightActiveLine: true,
            highlightSelectedWord: true,
            behavioursEnabled: true,
            wrapBehavioursEnabled: true,
            autoScrollEditorIntoView: true,
            copyWithEmptySelection: true,
            useSoftTabs: true,
            navigateWithinSoftTabs: true,
            tabSize: 4,
            useWorker: false
        });
        
        this.editor.setValue('; Voron Configurator - Based on LDO Kit Configuration\n; Select options and click Generate to create your printer.cfg', -1);
        
        // Set up cursor position tracking
        this.editor.selection.on('changeCursor', () => {
            const cursor = this.editor.selection.getCursor();
            document.getElementById('cursor-position').textContent = 
                `Ln ${cursor.row + 1}, Col ${cursor.column + 1}`;
        });
        
        // Set up change listener for file stats
        this.editor.session.on('change', () => {
            this.updateFileStats();
        });
        
        this.updateFileStats();
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

        // Setup tab event delegation
        this.setupTabEventListeners();
    }

    changeTheme(themeId) {
        document.body.dataset.theme = themeId;
        
        const themeMap = {
            'crimson': 'mainsail',
            'forest': 'mainsail',
            'nebula': 'mainsail',
            'amber': 'mainsail',
            'arctic': 'mainsail',
            'voron': 'mainsail'
        };
        
        const aceTheme = themeMap[themeId] || 'mainsail';
        this.editor.setTheme(`ace/theme/${aceTheme}`);
        
        // Also update theme for all tab editors
        this.tabs.forEach(tab => {
            if (tab.editor) {
                tab.editor.setTheme(`ace/theme/${aceTheme}`);
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
                this.editor.setValue(this.configContent, -1);
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
        const editor = this.activeTab === 'main' ? this.editor : 
                      (this.tabs.has(this.activeTab) ? this.tabs.get(this.activeTab).editor : null);
        
        if (!editor) return;
        
        const content = editor.getValue();
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
                this.editor.setValue(data.config, -1);
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
        editorDiv.id = `ace-editor-${tabId}`;
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
        // This ensures the editor gets proper dimensions
        this.switchToTab(tabId);
        
        // Initialize Ace editor for this tab
        const tabEditor = ace.edit(`ace-editor-${tabId}`);
        tabEditor.setTheme("ace/theme/mainsail");
        tabEditor.session.setMode("ace/mode/klipper");
        
        tabEditor.setOptions({
            enableBasicAutocompletion: true,
            enableLiveAutocompletion: false,
            enableSnippets: true,
            showPrintMargin: false,
            highlightActiveLine: true,
            readOnly: false,
            tabSize: 4,
            useSoftTabs: true,
            useWorker: false
        });
        
        tabEditor.setValue(content, -1);
        
        // Set up cursor position tracking
        tabEditor.selection.on('changeCursor', () => {
            const cursor = tabEditor.selection.getCursor();
            document.getElementById('cursor-position').textContent = 
                `Ln ${cursor.row + 1}, Col ${cursor.column + 1}`;
        });
        
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
        
        // Update current editor reference and resize
        if (tabId === 'main') {
            this.editor.resize();
        } else if (this.tabs.has(tabId)) {
            const tabEditor = this.tabs.get(tabId).editor;
            if (tabEditor) {
                tabEditor.resize();
            }
        }
        
        // Update stats
        this.updateFileStats();
    }

    closeTab(tabId) {
        if (tabId === 'main') return; // Can't close main tab
        
        const tab = this.tabs.get(tabId);
        if (tab && tab.editor) {
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
