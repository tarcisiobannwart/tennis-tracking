/**
 * GlobalSearch - Campo de busca global com autocomplete.
 *
 * Implementado para TT-138: Busca global de jogadores, locais, rankings e torneios.
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import { Search, Loader2, X } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Input } from '@/components/ui/input'
import { searchGlobal, SearchResponse } from '@/services/searchService'
import { SearchResultGroup } from './SearchResultGroup'

// Debounce hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(timer)
    }
  }, [value, delay])

  return debouncedValue
}

export const GlobalSearch: React.FC = () => {
  const [query, setQuery] = useState<string>('')
  const [isOpen, setIsOpen] = useState<boolean>(false)
  const [loading, setLoading] = useState<boolean>(false)
  const [results, setResults] = useState<SearchResponse | null>(null)
  const debouncedQuery = useDebounce(query, 300)
  const searchRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  const fetchResults = useCallback(async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setResults(null)
      return
    }

    try {
      setLoading(true)
      const response = await searchGlobal({ q: searchQuery, limit: 5 })
      setResults(response)
      setIsOpen(true)
    } catch (error) {
      console.error('Erro ao buscar:', error)
      setResults(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchResults(debouncedQuery)
  }, [debouncedQuery, fetchResults])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false)
        setQuery('')
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleEscape)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value)
  }

  const handleClear = () => {
    setQuery('')
    setResults(null)
    setIsOpen(false)
  }

  const handleResultClick = (type: string, id: string) => {
    setIsOpen(false)
    setQuery('')

    switch (type) {
      case 'player':
        navigate(`/app/players/${id}`)
        break
      case 'venue':
        navigate(`/app/venues/${id}`)
        break
      case 'ranking':
        navigate(`/app/rankings/${id}`)
        break
      case 'tournament':
        navigate(`/app/tournaments/${id}`)
        break
      default:
        break
    }
  }

  const hasResults =
    results &&
    (results.players.length > 0 ||
      results.venues.length > 0 ||
      results.rankings.length > 0 ||
      results.tournaments.length > 0)

  return (
    <div ref={searchRef} className="relative w-full">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-500" />
        <Input
          type="text"
          placeholder="Buscar jogadores, locais, rankings..."
          value={query}
          onChange={handleInputChange}
          onFocus={() => query.length >= 2 && setIsOpen(true)}
          className="pl-10 pr-10 h-9 w-full bg-slate-800 border-slate-700 text-slate-100 text-sm"
        />
        {query && (
          <button
            onClick={handleClear}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-500 hover:text-slate-300"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {isOpen && query.length >= 2 && (
        <div className="absolute top-full mt-2 w-full bg-slate-800 border border-slate-700 rounded-lg shadow-xl max-h-[500px] overflow-y-auto z-50">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 text-court-accent animate-spin" />
            </div>
          ) : hasResults ? (
            <div className="py-2">
              {results.players.length > 0 && (
                <SearchResultGroup
                  title="Jogadores"
                  items={results.players.map((player) => ({
                    id: player.id,
                    type: 'player',
                    title: player.name,
                    subtitle: `@${player.username}`,
                    imageUrl: player.avatar_url,
                  }))}
                  onItemClick={handleResultClick}
                />
              )}

              {results.venues.length > 0 && (
                <SearchResultGroup
                  title="Locais"
                  items={results.venues.map((venue) => ({
                    id: venue.id,
                    type: 'venue',
                    title: venue.name,
                    subtitle: venue.city || venue.type,
                  }))}
                  onItemClick={handleResultClick}
                />
              )}

              {results.rankings.length > 0 && (
                <SearchResultGroup
                  title="Rankings"
                  items={results.rankings.map((ranking) => ({
                    id: ranking.id,
                    type: 'ranking',
                    title: ranking.name,
                    subtitle: ranking.category || 'Ranking',
                  }))}
                  onItemClick={handleResultClick}
                />
              )}

              {results.tournaments.length > 0 && (
                <SearchResultGroup
                  title="Torneios"
                  items={results.tournaments.map((tournament) => ({
                    id: tournament.id,
                    type: 'tournament',
                    title: tournament.name,
                    subtitle: tournament.status || 'Torneio',
                  }))}
                  onItemClick={handleResultClick}
                />
              )}
            </div>
          ) : (
            <div className="text-center py-8 px-4">
              <p className="text-sm text-slate-400">Nenhum resultado encontrado</p>
              <p className="text-xs text-slate-500 mt-1">Tente outros termos de busca</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default GlobalSearch
