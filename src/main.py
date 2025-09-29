"""
Tennis Tracking - Sistema de Rastreamento de Tênis

Este módulo implementa um sistema completo de análise de vídeos de tênis que:
- Rastreia a posição da bola usando rede neural TrackNet
- Detecta e rastreia linhas da quadra
- Identifica e rastreia jogadores
- Prediz pontos de quique da bola
- Gera visualizações com minimapa da quadra

Utiliza modelos de deep learning (TrackNet, YOLO, Faster R-CNN) para análise
em tempo real de partidas de tênis.

Author: Tennis Tracking Team
Version: 1.0
"""

import argparse
import queue
import pandas as pd
import pickle
import imutils
import os
from PIL import Image, ImageDraw
import cv2
import numpy as np
import torch
import sys
import time

from sktime.datatypes._panel._convert import from_2d_array_to_nested
from court_detector import CourtDetector
from Models.tracknet import trackNet
from TrackPlayers.trackplayers import *
from utils import get_video_properties, get_dtype
from detection import *
from pickle import load


# Configuração de argumentos de linha de comando
parser = argparse.ArgumentParser(description='Sistema de Rastreamento de Tênis')

parser.add_argument("--input_video_path", type=str,
                   help="Caminho para o vídeo de entrada")
parser.add_argument("--output_video_path", type=str, default="",
                   help="Caminho para o vídeo de saída (padrão: pasta VideoOutput)")
parser.add_argument("--minimap", type=int, default=0,
                   help="Gerar minimapa da quadra (1=sim, 0=não)")
parser.add_argument("--bounce", type=int, default=0,
                   help="Detectar pontos de quique (1=sim, 0=não)")

args = parser.parse_args()

# Extração dos parâmetros
input_video_path = args.input_video_path
output_video_path = args.output_video_path
minimap = args.minimap
bounce = args.bounce

# Configurações dos modelos
n_classes = 256  # Número de classes para o TrackNet (mapa de calor de 256 intensidades)
save_weights_path = 'WeightsTracknet/model.1'  # Pesos pré-treinados do TrackNet
yolo_classes = 'Yolov3/yolov3.txt'  # Classes do YOLO para detecção de objetos
yolo_weights = 'Yolov3/yolov3.weights'  # Pesos pré-treinados do YOLOv3
yolo_config = 'Yolov3/yolov3.cfg'  # Configuração da arquitetura YOLOv3

# Definir caminho de saída padrão se não especificado
if output_video_path == "":
    # Vídeo de saída no mesmo diretório do vídeo de entrada
    output_video_path = input_video_path.split('.')[0] + "VideoOutput/video_output.mp4"

# Obter propriedades do vídeo (FPS e dimensões)
video = cv2.VideoCapture(input_video_path)
fps = int(video.get(cv2.CAP_PROP_FPS))
print('fps : {}'.format(fps))
output_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
output_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Determinar o número total de frames no arquivo de vídeo
if imutils.is_cv2() is True:
    prop = cv2.cv.CV_CAP_PROP_FRAME_COUNT
else:
    prop = cv2.CAP_PROP_FRAME_COUNT
total = int(video.get(prop))

# Iniciar do primeiro frame
currentFrame = 0

# Dimensões para o TrackNet (resolução fixa para melhor performance)
width, height = 640, 360
img, img1, img2 = None, None, None

# Carregar modelo TrackNet
modelFN = trackNet
m = modelFN(n_classes, input_height=height, input_width=width)
m.compile(loss='categorical_crossentropy', optimizer='adadelta', metrics=['accuracy'])
m.load_weights(save_weights_path)

# Para desenhar a trajetória da bola, salvamos as coordenadas dos 7 frames anteriores
q = queue.deque()
for i in range(0, 8):
    q.appendleft(None)

# Configurar gravação do vídeo de saída
fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_video = cv2.VideoWriter(output_video_path, fourcc, fps, (output_width, output_height))

# Carregar classes do YOLOv3
LABELS = open(yolo_classes).read().strip().split("\n")
# Rede neural YOLOv3
net = cv2.dnn.readNet(yolo_weights, yolo_config)

# Detector de quadra
court_detector = CourtDetector()

# Rastreador de jogadores
dtype = get_dtype()
detection_model = DetectionModel(dtype=dtype)

# Obter propriedades do vídeo
fps, length, v_width, v_height = get_video_properties(video)

