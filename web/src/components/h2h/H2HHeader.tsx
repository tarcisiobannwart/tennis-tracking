/**
 * H2HHeader - TT-134
 * Fotos lado a lado + placar H2H central
 */

import { User } from 'lucide-react'
import { PlayerProfile, H2HScore } from '@/services/h2hService'

interface H2HHeaderProps {
  player: PlayerProfile
  opponent: PlayerProfile
  h2hScore: H2HScore
}

const H2HHeader = ({ player, opponent, h2hScore }: H2HHeaderProps) => {
  return (
    <div className="bg-gradient-to-r from-slate-800 via-slate-900 to-slate-800 rounded-2xl p-6 border border-slate-700">
      <div className="flex items-center justify-between gap-4">
        {/* Jogador */}
        <div className="flex flex-col items-center flex-1">
          <div className="w-20 h-20 md:w-24 md:h-24 rounded-full overflow-hidden border-2 border-green-500/50 bg-slate-700 flex items-center justify-center mb-3">
            {player.avatar_url ? (
              <img
                src={player.avatar_url}
                alt={player.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <User className="w-10 h-10 text-slate-400" />
            )}
          </div>
          <h3 className="text-base md:text-lg font-bold text-slate-100 text-center truncate max-w-[140px]">
            {player.name}
          </h3>
          {player.country && (
            <span className="text-xs text-slate-400 mt-0.5">{player.country}</span>
          )}
          {player.ranking && (
            <span className="text-xs text-court-accent mt-0.5">#{player.ranking}</span>
          )}
        </div>

        {/* Placar H2H */}
        <div className="flex flex-col items-center px-4">
          <p className="text-xs text-slate-400 uppercase tracking-wider mb-2">H2H</p>
          <div className="flex items-center gap-3">
            <span
              className={`text-3xl md:text-5xl font-bold ${
                h2hScore.player_wins > h2hScore.opponent_wins
                  ? 'text-green-400'
                  : h2hScore.player_wins < h2hScore.opponent_wins
                  ? 'text-red-400'
                  : 'text-slate-300'
              }`}
            >
              {h2hScore.player_wins}
            </span>
            <span className="text-2xl md:text-4xl text-slate-500 font-light">/</span>
            <span
              className={`text-3xl md:text-5xl font-bold ${
                h2hScore.opponent_wins > h2hScore.player_wins
                  ? 'text-green-400'
                  : h2hScore.opponent_wins < h2hScore.player_wins
                  ? 'text-red-400'
                  : 'text-slate-300'
              }`}
            >
              {h2hScore.opponent_wins}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            {h2hScore.player_wins + h2hScore.opponent_wins} confrontos
          </p>
        </div>

        {/* Adversario */}
        <div className="flex flex-col items-center flex-1">
          <div className="w-20 h-20 md:w-24 md:h-24 rounded-full overflow-hidden border-2 border-red-500/50 bg-slate-700 flex items-center justify-center mb-3">
            {opponent.avatar_url ? (
              <img
                src={opponent.avatar_url}
                alt={opponent.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <User className="w-10 h-10 text-slate-400" />
            )}
          </div>
          <h3 className="text-base md:text-lg font-bold text-slate-100 text-center truncate max-w-[140px]">
            {opponent.name}
          </h3>
          {opponent.country && (
            <span className="text-xs text-slate-400 mt-0.5">{opponent.country}</span>
          )}
          {opponent.ranking && (
            <span className="text-xs text-court-accent mt-0.5">#{opponent.ranking}</span>
          )}
        </div>
      </div>
    </div>
  )
}

export default H2HHeader
