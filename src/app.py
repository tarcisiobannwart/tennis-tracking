"""
Tennis Analytics - Aplicação Principal

Ponto de entrada principal do sistema de análise de tênis.
Integra visão computacional, controle de jogo e análises em tempo real.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Importar módulos do sistema
from game_control import MatchManager
from game_control.models import Match, Player, PlayerInfo, Court
from scoring import ScoreManager
from analytics import PerformanceAnalyzer
from computer_vision import CourtDetector, PlayerDetector, BallDetector
from events import EventManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TennisAnalyticsApp:
    """
    Aplicação principal do sistema de análise de tênis.

    Coordena todos os módulos para análise completa de partidas.
    """

    def __init__(self):
        """Inicializa a aplicação."""
        self.match_manager: Optional[MatchManager] = None
        self.score_manager: Optional[ScoreManager] = None
        self.performance_analyzer: Optional[PerformanceAnalyzer] = None
        self.event_manager: Optional[EventManager] = None

        # Componentes de visão computacional
        self.court_detector: Optional[CourtDetector] = None
        self.player_detector: Optional[PlayerDetector] = None
        self.ball_detector: Optional[BallDetector] = None

        logger.info("TennisAnalyticsApp inicializada")

    def setup_match(self, player1_name: str, player2_name: str,
                   tournament: str = "", round_name: str = "",
                   match_format: str = "best_of_3") -> str:
        """
        Configura uma nova partida.

        Args:
            player1_name: Nome do jogador 1
            player2_name: Nome do jogador 2
            tournament: Nome do torneio
            round_name: Nome da rodada
            match_format: Formato da partida

        Returns:
            ID da partida criada
        """
        # Criar informações dos jogadores
        player1_info = PlayerInfo(name=player1_name)
        player2_info = PlayerInfo(name=player2_name)

        # Criar quadra padrão
        court = Court(court_id="main_court")

        # Criar match ID único
        match_id = f"match_{int(time.time())}"

        # Criar gerenciador de partida
        from game_control.models.match import MatchFormat
        format_enum = MatchFormat.BEST_OF_3 if match_format == "best_of_3" else MatchFormat.BEST_OF_5

        self.match_manager = MatchManager(
            match_id=match_id,
            player1_info=player1_info,
            player2_info=player2_info,
            court=court,
            match_format=format_enum
        )

        # Criar gerenciador de pontuação
        self.score_manager = ScoreManager(self.match_manager.match)

        # Criar analisador de performance
        try:
            self.performance_analyzer = PerformanceAnalyzer(self.match_manager.match)
        except Exception as e:
            logger.warning(f"Performance analyzer não disponível: {e}")

        # Criar gerenciador de eventos
        try:
            self.event_manager = EventManager(self.match_manager.match)
        except Exception as e:
            logger.warning(f"Event manager não disponível: {e}")

        # Configurar callbacks
        self._setup_callbacks()

        logger.info(f"Partida configurada: {match_id}")
        return match_id

    def _setup_callbacks(self):
        """Configura callbacks entre módulos."""
        if not self.match_manager:
            return

        # Callback para atualização de pontuação
        def on_point_scored(event_data):
            if self.score_manager:
                self.score_manager.update_score(
                    event_data['winner_player_id'],
                    event_data.get('point_type', 'normal'),
                    **event_data.get('point_data', {})
                )

        self.match_manager.register_event_callback('point_scored', on_point_scored)

        # Callback para análise de performance
        def on_game_won(event_data):
            if self.performance_analyzer:
                try:
                    self.performance_analyzer.analyze_game_performance(
                        event_data['set_number'],
                        event_data['game_number']
                    )
                except Exception as e:
                    logger.error(f"Erro na análise de performance: {e}")

        self.match_manager.register_event_callback('game_won', on_game_won)

    def start_match(self, serving_player: str = "player1"):
        """
        Inicia a partida.

        Args:
            serving_player: ID do jogador que vai sacar primeiro
        """
        if not self.match_manager:
            raise ValueError("Partida não configurada. Chame setup_match() primeiro.")

        self.match_manager.start_match(serving_player)
        logger.info(f"Partida iniciada - Sacador: {serving_player}")

    def setup_computer_vision(self, video_path: Optional[str] = None):
        """
        Configura os módulos de visão computacional.

        Args:
            video_path: Caminho para o vídeo (opcional)
        """
        try:
            self.court_detector = CourtDetector()
            logger.info("Court detector configurado")
        except Exception as e:
            logger.error(f"Erro ao configurar court detector: {e}")

        try:
            self.player_detector = PlayerDetector()
            logger.info("Player detector configurado")
        except Exception as e:
            logger.error(f"Erro ao configurar player detector: {e}")

        try:
            self.ball_detector = BallDetector()
            logger.info("Ball detector configurado")
        except Exception as e:
            logger.error(f"Erro ao configurar ball detector: {e}")

    def process_video(self, input_path: str, output_path: str,
                     enable_minimap: bool = False,
                     enable_bounce_detection: bool = False):
        """
        Processa um vídeo de tênis completo.

        Args:
            input_path: Caminho do vídeo de entrada
            output_path: Caminho do vídeo de saída
            enable_minimap: Habilitar geração de minimapa
            enable_bounce_detection: Habilitar detecção de quiques
        """
        logger.info(f"Processando vídeo: {input_path}")

        # Verificar se os componentes estão configurados
        if not all([self.court_detector, self.player_detector, self.ball_detector]):
            self.setup_computer_vision()

        # Importar o pipeline de processamento de vídeo original
        # (adaptado do main.py existente)
        from .video_processor import VideoProcessor

        processor = VideoProcessor(
            court_detector=self.court_detector,
            player_detector=self.player_detector,
            ball_detector=self.ball_detector,
            match_manager=self.match_manager
        )

        processor.process_video(
            input_path=input_path,
            output_path=output_path,
            enable_minimap=enable_minimap,
            enable_bounce_detection=enable_bounce_detection
        )

    def add_point(self, winner_player_id: str, point_type: str = "normal", **kwargs):
        """
        Adiciona um ponto manualmente.

        Args:
            winner_player_id: ID do jogador que ganhou o ponto
            point_type: Tipo do ponto
            **kwargs: Dados adicionais
        """
        if not self.match_manager:
            raise ValueError("Partida não configurada")

        self.match_manager.add_point(winner_player_id, point_type, **kwargs)

    def get_current_score(self) -> dict:
        """
        Retorna a pontuação atual.

        Returns:
            Dicionário com a pontuação atual
        """
        if not self.score_manager:
            return {}

        return self.score_manager.get_current_score()

    def get_live_data(self) -> dict:
        """
        Retorna dados em tempo real para transmissão.

        Returns:
            Dados completos para live stream
        """
        data = {}

        if self.score_manager:
            data['score'] = self.score_manager.get_live_score_data()

        if self.match_manager:
            data['match_stats'] = self.match_manager.get_match_statistics()
            data['recent_events'] = self.match_manager.get_recent_events(10)

        if self.performance_analyzer:
            try:
                data['performance'] = self.performance_analyzer.get_live_analytics()
            except Exception as e:
                logger.error(f"Erro ao obter analytics: {e}")

        return data

    def export_match_data(self) -> dict:
        """
        Exporta todos os dados da partida.

        Returns:
            Dados completos da partida
        """
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }

        if self.match_manager:
            export_data['match'] = self.match_manager.export_match_data()

        if self.score_manager:
            export_data['scoring'] = self.score_manager.export_scoring_data()

        if self.performance_analyzer:
            try:
                export_data['analytics'] = self.performance_analyzer.export_analytics()
            except Exception as e:
                logger.error(f"Erro ao exportar analytics: {e}")

        return export_data


def create_cli_parser():
    """Cria o parser para argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description='Tennis Analytics - Sistema de Análise de Tênis'
    )

    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')

    # Comando de processamento de vídeo
    video_parser = subparsers.add_parser('process-video', help='Processar vídeo de tênis')
    video_parser.add_argument('--input', required=True, help='Caminho do vídeo de entrada')
    video_parser.add_argument('--output', help='Caminho do vídeo de saída')
    video_parser.add_argument('--player1', default='Player 1', help='Nome do jogador 1')
    video_parser.add_argument('--player2', default='Player 2', help='Nome do jogador 2')
    video_parser.add_argument('--tournament', default='', help='Nome do torneio')
    video_parser.add_argument('--round', default='', help='Nome da rodada')
    video_parser.add_argument('--minimap', action='store_true', help='Gerar minimapa')
    video_parser.add_argument('--bounce', action='store_true', help='Detectar quiques')
    video_parser.add_argument('--format', choices=['best_of_3', 'best_of_5'],
                             default='best_of_3', help='Formato da partida')

    # Comando de simulação de partida
    sim_parser = subparsers.add_parser('simulate', help='Simular uma partida')
    sim_parser.add_argument('--player1', default='Player 1', help='Nome do jogador 1')
    sim_parser.add_argument('--player2', default='Player 2', help='Nome do jogador 2')
    sim_parser.add_argument('--points', type=int, default=10, help='Número de pontos a simular')

    return parser


