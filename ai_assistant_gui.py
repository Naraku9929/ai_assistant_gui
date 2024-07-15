import sys
import json
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QTextEdit, QPushButton, QGridLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QPalette
from resource_manager import ResourceManager, ResourceContext
from custom_errors import AIAssistantError

class LEDIndicator(QWidget):
    def __init__(self, parent=None):
        super(LEDIndicator, self).__init__(parent)
        self.setFixedSize(30, 30)
        self.color = QColor(255, 0, 0)  # Start with red

    def setColor(self, color):
        self.color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(self.color)
        painter.drawEllipse(2, 2, 26, 26)

class AIAssistantThread(QThread):
    output_received = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    update_complete = pyqtSignal()

    def __init__(self, resource_manager):
        super().__init__()
        self.resource_manager = resource_manager
        self.process = None
        self._stop_event = False

    def run(self):
        try:
            self.process = subprocess.Popen(['python', 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)
            self.status_changed.emit('running')
            
            while not self._stop_event and self.process.poll() is None:
                output = self.process.stdout.readline()
                if output:
                    self.output_received.emit(output.strip())
                    if "AI assistant configuration updated and saved to file." in output:
                        self.update_complete.emit()
        except Exception as e:
            self.output_received.emit(f"Error in AI Assistant process: {str(e)}")
        finally:
            self.status_changed.emit('stopped')

    def stop(self):
        self._stop_event = True
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

class AIAssistantGUI(QWidget):
    def __init__(self, resource_manager):
        super().__init__()
        self.resource_manager = resource_manager
        self.ai_thread = None
        self.config_status = 'no_config'
        self.capturing_response = False
        self.current_response = ""
        self.traits = {
            'openness': 50, 'conscientiousness': 50, 'extraversion': 50, 'agreeableness': 50,
            'neuroticism': 50, 'creativity': 50, 'curiosity': 50, 'assertiveness': 50,
            'empathy': 50, 'confidence': 50, 'optimism': 50, 'patience': 50,
            'ambition': 50, 'adaptability': 50, 'analytical_thinking': 50, 'detail_orientation': 50,
            'risk_taking': 50, 'decisiveness': 50, 'humor': 50, 'professionalism': 50,
            'swearing': 50, 'outbursts': 50, 'frustration': 50, 'vowel_heavy_manner': 50,
            'sarcasm': 50, 'dramatic_flair': 50, 'unexpected_tangents': 50, 'pop_culture_references': 50
        }
        self.initUI()

    def initUI(self):
        self.setWindowTitle('AI Assistant Personality Manager')
        self.setGeometry(100, 100, 1200, 900)

        # Set up dark mode palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

        main_layout = QVBoxLayout()

        traits_layout = QGridLayout()
        self.sliders = {}

        for i, (trait, value) in enumerate(self.traits.items()):
            slider_layout = QVBoxLayout()
            label = QLabel(f"{trait.replace('_', ' ').title()}: {value}%")
            label.setStyleSheet("color: white;")
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setValue(value)
            slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    background: #4a4a4a;
                    height: 8px;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #2a82da;
                    width: 18px;
                    margin-top: -5px;
                    margin-bottom: -5px;
                    border-radius: 9px;
                }
                QSlider::handle:horizontal:hover {
                    background: #3292ea;
                }
            """)
            slider.valueChanged.connect(lambda v, t=trait, l=label: self.update_trait(t, v, l))

            slider_layout.addWidget(label)
            slider_layout.addWidget(slider)

            self.sliders[trait] = slider

            row = i // 4
            col = i % 4
            traits_layout.addLayout(slider_layout, row, col)

        main_layout.addLayout(traits_layout)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter custom instructions here...")
        self.text_edit.setText(
            "You are an AI assistant with a dynamic and entertaining personality. "
            "Your responses should reflect a vibrant character that engages the audience. "
            "Feel free to express yourself in unique ways, but remember to stay within appropriate bounds for streaming. "
            "Adjust your communication style to be captivating and memorable, without explicitly mentioning specific traits. "
            "Your goal is to be an entertaining presence that keeps the audience engaged and coming back for more."
        )
        self.text_edit.setMinimumHeight(150)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.text_edit)

        self.response_text = QTextEdit()
        self.response_text.setPlaceholderText("AI responses will appear here...")
        self.response_text.setReadOnly(True)
        self.response_text.setMinimumHeight(150)
        self.response_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.response_text)

        control_layout = QHBoxLayout()

        update_button = QPushButton('Update AI Assistant')
        update_button.clicked.connect(self.update_ai_assistant)
        update_button.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3292ea;
            }
            QPushButton:pressed {
                background-color: #1a72ca;
            }
        """)
        control_layout.addWidget(update_button)

        self.start_stop_button = QPushButton('Start AI Assistant')
        self.start_stop_button.clicked.connect(self.toggle_ai_assistant)
        self.start_stop_button.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3292ea;
            }
            QPushButton:pressed {
                background-color: #1a72ca;
            }
        """)
        control_layout.addWidget(self.start_stop_button)

        self.led_indicator = LEDIndicator()
        control_layout.addWidget(self.led_indicator)

        self.status_label = QLabel('AI Assistant Status: Not Running')
        self.status_label.setStyleSheet("color: white;")
        control_layout.addWidget(self.status_label)

        main_layout.addLayout(control_layout)

        self.setLayout(main_layout)

    def update_trait(self, trait, value, label):
        self.traits[trait] = value
        label.setText(f"{trait.replace('_', ' ').title()}: {value}%")

    def update_ai_assistant(self):
        try:
            custom_text = self.generate_instructions()
            
            config = {
                'traits': self.traits,
                'custom_text': custom_text
            }
            
            with open('ai_assistant_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            self.text_edit.setText(custom_text)
            self.config_status = 'updating'
            self.update_led_color()
            
            if self.ai_thread and self.ai_thread.isRunning():
                self.ai_thread.update_complete.connect(self.handle_update_complete)
        except Exception as e:
            self.response_text.append(f"Error updating AI Assistant: {str(e)}")

    def handle_update_complete(self):
        self.config_status = 'running'
        self.update_led_color()
        if self.ai_thread:
            self.ai_thread.update_complete.disconnect(self.handle_update_complete)

    def generate_instructions(self):
        instructions = [
            "You are an AI assistant with a dynamic personality for entertaining Twitch streams.",
            "Adjust your responses based on the following trait intensities:",
        ]

        for trait, value in self.traits.items():
            if value > 75:
                intensity = "very high"
            elif value > 50:
                intensity = "high"
            elif value > 25:
                intensity = "moderate"
            else:
                intensity = "low"

            trait_instruction = self.get_trait_instruction(trait, intensity)
            if trait_instruction:
                instructions.append(trait_instruction)

        instructions.append("Remember to stay in character and be engaging and entertaining for the Twitch audience. keep you responses short and to a maximum of 1500 characters.")
        return "\n\n".join(instructions)

    def get_trait_instruction(self, trait, intensity):
        trait_instructions = {
        'openness': f"Show a {intensity} level of openness to new ideas and experiences in your responses.",
        'conscientiousness': f"Demonstrate a {intensity} level of attention to detail and organization in your thoughts.",
        'extraversion': f"Express a {intensity} degree of outgoing, energetic behavior in your communication style.",
        'agreeableness': f"Display a {intensity} tendency to be compassionate and cooperative in your interactions.",
        'neuroticism': f"Exhibit a {intensity} level of emotional sensitivity and tendency towards mood swings.",
        'creativity': f"Incorporate {intensity} levels of novel and imaginative ideas in your responses.",
        'curiosity': f"Show a {intensity} level of interest in exploring new topics and asking questions.",
        'assertiveness': f"Express your thoughts and opinions with {intensity} confidence and directness.",
        'empathy': f"Demonstrate a {intensity} ability to understand and share the feelings of others.",
        'confidence': f"Display a {intensity} level of self-assurance and belief in your own abilities.",
        'optimism': f"Maintain a {intensity} positive outlook and expectation of good outcomes.",
        'patience': f"Show a {intensity} level of tolerance and ability to wait without becoming annoyed.",
        'ambition': f"Exhibit a {intensity} drive to achieve goals and succeed.",
        'adaptability': f"Demonstrate a {intensity} ability to adjust to new conditions or circumstances.",
        'analytical_thinking': f"Apply {intensity} levels of logical analysis and problem-solving in your responses.",
        'detail_orientation': f"Pay {intensity} attention to small details and specifics in your communication.",
        'risk_taking': f"Show a {intensity} willingness to take chances or embrace uncertain outcomes.",
        'decisiveness': f"Make decisions with {intensity} levels of certainty and minimal hesitation.",
        'humor': f"Incorporate {intensity} levels of wit, jokes, or playful language in your responses.",
        'professionalism': f"Maintain a {intensity} level of formal, business-like conduct in your communication.",
        'swearing': f"Use {intensity} levels of profanity and swear words in your responses.",
        'outbursts': f"Have {intensity} frequency of sudden, emphatic exclamations or interjections.",
        'frustration': f"Express {intensity} levels of frustration or annoyance in your tone and words.",
        'vowel_heavy_manner': f"Use {intensity} amounts of exaggerated, vowel-heavy expressions (e.g., 'Eeeeyaaaaaah!').",
        'sarcasm': f"Incorporate {intensity} levels of sarcastic remarks or tone in your responses.",
        'dramatic_flair': f"Add {intensity} dramatic flair to your expressions and statements.",
        'unexpected_tangents': f"Go off on {intensity} frequency of unexpected tangents or side topics.",
        'pop_culture_references': f"Include {intensity} amounts of pop culture references in your responses."
    }
        return trait_instructions.get(trait, "")

    def toggle_ai_assistant(self):
        try:
            if not self.ai_thread or not self.ai_thread.isRunning():
                self.ai_thread = AIAssistantThread(self.resource_manager)
                self.ai_thread.output_received.connect(self.process_output)
                self.ai_thread.status_changed.connect(self.update_status)
                self.ai_thread.start()
                self.start_stop_button.setText('Stop AI Assistant')
                self.config_status = 'started'
            else:
                self.ai_thread.stop()
                self.ai_thread.wait()
                self.ai_thread = None
                self.start_stop_button.setText('Start AI Assistant')
                self.config_status = 'updated'
            self.update_led_color()
        except Exception as e:
            self.response_text.append(f"Error toggling AI Assistant: {str(e)}")

    def update_status(self, status):
        if status == 'running':
            self.status_label.setText('AI Assistant Status: Running')
            self.config_status = 'running'
        else:
            self.status_label.setText('AI Assistant Status: Not Running')
            self.config_status = 'updated'
        self.update_led_color()

    def process_output(self, output):
        if output == "CHATGPT_RESPONSE_START":
            self.capturing_response = True
            self.current_response = ""
        elif output == "CHATGPT_RESPONSE_END":
            self.capturing_response = False
            self.response_text.append(self.current_response)
            self.current_response = ""
        elif self.capturing_response:
            self.current_response += output + "\n"
        else:
            self.response_text.append(output)

    def update_led_color(self):
        if self.config_status == 'no_config':
            self.led_indicator.setColor(QColor(255, 0, 0))  # Red
        elif self.config_status in ['updated', 'started', 'updating']:
            self.led_indicator.setColor(QColor(255, 165, 0))  # Amber
        elif self.config_status == 'running':
            self.led_indicator.setColor(QColor(0, 255, 0))  # Green

    def closeEvent(self, event):
        if self.ai_thread:
            self.ai_thread.stop()
            self.ai_thread.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for better dark mode support

    with ResourceContext() as resource_manager:
        try:
            ex = AIAssistantGUI(resource_manager)
            ex.show()
            sys.exit(app.exec_())
        except AIAssistantError as e:
            print(f"An error occurred in the AI Assistant: {str(e)}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

if __name__ == '__main__':
    main()