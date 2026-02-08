/**
 * SearchResultGroup - Grupo de resultados de busca por categoria.
 *
 * Implementado para TT-138: Busca global.
 */

import { SearchResultItem } from './SearchResultItem'

interface SearchResultGroupProps {
  title: string
  items: Array<{
    id: string
    type: string
    title: string
    subtitle?: string
    imageUrl?: string
  }>
  onItemClick: (type: string, id: string) => void
}

export const SearchResultGroup: React.FC<SearchResultGroupProps> = ({
  title,
  items,
  onItemClick,
}) => {
  if (items.length === 0) return null

  return (
    <div className="border-t border-slate-700 first:border-t-0">
      <div className="px-4 py-2">
        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</h3>
      </div>
      <div>
        {items.map((item) => (
          <SearchResultItem key={item.id} {...item} onClick={onItemClick} />
        ))}
      </div>
    </div>
  )
}

export default SearchResultGroup
