"""
Ball Detector - Detector de Bola usando TrackNet

Wrapper moderno para o sistema de detecção de bola baseado em TrackNet.
Integra com a nova arquitetura orientada ao domínio.
"""

import cv2
import numpy as np
import queue
from typing import List, Optional, Tuple
import logging

from ..models.tracknet import trackNet


class BallDetector:
    """
    Detector de bola de tênis usando rede neural TrackNet.

    Detecta a posição da bola em frames de vídeo e mantém
    histórico de trajetória para análise.
    """

    def __init__(self, model_weights_path: str = 'WeightsTracknet/model.1',
                 input_width: int = 640, input_height: int = 360):
        """
        Inicializa o detector de bola.

        Args:
            model_weights_path: Caminho para os pesos do modelo TrackNet
            input_width: Largura de entrada do modelo
            input_height: Altura de entrada do modelo
        """
        self.logger = logging.getLogger(__name__)

        # Configurações do modelo
        self.input_width = input_width
        self.input_height = input_height
        self.n_classes = 256

        # Carregar modelo TrackNet
        try:
            self.model = trackNet(
                self.n_classes,
                input_height=input_height,
                input_width=input_width
            )
            self.model.compile(
                loss='categorical_crossentropy',
                optimizer='adadelta',
                metrics=['accuracy']
            )
            self.model.load_weights(model_weights_path)
            self.logger.info(f"Modelo TrackNet carregado: {model_weights_path}")
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo TrackNet: {e}")
            raise

        # Histórico de detecções para trajetória
        self.trajectory_queue = queue.deque(maxlen=8)
        self.detection_history: List[Optional[Tuple[float, float]]] = []

        # Configurações de detecção
        self.heatmap_threshold = 127
        self.min_radius = 2
        self.max_radius = 7
        self.confidence_threshold = 0.5

        # Estatísticas
        self.total_detections = 0
        self.successful_detections = 0

    def detect_ball(self, frame: np.ndarray, frame_width: int, frame_height: int) -> Optional[Tuple[float, float]]:
        """
        Detecta a posição da bola em um frame.

        Args:
            frame: Frame de entrada em formato BGR
            frame_width: Largura original do frame
            frame_height: Altura original do frame

        Returns:
            Tupla (x, y) com a posição da bola ou None se não detectada
        """
        self.total_detections += 1

        try:
            # Preparar imagem para o modelo
            processed_frame = self._preprocess_frame(frame)

            # Predição do modelo
            prediction = self.model.predict(np.array([processed_frame]))[0]

            # Processar saída do modelo
            heatmap = self._process_prediction(prediction)

            # Redimensionar heatmap para tamanho original
            heatmap_resized = cv2.resize(heatmap, (frame_width, frame_height))

            # Detectar círculos no heatmap
            ball_position = self._detect_circles(heatmap_resized)

            if ball_position:
                self.successful_detections += 1
                self.detection_history.append(ball_position)
                self.trajectory_queue.appendleft(ball_position)
            else:
                self.detection_history.append(None)
                self.trajectory_queue.appendleft(None)

            return ball_position

        except Exception as e:
            self.logger.error(f"Erro na detecção da bola: {e}")
            self.detection_history.append(None)
            self.trajectory_queue.appendleft(None)
            return None

    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocessa o frame para entrada no modelo.

        Args:
            frame: Frame original

        Returns:
            Frame preprocessado
        """
        # Redimensionar para tamanho esperado pelo modelo
        resized = cv2.resize(frame, (self.input_width, self.input_height))

        # Converter para float32
        processed = resized.astype(np.float32)

        # Reorganizar eixos para 'channels_first'
        processed = np.rollaxis(processed, 2, 0)

        return processed

    def _process_prediction(self, prediction: np.ndarray) -> np.ndarray:
        """
        Processa a predição do modelo em heatmap.

        Args:
            prediction: Saída do modelo

        Returns:
            Heatmap processado
        """
        # Reformatar para (height, width, classes)
        heatmap = prediction.reshape((self.input_height, self.input_width, self.n_classes))

        # Obter classe com maior probabilidade
        heatmap = heatmap.argmax(axis=2)

        # Converter para uint8
        heatmap = heatmap.astype(np.uint8)

        return heatmap

    def _detect_circles(self, heatmap: np.ndarray) -> Optional[Tuple[float, float]]:
        """
        Detecta círculos (bola) no heatmap.

        Args:
            heatmap: Heatmap da predição

        Returns:
            Posição da bola ou None
        """
        # Aplicar threshold binário
        _, binary_heatmap = cv2.threshold(
            heatmap,
            self.heatmap_threshold,
            255,
            cv2.THRESH_BINARY
        )

        # Detectar círculos usando Hough Transform
        circles = cv2.HoughCircles(
            binary_heatmap,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=1,
            param1=50,
            param2=2,
            minRadius=self.min_radius,
            maxRadius=self.max_radius
        )

        if circles is not None and len(circles[0]) == 1:
            # Uma bola detectada (caso ideal)
            x, y, radius = circles[0][0]
            return (float(x), float(y))

        return None

    def get_trajectory(self, length: int = 8) -> List[Optional[Tuple[float, float]]]:
        """
        Retorna a trajetória recente da bola.

        Args:
            length: Número de posições a retornar

        Returns:
            Lista com as últimas posições da bola
        """
        trajectory = list(self.trajectory_queue)[:length]
        # Preencher com None se necessário
        while len(trajectory) < length:
            trajectory.append(None)
        return trajectory

    def get_ball_speed(self, fps: float = 30.0) -> Optional[float]:
        """
        Calcula a velocidade da bola baseada nas duas últimas detecções.

        Args:
            fps: Taxa de quadros por segundo do vídeo

        Returns:
            Velocidade em pixels por segundo ou None
        """
        trajectory = list(self.trajectory_queue)

        if len(trajectory) < 2 or trajectory[0] is None or trajectory[1] is None:
            return None

        # Calcular distância entre as duas últimas posições
        pos1 = trajectory[0]
        pos2 = trajectory[1]

        distance = np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

        # Calcular velocidade (pixels por segundo)
        time_interval = 1.0 / fps
        speed = distance / time_interval

        return float(speed)

    def get_detection_confidence(self) -> float:
        """
        Retorna a taxa de confiança das detecções.

        Returns:
            Taxa de sucesso das detecções (0.0 a 1.0)
        """
        if self.total_detections == 0:
            return 0.0

        return self.successful_detections / self.total_detections

    def draw_trajectory(self, frame: np.ndarray, color: Tuple[int, int, int] = (0, 255, 255),
                       thickness: int = 2) -> np.ndarray:
        """
        Desenha a trajetória da bola no frame.

        Args:
            frame: Frame onde desenhar
            color: Cor da trajetória (BGR)
            thickness: Espessura da linha

        Returns:
            Frame com trajetória desenhada
        """
        result_frame = frame.copy()
        trajectory = list(self.trajectory_queue)

        # Desenhar círculos para cada posição válida
        for i, position in enumerate(trajectory):
            if position is not None:
                x, y = int(position[0]), int(position[1])
                radius = max(1, thickness - i // 2)  # Reduzir raio para posições mais antigas
                cv2.circle(result_frame, (x, y), radius, color, -1)

        return result_frame

    def reset(self):
        """Reset do detector para nova análise."""
        self.trajectory_queue.clear()
        self.detection_history.clear()
        self.total_detections = 0
        self.successful_detections = 0

    def get_statistics(self) -> dict:
        """
        Retorna estatísticas do detector.

        Returns:
            Dicionário com estatísticas
        """
        return {
            'total_detections': self.total_detections,
            'successful_detections': self.successful_detections,
            'detection_rate': self.get_detection_confidence(),
            'trajectory_length': len(self.trajectory_queue),
            'history_length': len(self.detection_history)
        }

    def __str__(self) -> str:
        return f"BallDetector(detections: {self.successful_detections}/{self.total_detections})"

    def __repr__(self) -> str:
        return self.__str__()