# Inicialização de variáveis para armazenar dados de rastreamento
coords = []  # Coordenadas da bola detectadas
frame_i = 0  # Índice do frame atual
frames = []  # Lista para armazenar frames processados
t = []  # Tempos de processamento

# PRIMEIRA PASSADA: Detecção inicial de quadra e jogadores
print('Iniciando primeira passada: detecção de quadra e jogadores...')
while True:
    ret, frame = video.read()
    frame_i += 1

    if ret:
        # No primeiro frame, detectar a quadra completa
        if frame_i == 1:
            print('Detectando a quadra e os jogadores...')
            lines = court_detector.detect(frame)
        else:
            # Nos frames subsequentes, apenas rastrear a quadra detectada
            lines = court_detector.track_court(frame)

        # Detectar jogadores em relação à quadra
        detection_model.detect_player_1(frame, court_detector)
        detection_model.detect_top_persons(frame, court_detector, frame_i)

        # Desenhar linhas da quadra detectadas no frame
        for i in range(0, len(lines), 4):
            x1, y1, x2, y2 = lines[i], lines[i+1], lines[i+2], lines[i+3]
            cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 5)

        # Redimensionar frame para tamanho de saída e armazenar
        new_frame = cv2.resize(frame, (v_width, v_height))
        frames.append(new_frame)
    else:
        break

video.release()
print('Primeira passada concluída!')

# Identificar segundo jogador baseado nos dados coletados
detection_model.find_player_2_box()

# SEGUNDA PASSADA: Rastreamento da bola usando TrackNet
player1_boxes = detection_model.player_1_boxes
player2_boxes = detection_model.player_2_boxes

video = cv2.VideoCapture(input_video_path)
frame_i = 0

last = time.time()  # Iniciar contagem de tempo
print('Iniciando segunda passada: rastreamento da bola...')

# Processar cada frame para detectar a posição da bola
for img in frames:
    print('Rastreando a bola: {}%'.format(round((currentFrame / total) * 100, 2)))
    frame_i += 1

    # Preparar imagem para detecção da bola
    # img é o frame que o TrackNet usará para predizer a posição
    # Como precisamos alterar o tamanho e tipo da img, copiamos para output_img
    output_img = img

    # Redimensionar para tamanho esperado pelo TrackNet
    img = cv2.resize(img, (width, height))
    # Entrada deve ser do tipo float
    img = img.astype(np.float32)

    # O TrackNet usa ordenação 'channels_first', então mudamos os eixos
    X = np.rollaxis(img, 2, 0)
    # Predizer mapa de calor
    pr = m.predict(np.array([X]))[0]

    # A saída do TrackNet é (net_output_height*model_output_width, n_classes)
    # então reformatamos como (net_output_height, model_output_width, n_classes(profundidade))
    pr = pr.reshape((height, width, n_classes)).argmax(axis=2)

    # Imagem cv2 deve ser numpy.uint8, converter numpy.int64 para numpy.uint8
    pr = pr.astype(np.uint8)

    # Redimensionar de volta para o tamanho original da imagem
    heatmap = cv2.resize(pr, (output_width, output_height))

    # Converter mapa de calor em imagem binária usando threshold
    ret, heatmap = cv2.threshold(heatmap, 127, 255, cv2.THRESH_BINARY)

    # Encontrar círculos na imagem com raio entre 2 e 7 pixels (tamanho típico da bola)
    circles = cv2.HoughCircles(heatmap, cv2.HOUGH_GRADIENT, dp=1, minDist=1,
                              param1=50, param2=2, minRadius=2, maxRadius=7)


    # Marcar caixas delimitadoras dos jogadores no frame
    output_img = mark_player_box(output_img, player1_boxes, currentFrame-1)
    output_img = mark_player_box(output_img, player2_boxes, currentFrame-1)

    # Converter para formato PIL para desenho
    PIL_image = cv2.cvtColor(output_img, cv2.COLOR_BGR2RGB)
    PIL_image = Image.fromarray(PIL_image)

    # Verificar se alguma bola foi detectada
    if circles is not None:
        # Se apenas uma bola foi detectada (caso ideal)
        if len(circles) == 1:
            # Extrair coordenadas x, y da bola detectada
            x = int(circles[0][0][0])
            y = int(circles[0][0][1])

            # Armazenar coordenadas e tempo
            coords.append([x, y])
            t.append(time.time() - last)

            # Adicionar coordenadas à fila para trajetória
            q.appendleft([x, y])
            # Remover coordenada mais antiga da fila
            q.pop()

        else:
            # Múltiplas detecções - caso ambíguo, não armazenar posição
            coords.append(None)
            t.append(time.time() - last)
            # Adicionar None à fila
            q.appendleft(None)
            # Remover coordenada mais antiga da fila
            q.pop()

    else:
        # Nenhuma bola detectada neste frame
        coords.append(None)
        t.append(time.time() - last)
        # Adicionar None à fila
        q.appendleft(None)
        # Remover coordenada mais antiga da fila
        q.pop()

    # Desenhar predição do frame atual e 7 frames anteriores como círculos amarelos (total: 8 frames)
    for i in range(0, 8):
        if q[i] is not None:
            draw_x = q[i][0]
            draw_y = q[i][1]
            # Criar caixa delimitadora para o círculo
            bbox = (draw_x - 2, draw_y - 2, draw_x + 2, draw_y + 2)
            draw = ImageDraw.Draw(PIL_image)
            draw.ellipse(bbox, outline='yellow')
            del draw

    # Converter formato PIL de volta para formato opencv
    opencvImage = cv2.cvtColor(np.array(PIL_image), cv2.COLOR_RGB2BGR)

    # Escrever frame processado no vídeo de saída
    output_video.write(opencvImage)

    # Avançar para próximo frame
    currentFrame += 1

