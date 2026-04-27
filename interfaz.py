import sys
import numpy as np
import pyaudio
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen

class InterfazAbril(QWidget):
    def __init__(self):
        super().__init__()
        
        # 1. Configuración de ventana (Transparente, sin bordes y siempre arriba)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(400, 400)
        
        # Centrar la interfaz en la pantalla
        # (Se ajustará automáticamente cuando la ejecutes)
        
        # 2. Variables de Animación J.A.R.V.I.S.
        self.volumen_actual = 0
        self.radio_base = 60
        
        # 3. Configuración del Micrófono (Los oídos)
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)
        
        # 4. Bucle de renderizado (30 Fotogramas por segundo)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_animacion)
        self.timer.start(30) # 30 milisegundos

    def actualizar_animacion(self):
        try:
            # Leer el micrófono en tiempo real
            data = np.frombuffer(self.stream.read(self.CHUNK, exception_on_overflow=False), dtype=np.int16)
            
            # Convertir a float32 para evitar desbordamiento (overflow) al elevar al cuadrado
            data_float = data.astype(np.float32)
            
            # Calcular la potencia del sonido (RMS)
            rms = np.sqrt(np.mean(np.square(data_float)))
            
            # Prevenir NaN
            if np.isnan(rms):
                rms = 0
                
            # Normalizar el volumen para que mueva los anillos de forma suave
            # (Si tu micrófono es muy sensible, aumenta el número 50)
            volumen_objetivo = min(rms / 50, 150) 
            
            # Suavizado matemático para que no tiemble bruscamente
            self.volumen_actual = (self.volumen_actual * 0.7) + (volumen_objetivo * 0.3)
        except Exception:
            pass
            
        self.update() # Forzar a PyQt5 a re-dibujar la pantalla

    def paintEvent(self, event):
        """Aquí ocurre la magia visual. Dibujamos los hologramas."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # Suavizar bordes
        
        centro_x = self.width() // 2
        centro_y = self.height() // 2
        
        # Paleta de colores A.B.R.I.L. (Cian Holográfico)
        color_neon = QColor(0, 255, 255, 180)
        color_nucleo = QColor(0, 200, 255, 220)
        color_tenue = QColor(0, 255, 255, 50)
        
        # DIBUJO 1: Núcleo central estático
        painter.setBrush(color_nucleo)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(centro_x - 40, centro_y - 40, 80, 80)
        
        # DIBUJO 2: Anillo exterior tecnológico (Línea punteada)
        painter.setBrush(Qt.NoBrush)
        pen_exterior = QPen(color_tenue, 3, Qt.DashLine)
        painter.setPen(pen_exterior)
        painter.drawEllipse(centro_x - 120, centro_y - 120, 240, 240)
        
        # DIBUJO 3: Anillo principal que reacciona a tu voz
        pen_dinamico = QPen(color_neon, 5)
        painter.setPen(pen_dinamico)
        radio_dinamico = int(self.radio_base + self.volumen_actual)
        painter.drawEllipse(centro_x - radio_dinamico, centro_y - radio_dinamico, radio_dinamico * 2, radio_dinamico * 2)
        
        # DIBUJO 4: Anillo de eco (Más grande y transparente al hablar fuerte)
        pen_eco = QPen(color_tenue, 10)
        painter.setPen(pen_eco)
        radio_eco = int(self.radio_base + (self.volumen_actual * 1.5))
        painter.drawEllipse(centro_x - radio_eco, centro_y - radio_eco, radio_eco * 2, radio_eco * 2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = InterfazAbril()
    ventana.show()
    print("🎙️ Interfaz iniciada. Habla por el micrófono para ver la reacción.")
    sys.exit(app.exec_())