def main():
    """Função principal da aplicação."""
    import time
    from datetime import datetime

    parser = create_cli_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Criar aplicação
    app = TennisAnalyticsApp()

    if args.command == 'process-video':
        # Configurar partida
        match_id = app.setup_match(
            player1_name=args.player1,
            player2_name=args.player2,
            tournament=args.tournament,
            round_name=args.round,
            match_format=args.format
        )

        # Determinar caminho de saída
        output_path = args.output
        if not output_path:
            input_path = Path(args.input)
            output_path = input_path.parent / f"{input_path.stem}_analyzed{input_path.suffix}"

        # Processar vídeo
        app.process_video(
            input_path=args.input,
            output_path=str(output_path),
            enable_minimap=args.minimap,
            enable_bounce_detection=args.bounce
        )

        # Exportar dados
        export_data = app.export_match_data()
        export_path = Path(output_path).parent / f"{match_id}_data.json"

        import json
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Processamento concluído. Dados exportados para: {export_path}")

    elif args.command == 'simulate':
        # Configurar partida
        match_id = app.setup_match(
            player1_name=args.player1,
            player2_name=args.player2
        )

        # Iniciar partida
        app.start_match()

        # Simular pontos
        import random

        for i in range(args.points):
            # Escolher vencedor aleatório
            winner = "player1" if random.random() > 0.5 else "player2"

            # Escolher tipo de ponto aleatório
            point_types = ["normal", "ace", "winner", "unforced_error"]
            point_type = random.choice(point_types)

            # Adicionar ponto
            app.add_point(winner, point_type)

            # Mostrar pontuação atual
            score = app.get_current_score()
            print(f"Ponto {i+1}: {point_type} para {winner}")
            print(f"Placar: {score.get('score', {}).get('score_string', 'N/A')}")
            print("---")

            time.sleep(0.5)  # Pausa entre pontos

        # Exportar dados finais
        export_data = app.export_match_data()
        export_path = f"{match_id}_simulation.json"

        import json
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"Simulação concluída. Dados exportados para: {export_path}")


if __name__ == "__main__":
    main()