# Finalizar processamento básico
video.release()
output_video.release()
print('Rastreamento básico concluído!')

# GERAÇÃO DO MINIMAPA (se solicitado)
if minimap == 1:
    print('Iniciando geração do minimapa...')
    game_video = cv2.VideoCapture(output_video_path)

    fps1 = int(game_video.get(cv2.CAP_PROP_FPS))
    output_width = int(game_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    output_height = int(game_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print('FPS do vídeo principal:', fps1)

    # Criar novo vídeo com minimapa
    output_video = cv2.VideoWriter('VideoOutput/video_with_map.mp4', fourcc, fps, (output_width, output_height))

    print('Adicionando o minimapa...')

    # Remover outliers das coordenadas da bola
    x, y = diff_xy(coords)
    remove_outliers(x, y, coords)

    # Interpolação para suavizar trajetória
    coords = interpolation(coords)

    # Criar visualização em vista superior da quadra
    create_top_view(court_detector, detection_model, coords, fps)

    # Carregar vídeo do minimapa gerado
    minimap_video = cv2.VideoCapture('VideoOutput/minimap.mp4')
    fps2 = int(minimap_video.get(cv2.CAP_PROP_FPS))
    print('FPS do minimapa:', fps2)

    # Combinar vídeo principal com minimapa
    while True:
        ret, frame = game_video.read()
        ret2, img = minimap_video.read()
        if ret:
            # Mesclar frame do jogo com minimapa
            output = merge(frame, img)
            output_video.write(output)
        else:
            break

    # Finalizar vídeos
    game_video.release()
    minimap_video.release()

output_video.release()

# PÓS-PROCESSAMENTO: Limpeza adicional dos dados
print('Iniciando pós-processamento dos dados...')
for _ in range(3):
    x, y = diff_xy(coords)
    remove_outliers(x, y, coords)

# Interpolação final para suavizar trajetória
coords = interpolation(coords)

# CÁLCULO DE VELOCIDADES
print('Calculando velocidades da bola...')
Vx = []  # Velocidades no eixo X
Vy = []  # Velocidades no eixo Y
V = []   # Velocidades resultantes
frames = [*range(len(coords))]

# Calcular velocidades entre frames consecutivos
for i in range(len(coords)-1):
    p1 = coords[i]      # Posição no frame atual
    p2 = coords[i+1]    # Posição no próximo frame
    t1 = t[i]           # Tempo do frame atual
    t2 = t[i+1]         # Tempo do próximo frame

    # Calcular velocidades nos eixos X e Y
    x = (p1[0]-p2[0])/(t1-t2)
    y = (p1[1]-p2[1])/(t1-t2)
    Vx.append(x)
    Vy.append(y)

# Calcular velocidade resultante (magnitude do vetor velocidade)
for i in range(len(Vx)):
    vx = Vx[i]
    vy = Vy[i]
    v = (vx**2+vy**2)**0.5  # Magnitude do vetor velocidade
    V.append(v)

xy = coords[:]

# DETECÇÃO DE QUIQUES (se solicitado)
if bounce == 1:
    print('Iniciando detecção de pontos de quique...')

    # Preparar dados para predição de quiques
    test_df = pd.DataFrame({
        'x': [coord[0] for coord in xy[:-1]],
        'y': [coord[1] for coord in xy[:-1]],
        'V': V
    })

    # Criar features de lag (dados dos 20 frames anteriores)
    # Essas features capturam o padrão de movimento que precede um quique
    for i in range(20, 0, -1):
        test_df[f'lagX_{i}'] = test_df['x'].shift(i, fill_value=0)
    for i in range(20, 0, -1):
        test_df[f'lagY_{i}'] = test_df['y'].shift(i, fill_value=0)
    for i in range(20, 0, -1):
        test_df[f'lagV_{i}'] = test_df['V'].shift(i, fill_value=0)

    # Remover colunas originais, manter apenas features de lag
    test_df.drop(['x', 'y', 'V'], 1, inplace=True)

    # Preparar dados de entrada para o classificador
    # Coordenadas X dos últimos 20 frames
    Xs = test_df[['lagX_20', 'lagX_19', 'lagX_18', 'lagX_17', 'lagX_16',
                  'lagX_15', 'lagX_14', 'lagX_13', 'lagX_12', 'lagX_11', 'lagX_10',
                  'lagX_9', 'lagX_8', 'lagX_7', 'lagX_6', 'lagX_5', 'lagX_4', 'lagX_3',
                  'lagX_2', 'lagX_1']]
    Xs = from_2d_array_to_nested(Xs.to_numpy())

    # Coordenadas Y dos últimos 20 frames
    Ys = test_df[['lagY_20', 'lagY_19', 'lagY_18', 'lagY_17',
                  'lagY_16', 'lagY_15', 'lagY_14', 'lagY_13', 'lagY_12', 'lagY_11',
                  'lagY_10', 'lagY_9', 'lagY_8', 'lagY_7', 'lagY_6', 'lagY_5', 'lagY_4',
                  'lagY_3', 'lagY_2', 'lagY_1']]
    Ys = from_2d_array_to_nested(Ys.to_numpy())

    # Velocidades dos últimos 20 frames
    Vs = test_df[['lagV_20', 'lagV_19', 'lagV_18',
                  'lagV_17', 'lagV_16', 'lagV_15', 'lagV_14', 'lagV_13', 'lagV_12',
                  'lagV_11', 'lagV_10', 'lagV_9', 'lagV_8', 'lagV_7', 'lagV_6', 'lagV_5',
                  'lagV_4', 'lagV_3', 'lagV_2', 'lagV_1']]
    Vs = from_2d_array_to_nested(Vs.to_numpy())

    # Combinar todas as features
    X = pd.concat([Xs, Ys, Vs], 1)

    # Carregar classificador pré-treinado para detecção de quiques
    clf = load(open('clf.pkl', 'rb'))

    # Fazer predições
    predcted = clf.predict(X)
    idx = list(np.where(predcted == 1)[0])
    idx = np.array(idx) - 10  # Ajuste de offset

    print(f'Detectados {len(idx)} possíveis pontos de quique')

    # Determinar qual vídeo usar como base
    if minimap == 1:
        video = cv2.VideoCapture('VideoOutput/video_with_map.mp4')
    else:
        video = cv2.VideoCapture(output_video_path)

    # Obter propriedades do vídeo
    output_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    output_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    print(f'FPS: {fps}, Frames: {length}')

    # Criar vídeo final com marcação de quiques
    output_video = cv2.VideoWriter('VideoOutput/final_video.mp4', fourcc, fps, (output_width, output_height))

    i = 0
    print('Gerando vídeo final com pontos de quique marcados...')
    while True:
        ret, frame = video.read()
        if ret:
            # Marcar pontos de quique com círculos azuis
            if i in idx:
                center_coordinates = int(xy[i][0]), int(xy[i][1])
                radius = 3
                color = (255, 0, 0)  # Azul em formato BGR
                thickness = -1
                cv2.circle(frame, center_coordinates, 10, color, thickness)
            i += 1
            output_video.write(frame)
        else:
            break

    video.release()
    output_video.release()
    print('Vídeo final gerado com sucesso!')

print('Processamento completo finalizado!')
