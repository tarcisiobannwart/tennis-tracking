"""
TrackNet - Rede Neural Convolucional para Rastreamento de Bola de Tênis

Este módulo implementa a arquitetura TrackNet, uma CNN profunda baseada na arquitetura
VGG-16 modificada para gerar mapas de calor que indicam a posição da bola de tênis
em imagens de vídeo.

A rede utiliza uma estrutura encoder-decoder:
- Encoder: Extrai características da imagem usando camadas convolucionais e pooling
- Decoder: Reconstrói a resolução original usando upsampling e gera mapa de calor

Architecture:
    - Input: (3, 360, 640) - 3 canais RGB, resolução 640x360
    - Output: (360*640, 256) - Mapa de calor com 256 níveis de intensidade
    - Total layers: 25 camadas (incluindo ativações e normalizações)

Reference:
    Baseado no paper "TrackNet: A Deep Learning Network for Tracking High-speed
    and Tiny Objects in Sports Applications"

Author: Tennis Tracking Team
Version: 1.0
"""

from keras.models import *
from keras.layers import *


def trackNet(n_classes, input_height, input_width):
    """
    Constrói e retorna o modelo TrackNet para rastreamento de bola.

    A arquitetura segue um padrão encoder-decoder baseado em VGG-16:
    - Encoder: Reduz dimensionalidade espacial enquanto aumenta profundidade
    - Decoder: Reconstrói resolução espacial para gerar mapa de calor

    Args:
        n_classes (int): Número de classes para o mapa de calor (geralmente 256)
        input_height (int): Altura da imagem de entrada (padrão: 360)
        input_width (int): Largura da imagem de entrada (padrão: 640)

    Returns:
        Model: Modelo Keras compilado pronto para treinamento/inferência

    Example:
        >>> model = trackNet(256, 360, 640)
        >>> model.compile(loss='categorical_crossentropy', optimizer='adadelta')
        >>> predictions = model.predict(image_batch)
    """

    # ENTRADA: Tensor de forma (3, altura, largura) para canais RGB
    imgs_input = Input(shape=(3, input_height, input_width))

    # ======== ENCODER - SEÇÃO DE CONTRAÇÃO ========
    # Bloco 1: Extração de características de baixo nível (64 filtros)
    # Layer 1: Primeira convolução para detectar bordas e texturas básicas
    x = Conv2D(64, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(imgs_input)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 2: Segunda convolução para refinar características do bloco 1
    x = Conv2D(64, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 3: Pooling para reduzir dimensionalidade espacial (640x360 -> 320x180)
    x = MaxPooling2D((2, 2), strides=(2, 2), data_format='channels_first')(x)

    # Bloco 2: Características de nível médio (128 filtros)
    # Layer 4: Detectar padrões mais complexos
    x = Conv2D(128, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 5: Refinamento das características do bloco 2
    x = Conv2D(128, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 6: Segundo pooling (320x180 -> 160x90)
    x = MaxPooling2D((2, 2), strides=(2, 2), data_format='channels_first')(x)

    # Bloco 3: Características de alto nível (256 filtros)
    # Layer 7: Detectar formas e objetos complexos
    x = Conv2D(256, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 8: Refinamento das características do bloco 3
    x = Conv2D(256, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 9: Terceira convolução para características ainda mais complexas
    x = Conv2D(256, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 10: Terceiro pooling (160x90 -> 80x45)
    x = MaxPooling2D((2, 2), strides=(2, 2), data_format='channels_first')(x)

    # Bloco 4: Características semânticas de mais alto nível (512 filtros)
    # Layer 11: Detectar objetos específicos como bolas
    x = Conv2D(512, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 12: Refinamento para detecção precisa de objetos
    x = Conv2D(512, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 13: Terceira convolução para características semânticas robustas
    x = Conv2D(512, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # ======== DECODER - SEÇÃO DE EXPANSÃO ========
    # Layer 14: Primeiro upsampling (80x45 -> 160x90)
    x = UpSampling2D((2, 2), data_format='channels_first')(x)

    # Bloco 5: Reconstrução com 256 filtros
    # Layer 15: Combinar características de alto nível com resolução aumentada
    x = Conv2D(256, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 16: Refinamento das características reconstruídas
    x = Conv2D(256, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 17: Terceira convolução para melhor reconstrução
    x = Conv2D(256, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 18: Segundo upsampling (160x90 -> 320x180)
    x = UpSampling2D((2, 2), data_format='channels_first')(x)

    # Bloco 6: Reconstrução com 128 filtros
    # Layer 19: Combinar características de nível médio
    x = Conv2D(128, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 20: Refinamento das características de nível médio
    x = Conv2D(128, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 21: Terceiro upsampling (320x180 -> 640x360) - resolução original
    x = UpSampling2D((2, 2), data_format='channels_first')(x)

    # Bloco 7: Reconstrução final com 64 filtros
    # Layer 22: Combinar características de baixo nível para detalhes finos
    x = Conv2D(64, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 23: Refinamento final das características de baixo nível
    x = Conv2D(64, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # Layer 24: Camada de saída - gerar mapa de calor final
    x = Conv2D(n_classes, (3, 3), kernel_initializer='random_uniform', padding='same',
               data_format='channels_first')(x)
    x = Activation('relu')(x)
    x = BatchNormalization()(x)

    # ======== FORMATAÇÃO DA SAÍDA ========
    # Obter dimensões da saída da camada 24
    o_shape = Model(imgs_input, x).output_shape
    print("Formato da saída da layer24:", o_shape[1], o_shape[2], o_shape[3])
    # Formato esperado: 256, 360, 640

    OutputHeight = o_shape[2]
    OutputWidth = o_shape[3]

    # Reformatar de (256, 360, 640) para (256, 360*640)
    # Isso lineariza as dimensões espaciais mantendo os canais separados
    x = Reshape((-1, OutputHeight*OutputWidth))(x)

    # Trocar ordem das dimensões de (256, 360*640) para (360*640, 256)
    # Isso coloca cada pixel como uma linha com 256 valores de probabilidade
    x = Permute((2, 1))(x)

    # Layer 25: Ativação softmax para gerar distribuição de probabilidade
    # Cada pixel terá probabilidades que somam 1 entre as 256 classes
    gaussian_output = Activation('softmax')(x)

    # ======== CONSTRUÇÃO DO MODELO FINAL ========
    model = Model(imgs_input, gaussian_output)
    model.outputWidth = OutputWidth
    model.outputHeight = OutputHeight

    # Mostrar detalhes da arquitetura do modelo
    model.summary()

    return model




