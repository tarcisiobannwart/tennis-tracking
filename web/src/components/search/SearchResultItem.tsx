/**
 * SearchResultItem - Item individual de resultado de busca.
 *
 * Implementado para TT-138: Busca global.
 */

import { User, MapPin, TrendingUp, Trophy } from 'lucide-react'

interface SearchResultItemProps {
  id: string
  type: string
  title: string
  subtitle?: string
  imageUrl?: string
  onClick: (type: string, id: string) => void
}

const getIcon = (type: string) => {
  switch (type) {
    case 'player':
      return <User className="w-4 h-4 text-blue-500" />
    case 'venue':
      return <MapPin className="w-4 h-4 text-green-500" />
    case 'ranking':
      return <TrendingUp className="w-4 h-4 text-purple-500" />
    case 'tournament':
      return <Trophy className="w-4 h-4 text-yellow-500" />
    default:
      return null
  }
}

export const SearchResultItem: React.FC<SearchResultItemProps> = ({
  id,
  type,
  title,
  subtitle,
  imageUrl,
  onClick,
}) => {
  const handleClick = () => {
    onClick(type, id)
  }

  return (
    <div
      onClick={handleClick}
      className="flex items-center gap-3 px-4 py-3 hover:bg-slate-700 cursor-pointer transition-colors"
    >
      {imageUrl ? (
        <img
          src={imageUrl}
          alt={title}
          className="w-8 h-8 rounded-full object-cover flex-shrink-0"
        />
      ) : (
        <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center flex-shrink-0">
          {getIcon(type)}
        </div>
      )}

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-100 truncate">{title}</p>
        {subtitle && <p className="text-xs text-slate-400 truncate">{subtitle}</p>}
      </div>
    </div>
  )
}

export default SearchResultItem
