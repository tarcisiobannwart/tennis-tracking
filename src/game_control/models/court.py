"""
Court Model - Modelo de Quadra

Define a estrutura de dados para representar uma quadra de tênis,
incluindo dimensões oficiais, linhas e conversões de coordenadas.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import numpy as np


class CourtType(Enum):
    """Tipos de superfície da quadra"""
    HARD = "hard"
    CLAY = "clay"
    GRASS = "grass"
    CARPET = "carpet"


class CourtSize(Enum):
    """Tamanhos de quadra"""
    SINGLES = "singles"
    DOUBLES = "doubles"


@dataclass
class CourtDimensions:
    """Dimensões oficiais da quadra de tênis (em metros)"""

    # Dimensões básicas (ATP/ITF official)
    total_length: float = 23.77  # Comprimento total
    total_width_singles: float = 8.23  # Largura para simples
    total_width_doubles: float = 10.97  # Largura para duplas

    # Áreas de saque
    service_box_length: float = 6.40  # Comprimento da área de saque
    service_box_width: float = 4.115  # Largura da área de saque

    # Linhas
    baseline_to_service_line: float = 5.485  # Distância da linha de base ao saque
    net_height_center: float = 0.914  # Altura da rede no centro
    net_height_posts: float = 1.07  # Altura da rede nos postes

    # Margens
    back_margin: float = 6.40  # Margem atrás da linha de base
    side_margin: float = 3.66  # Margem lateral


@dataclass
class CourtLine:
    """Representa uma linha da quadra"""
    name: str
    start_point: Tuple[float, float]  # (x, y) em metros
    end_point: Tuple[float, float]    # (x, y) em metros
    pixel_coords: Optional[Tuple[int, int, int, int]] = None  # (x1, y1, x2, y2) em pixels


@dataclass
class Court:
    """
    Modelo completo de uma quadra de tênis.

    Contém todas as informações sobre a quadra, incluindo dimensões,
    linhas, transformações de perspectiva e métodos de conversão.
    """

    # Identificação e tipo
    court_id: str = "default"
    court_type: CourtType = CourtType.HARD
    court_size: CourtSize = CourtSize.SINGLES

    # Dimensões
    dimensions: CourtDimensions = field(default_factory=CourtDimensions)

    # Transformações de perspectiva
    homography_matrix: Optional[np.ndarray] = None
    inverse_homography: Optional[np.ndarray] = None

    # Linhas da quadra (em coordenadas de imagem)
    lines: Dict[str, CourtLine] = field(default_factory=dict)

    # Pontos de referência importantes (em pixels)
    reference_points: Dict[str, Tuple[int, int]] = field(default_factory=dict)

    # Configurações de visualização
    line_color: Tuple[int, int, int] = (255, 255, 255)  # Cor das linhas (BGR)
    line_thickness: int = 2

    def __post_init__(self):
        """Inicializa as linhas padrão da quadra"""
        if not self.lines:
            self._initialize_court_lines()

    def _initialize_court_lines(self):
        """Inicializa as linhas padrão da quadra em coordenadas reais"""
        width = (self.dimensions.total_width_singles if self.court_size == CourtSize.SINGLES
                else self.dimensions.total_width_doubles)

        length = self.dimensions.total_length
        service_length = self.dimensions.service_box_length

        # Linhas de base
        self.lines["baseline_top"] = CourtLine(
            "baseline_top",
            (0, 0),
            (width, 0)
        )

        self.lines["baseline_bottom"] = CourtLine(
            "baseline_bottom",
            (0, length),
            (width, length)
        )

        # Linhas de saque
        self.lines["service_line_top"] = CourtLine(
            "service_line_top",
            (0, self.dimensions.baseline_to_service_line),
            (width, self.dimensions.baseline_to_service_line)
        )

        self.lines["service_line_bottom"] = CourtLine(
            "service_line_bottom",
            (0, length - self.dimensions.baseline_to_service_line),
            (width, length - self.dimensions.baseline_to_service_line)
        )

        # Rede (linha central)
        self.lines["net"] = CourtLine(
            "net",
            (0, length / 2),
            (width, length / 2)
        )

        # Linhas laterais
        self.lines["left_sideline"] = CourtLine(
            "left_sideline",
            (0, 0),
            (0, length)
        )

        self.lines["right_sideline"] = CourtLine(
            "right_sideline",
            (width, 0),
            (width, length)
        )

        # Linha central de saque
        self.lines["center_service_line"] = CourtLine(
            "center_service_line",
            (width / 2, self.dimensions.baseline_to_service_line),
            (width / 2, length - self.dimensions.baseline_to_service_line)
        )

    def set_homography_matrix(self, matrix: np.ndarray):
        """
        Define a matriz de homografia para conversão de coordenadas.

        Args:
            matrix: Matriz de homografia 3x3
        """
        self.homography_matrix = matrix
        # Calcular matriz inversa
        if matrix is not None:
            self.inverse_homography = np.linalg.inv(matrix)

    def update_line_pixels(self, line_name: str, pixel_coords: Tuple[int, int, int, int]):
        """
        Atualiza as coordenadas em pixels de uma linha.

        Args:
            line_name: Nome da linha
            pixel_coords: Coordenadas em pixels (x1, y1, x2, y2)
        """
        if line_name in self.lines:
            self.lines[line_name].pixel_coords = pixel_coords

    def pixel_to_court_coords(self, x: int, y: int) -> Optional[Tuple[float, float]]:
        """
        Converte coordenadas de pixel para coordenadas reais da quadra.

        Args:
            x: Coordenada X em pixels
            y: Coordenada Y em pixels

        Returns:
            Tupla (x, y) em metros ou None se não houver homografia
        """
        if self.inverse_homography is None:
            return None

        # Criar ponto homogêneo
        pixel_point = np.array([x, y, 1])

        # Aplicar transformação inversa
        court_point = self.inverse_homography @ pixel_point

        # Normalizar
        if court_point[2] != 0:
            court_x = court_point[0] / court_point[2]
            court_y = court_point[1] / court_point[2]
            return (court_x, court_y)

        return None

    def court_to_pixel_coords(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        """
        Converte coordenadas reais da quadra para pixels.

        Args:
            x: Coordenada X em metros
            y: Coordenada Y em metros

        Returns:
            Tupla (x, y) em pixels ou None se não houver homografia
        """
        if self.homography_matrix is None:
            return None

        # Criar ponto homogêneo
        court_point = np.array([x, y, 1])

        # Aplicar transformação
        pixel_point = self.homography_matrix @ court_point

        # Normalizar
        if pixel_point[2] != 0:
            pixel_x = int(pixel_point[0] / pixel_point[2])
            pixel_y = int(pixel_point[1] / pixel_point[2])
            return (pixel_x, pixel_y)

        return None

    def is_ball_in_court(self, x: float, y: float) -> bool:
        """
        Verifica se uma coordenada (em metros) está dentro da quadra.

        Args:
            x: Coordenada X em metros
            y: Coordenada Y em metros

        Returns:
            True se estiver dentro da quadra
        """
        width = (self.dimensions.total_width_singles if self.court_size == CourtSize.SINGLES
                else self.dimensions.total_width_doubles)

        return (0 <= x <= width and
                0 <= y <= self.dimensions.total_length)

    def get_service_box(self, player_side: str, service_side: str) -> Dict[str, float]:
        """
        Retorna as coordenadas de uma área de saque específica.

        Args:
            player_side: "top" ou "bottom"
            service_side: "left" ou "right"

        Returns:
            Dicionário com as coordenadas da área de saque
        """
        width = (self.dimensions.total_width_singles if self.court_size == CourtSize.SINGLES
                else self.dimensions.total_width_doubles)

        service_width = self.dimensions.service_box_width
        center_x = width / 2

        if player_side == "top":
            y_start = self.dimensions.baseline_to_service_line
            y_end = self.dimensions.total_length / 2
        else:  # bottom
            y_start = self.dimensions.total_length / 2
            y_end = self.dimensions.total_length - self.dimensions.baseline_to_service_line

        if service_side == "left":
            x_start = center_x - service_width
            x_end = center_x
        else:  # right
            x_start = center_x
            x_end = center_x + service_width

        return {
            'x_min': x_start,
            'x_max': x_end,
            'y_min': y_start,
            'y_max': y_end
        }

    def get_court_regions(self) -> Dict[str, Dict[str, float]]:
        """
        Retorna todas as regiões importantes da quadra.

        Returns:
            Dicionário com todas as regiões da quadra
        """
        regions = {}

        # Áreas de saque
        regions['service_box_top_left'] = self.get_service_box("top", "left")
        regions['service_box_top_right'] = self.get_service_box("top", "right")
        regions['service_box_bottom_left'] = self.get_service_box("bottom", "left")
        regions['service_box_bottom_right'] = self.get_service_box("bottom", "right")

        # Áreas de fundo
        width = (self.dimensions.total_width_singles if self.court_size == CourtSize.SINGLES
                else self.dimensions.total_width_doubles)

        regions['backcourt_top'] = {
            'x_min': 0,
            'x_max': width,
            'y_min': 0,
            'y_max': self.dimensions.baseline_to_service_line
        }

        regions['backcourt_bottom'] = {
            'x_min': 0,
            'x_max': width,
            'y_min': self.dimensions.total_length - self.dimensions.baseline_to_service_line,
            'y_max': self.dimensions.total_length
        }

        return regions

    def to_dict(self) -> Dict:
        """
        Converte a quadra para um dicionário.

        Returns:
            Dicionário com todos os dados da quadra
        """
        return {
            'court_id': self.court_id,
            'court_type': self.court_type.value,
            'court_size': self.court_size.value,
            'dimensions': {
                'total_length': self.dimensions.total_length,
                'total_width_singles': self.dimensions.total_width_singles,
                'total_width_doubles': self.dimensions.total_width_doubles
            },
            'lines': {
                name: {
                    'start_point': line.start_point,
                    'end_point': line.end_point,
                    'pixel_coords': line.pixel_coords
                }
                for name, line in self.lines.items()
            }
        }

    def __str__(self) -> str:
        return f"Court({self.court_id}, {self.court_type.value}, {self.court_size.value})"

    def __repr__(self) -> str:
        return self.__str__()