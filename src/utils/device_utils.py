"""
Utils - Funções Utilitárias para o Sistema de Rastreamento de Tênis

Este módulo contém funções auxiliares utilizadas em todo o sistema:
- Processamento de imagens e vídeos
- Configuração de dispositivos (CPU/GPU)
- Conversões de tipos de dados
- Funções matemáticas e geométricas

Author: Tennis Tracking Team
Version: 1.0
"""

import argparse
import cv2
import torch
import numpy as np


def crop_center(image):
    """
    Corta o centro de uma imagem para igualar altura e largura.

    Usado para padronizar dimensões de imagens mantendo o centro,
    útil para preprocessamento antes de redes neurais.

    Args:
        image (numpy.ndarray): Imagem de entrada

    Returns:
        numpy.ndarray: Imagem cortada no formato quadrado
    """
    # crop the center of an image and matching the height with the width of the image
    shape = image.shape[:-1]
    max_size_index = np.argmax(shape)
    diff1 = abs((shape[0] - shape[1]) // 2)
    diff2 = shape[max_size_index] - shape[1 - max_size_index] - diff1
    return image[:, diff1: -diff2] if max_size_index == 1 else image[diff1: -diff2, :]


def get_dtype():
    """
    Determina o tipo de tensor apropriado baseado na disponibilidade de GPU.

    Detecta automaticamente se CUDA está disponível e retorna o tipo
    de tensor correspondente para otimizar performance.

    Returns:
        torch.dtype: torch.cuda.FloatTensor se GPU disponível,
                    senão torch.FloatTensor para CPU
    """
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    device = torch.device(dev)
    if dev == 'cuda':
        dtype = torch.cuda.FloatTensor
    else:
        dtype = torch.FloatTensor
    print(f'Using device {device}')
    return dtype


def get_video_properties(video):
    """
    Extrai propriedades de um vídeo compatível com diferentes versões do OpenCV.

    Args:
        video (cv2.VideoCapture): Objeto de captura de vídeo

    Returns:
        tuple: (fps, length, width, height) do vídeo
            - fps (float): Frames por segundo
            - length (int): Número total de frames
            - width (int): Largura do frame
            - height (int): Altura do frame
    """
    # Detectar versão do OpenCV
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

    # Obter propriedades do vídeo
    if int(major_ver) < 3:
        # OpenCV 2.x
        fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
        length = int(video.get(cv2.cv.CAP_PROP_FRAME_COUNT))
        v_width = int(video.get(cv2.cv.CAP_PROP_FRAME_WIDTH))
        v_height = int(video.get(cv2.cv.CAP_PROP_FRAME_HEIGHT))
    else:
        # OpenCV 3.x+
        fps = video.get(cv2.CAP_PROP_FPS)
        length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        v_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        v_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return fps, length, v_width, v_height


def str2bool(v):
    """
    Converte string para valor booleano.

    Útil para parsing de argumentos de linha de comando.

    Args:
        v (str or bool): Valor a ser convertido

    Returns:
        bool: Valor booleano correspondente

    Raises:
        argparse.ArgumentTypeError: Se valor não for reconhecido como booleano
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_stickman_line_connection():
    """
    Retorna conexões de linhas para desenhar pose humana (stickman).

    Define quais keypoints devem ser conectados para formar uma
    representação esquelética da pose humana.

    Returns:
        list: Lista de tuplas (ponto1, ponto2) representando conexões
              entre keypoints para formar o esqueleto humano
    """
    # Conexões de linhas do stickman com índices de keypoints para R-CNN
    line_connection = [
        (7, 9), (7, 5), (10, 8), (8, 6), (6, 5), (15, 13), (13, 11),
        (11, 12), (12, 14), (14, 16), (5, 11), (12, 6)
    ]
    return line_connection
