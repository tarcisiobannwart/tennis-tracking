import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useThemeStore, CourtColor } from '../stores/themeStore'
import { useEffect, useState } from 'react'
import {
  Video,
  Target,
  BarChart3,
  Zap,
  Users,
  Trophy,
  ChevronRight,
  Play,
  Shield,
  Cpu,
  Eye,
  Star,
  Check,
  ArrowRight,
  Globe,
  Smartphone,
  Monitor,
} from 'lucide-react'

const courtColors: Record<CourtColor, { hex: string; name: string }> = {
  hard: { hex: '#2196F3', name: 'Hard Court' },
  clay: { hex: '#D4A373', name: 'Clay Court' },
  grass: { hex: '#4CAF50', name: 'Grass Court' },
  red_clay: { hex: '#E53935', name: 'Red Clay' },
}

const features = [
  {
    icon: Eye,
    title: 'Rastreamento de Bola',
    description: 'IA TrackNet detecta a bola em tempo real com precisao de pixels via heatmaps.',
  },
  {
    icon: Target,
    title: 'Deteccao de Quadra',
    description: 'Transformada de Hough identifica linhas e calcula perspectiva automaticamente.',
  },
  {
    icon: Users,
    title: 'Tracking de Jogadores',
    description: 'Faster R-CNN + SORT rastreia jogadores com IDs consistentes entre frames.',
  },
  {
    icon: BarChart3,
    title: 'Analytics Avancado',
    description: 'Eficiencia, consistencia, momentum e cobertura de quadra em tempo real.',
  },
  {
    icon: Zap,
    title: 'Deteccao de Quique',
    description: 'ML com 83% de precisao preve pontos de quique usando series temporais.',
  },
  {
    icon: Trophy,
    title: 'Pontuacao ATP/WTA',
    description: 'Regras oficiais com deteccao automatica de break point e match point.',
  },
]

const stats = [
  { value: '83%', label: 'Precisao de Quique' },
  { value: '17', label: 'Tipos de Eventos' },
  { value: '640x360', label: 'Resolucao de Analise' },
  { value: '3', label: 'Modelos de IA' },
]

const testimonials = [
  {
    name: 'Carlos M.',
    role: 'Treinador ATP',
    text: 'Revolucionou minha forma de analisar partidas. O tracking de bola e jogadores e impressionante.',
    rating: 5,
  },
  {
    name: 'Ana L.',
    role: 'Analista de Performance',
    text: 'Os heatmaps e analytics me permitem identificar padroes que antes eram impossiveis de ver.',
    rating: 5,
  },
  {
    name: 'Roberto S.',
    role: 'Clube de Tenis',
    text: 'Nossos alunos evoluiram muito mais rapido com o feedback visual em tempo real.',
    rating: 4,
  },
]

export default function LandingPage() {
  const navigate = useNavigate()
  const { courtColor, setCourtColor } = useThemeStore()
  const [activeColor, setActiveColor] = useState<CourtColor>(courtColor)

  useEffect(() => {
    document.documentElement.classList.add('dark')
  }, [])

  const handleColorChange = (color: CourtColor) => {
    setActiveColor(color)
    setCourtColor(color)
  }

  const accentHex = courtColors[activeColor].hex

  return (
    <div className="min-h-screen bg-[#0a0f1a] text-white overflow-x-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-[#0a0f1a]/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: accentHex }}
              >
                <Video className="w-4 h-4 text-white" />
              </div>
              <span className="text-lg font-bold">Tennis Tracking</span>
            </div>

            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm text-slate-400 hover:text-white transition-colors">
                Recursos
              </a>
              <a href="#pricing" className="text-sm text-slate-400 hover:text-white transition-colors">
                Planos
              </a>
              <a href="#testimonials" className="text-sm text-slate-400 hover:text-white transition-colors">
                Depoimentos
              </a>
              <a href="#faq" className="text-sm text-slate-400 hover:text-white transition-colors">
                FAQ
              </a>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/login')}
                className="text-sm text-slate-300 hover:text-white transition-colors"
              >
                Entrar
              </button>
              <button
                onClick={() => navigate('/login')}
                className="text-sm px-4 py-2 rounded-lg font-medium transition-all hover:opacity-90"
                style={{ backgroundColor: accentHex }}
              >
                Comecar Gratis
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 relative">
        {/* Background Effects */}
        <div
          className="absolute top-20 left-1/4 w-96 h-96 rounded-full blur-[120px] opacity-20"
          style={{ backgroundColor: accentHex }}
        />
        <div
          className="absolute bottom-0 right-1/4 w-72 h-72 rounded-full blur-[100px] opacity-10"
          style={{ backgroundColor: accentHex }}
        />

        <div className="max-w-7xl mx-auto text-center relative z-10">
          {/* Court Color Selector */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-center gap-2 mb-8"
          >
            <span className="text-xs text-slate-500 mr-2">Sua quadra:</span>
            {(Object.keys(courtColors) as CourtColor[]).map((color) => (
              <button
                key={color}
                onClick={() => handleColorChange(color)}
                className={`w-8 h-8 rounded-full transition-all duration-300 ${
                  activeColor === color ? 'ring-2 ring-offset-2 ring-offset-[#0a0f1a] scale-110' : 'opacity-60 hover:opacity-100'
                }`}
                style={{
                  backgroundColor: courtColors[color].hex,
                  '--tw-ring-color': courtColors[color].hex,
                } as React.CSSProperties}
                title={courtColors[color].name}
              />
            ))}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium mb-6 border"
              style={{
                backgroundColor: `${accentHex}15`,
                borderColor: `${accentHex}30`,
                color: accentHex,
              }}
            >
              <Cpu className="w-3 h-3" />
              Powered by TrackNet + YOLO + Faster R-CNN
            </div>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-5xl sm:text-6xl lg:text-7xl font-bold leading-tight mb-6"
          >
            Analise de Tenis
            <br />
            <span style={{ color: accentHex }}>Inteligente</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10"
          >
            Rastreie bola, jogadores e quadra com IA. Obtenha analytics
            avancados, deteccao de quique e pontuacao automatica em tempo real.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <button
              onClick={() => navigate('/login')}
              className="flex items-center gap-2 px-8 py-3.5 rounded-xl text-white font-semibold text-lg transition-all hover:opacity-90 hover:scale-105"
              style={{ backgroundColor: accentHex }}
            >
              <Play className="w-5 h-5" />
              Testar Gratis por 14 Dias
            </button>
            <button
              onClick={() => {
                document.getElementById('pricing')?.scrollIntoView({ behavior: 'smooth' })
              }}
              className="flex items-center gap-2 px-8 py-3.5 rounded-xl text-slate-300 font-medium text-lg border border-slate-700 hover:border-slate-500 transition-all"
            >
              Ver Planos
              <ChevronRight className="w-5 h-5" />
            </button>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20 max-w-3xl mx-auto"
          >
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl font-bold" style={{ color: accentHex }}>
                  {stat.value}
                </div>
                <div className="text-sm text-slate-500 mt-1">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Tecnologia de Ponta para{' '}
              <span style={{ color: accentHex }}>Cada Jogada</span>
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto">
              Tres modelos de deep learning trabalhando juntos para uma analise completa.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="group p-6 rounded-2xl bg-[#111827] border border-white/5 hover:border-white/10 transition-all duration-300"
                style={{
                  boxShadow: 'none',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow = `0 0 30px ${accentHex}15`
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = 'none'
                }}
              >
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
                  style={{ backgroundColor: `${accentHex}20` }}
                >
                  <feature.icon className="w-6 h-6" style={{ color: accentHex }} />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 bg-[#111827]/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Como <span style={{ color: accentHex }}>Funciona</span>
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto">
              Em 3 passos simples, transforme qualquer video em dados acionaveis.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                icon: Video,
                title: 'Faca Upload',
                description: 'Envie o video da partida. Aceitamos MP4 de qualquer camera ou transmissao oficial.',
              },
              {
                step: '02',
                icon: Cpu,
                title: 'IA Processa',
                description: 'TrackNet, YOLO e Faster R-CNN analisam cada frame detectando bola, quadra e jogadores.',
              },
              {
                step: '03',
                icon: BarChart3,
                title: 'Analise os Dados',
                description: 'Receba analytics completos: trajetorias, heatmaps, estatisticas e pontuacao automatica.',
              },
            ].map((item, i) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                className="text-center"
              >
                <div className="relative inline-block mb-6">
                  <div
                    className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto"
                    style={{ backgroundColor: `${accentHex}15` }}
                  >
                    <item.icon className="w-8 h-8" style={{ color: accentHex }} />
                  </div>
                  <span
                    className="absolute -top-2 -right-2 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white"
                    style={{ backgroundColor: accentHex }}
                  >
                    {item.step}
                  </span>
                </div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-slate-400 text-sm">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Planos para Cada{' '}
              <span style={{ color: accentHex }}>Nivel de Jogo</span>
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto">
              Do amador ao profissional, temos o plano certo para voce.
              Comece gratis e faca upgrade quando quiser.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Rally Plan - Free */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="rounded-2xl bg-[#111827] border border-white/5 p-8 flex flex-col"
            >
              <div className="mb-6">
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Iniciante</span>
                <h3 className="text-2xl font-bold mt-1">Rally</h3>
                <p className="text-slate-400 text-sm mt-2">Para quem esta comecando a explorar analytics.</p>
              </div>

              <div className="mb-8">
                <span className="text-4xl font-bold">Gratis</span>
                <span className="text-slate-500 text-sm ml-2">para sempre</span>
              </div>

              <ul className="space-y-3 mb-8 flex-1">
                {[
                  '3 videos por mes',
                  'Videos ate 5 minutos',
                  'Deteccao de bola e quadra',
                  'Pontuacao automatica basica',
                  'Dashboard com metricas',
                  'Suporte por email',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-3 text-sm text-slate-300">
                    <Check className="w-4 h-4 mt-0.5 text-slate-500 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>

              <button
                onClick={() => navigate('/login')}
                className="w-full py-3 rounded-xl font-medium border border-slate-700 text-slate-300 hover:bg-slate-800 transition-colors"
              >
                Comecar Gratis
              </button>
            </motion.div>

            {/* Match Point Plan - Pro */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="rounded-2xl border-2 p-8 flex flex-col relative"
              style={{
                backgroundColor: `${accentHex}08`,
                borderColor: accentHex,
              }}
            >
              <div
                className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-xs font-bold text-white"
                style={{ backgroundColor: accentHex }}
              >
                MAIS POPULAR
              </div>

              <div className="mb-6">
                <span className="text-xs font-medium uppercase tracking-wider" style={{ color: accentHex }}>
                  Profissional
                </span>
                <h3 className="text-2xl font-bold mt-1">Match Point</h3>
                <p className="text-slate-400 text-sm mt-2">Para jogadores e treinadores que levam a serio.</p>
              </div>

              <div className="mb-8">
                <span className="text-4xl font-bold">R$97</span>
                <span className="text-slate-500 text-sm ml-2">/mes</span>
              </div>

              <ul className="space-y-3 mb-8 flex-1">
                {[
                  'Videos ilimitados',
                  'Videos ate 60 minutos',
                  'Todos os modelos de IA',
                  'Tracking de jogadores (SORT)',
                  'Deteccao de quique (83%)',
                  'Heatmaps e analytics avancado',
                  'Minimap em tempo real',
                  'Exportacao de dados (CSV/JSON)',
                  'Historico de 90 dias',
                  'Suporte prioritario',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-3 text-sm text-slate-300">
                    <Check className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: accentHex }} />
                    {item}
                  </li>
                ))}
              </ul>

              <button
                onClick={() => navigate('/login')}
                className="w-full py-3 rounded-xl font-semibold text-white transition-all hover:opacity-90"
                style={{ backgroundColor: accentHex }}
              >
                Testar 14 Dias Gratis
              </button>
            </motion.div>

            {/* Grand Slam Plan - Enterprise */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="rounded-2xl bg-[#111827] border border-white/5 p-8 flex flex-col"
            >
              <div className="mb-6">
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Equipe</span>
                <h3 className="text-2xl font-bold mt-1">Grand Slam</h3>
                <p className="text-slate-400 text-sm mt-2">Para clubes, academias e equipes profissionais.</p>
              </div>

              <div className="mb-8">
                <span className="text-4xl font-bold">R$297</span>
                <span className="text-slate-500 text-sm ml-2">/mes</span>
              </div>

              <ul className="space-y-3 mb-8 flex-1">
                {[
                  'Tudo do Match Point',
                  'Ate 10 usuarios',
                  'Videos ate 3 horas',
                  'API de integracao (REST)',
                  'WebSocket tempo real',
                  'Processamento prioritario',
                  'Analytics comparativo',
                  'Relatorios automaticos',
                  'Historico ilimitado',
                  'Treinamento com IA',
                  'Suporte dedicado 24/7',
                  'Onboarding personalizado',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-3 text-sm text-slate-300">
                    <Check className="w-4 h-4 mt-0.5 text-slate-500 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>

              <button
                onClick={() => navigate('/login')}
                className="w-full py-3 rounded-xl font-medium border border-slate-700 text-slate-300 hover:bg-slate-800 transition-colors"
              >
                Falar com Vendas
              </button>
            </motion.div>
          </div>

          {/* Enterprise Custom */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mt-12 max-w-5xl mx-auto rounded-2xl bg-[#111827] border border-white/5 p-8 flex flex-col md:flex-row items-center justify-between gap-6"
          >
            <div>
              <h3 className="text-xl font-bold mb-1">Precisa de algo maior?</h3>
              <p className="text-slate-400 text-sm">
                Federacoes, broadcasters e grandes organizacoes. Plano personalizado com GPU dedicada e SLA garantido.
              </p>
            </div>
            <button
              className="flex items-center gap-2 px-6 py-3 rounded-xl font-medium text-white whitespace-nowrap transition-all hover:opacity-90"
              style={{ backgroundColor: accentHex }}
            >
              Contato Enterprise
              <ArrowRight className="w-4 h-4" />
            </button>
          </motion.div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="py-20 px-4 bg-[#111827]/50">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold mb-4">
              Compare os <span style={{ color: accentHex }}>Planos</span>
            </h2>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="rounded-2xl bg-[#0a0f1a] border border-white/5 overflow-hidden"
          >
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="text-left p-4 text-sm font-medium text-slate-400">Recurso</th>
                  <th className="p-4 text-sm font-medium text-center">Rally</th>
                  <th className="p-4 text-sm font-medium text-center" style={{ color: accentHex }}>
                    Match Point
                  </th>
                  <th className="p-4 text-sm font-medium text-center">Grand Slam</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { feature: 'Videos por mes', rally: '3', match: 'Ilimitado', grand: 'Ilimitado' },
                  { feature: 'Duracao maxima', rally: '5 min', match: '60 min', grand: '3 horas' },
                  { feature: 'Deteccao de bola', rally: true, match: true, grand: true },
                  { feature: 'Deteccao de quadra', rally: true, match: true, grand: true },
                  { feature: 'Tracking de jogadores', rally: false, match: true, grand: true },
                  { feature: 'Deteccao de quique', rally: false, match: true, grand: true },
                  { feature: 'Minimap top-view', rally: false, match: true, grand: true },
                  { feature: 'Heatmaps', rally: false, match: true, grand: true },
                  { feature: 'Pontuacao automatica', rally: 'Basica', match: 'Completa', grand: 'Completa' },
                  { feature: 'Exportacao de dados', rally: false, match: 'CSV/JSON', grand: 'CSV/JSON/API' },
                  { feature: 'Usuarios', rally: '1', match: '1', grand: 'Ate 10' },
                  { feature: 'API REST', rally: false, match: false, grand: true },
                  { feature: 'WebSocket ao vivo', rally: false, match: false, grand: true },
                  { feature: 'Treinamento com IA', rally: false, match: false, grand: true },
                  { feature: 'Suporte', rally: 'Email', match: 'Prioritario', grand: '24/7 Dedicado' },
                  { feature: 'Historico', rally: '7 dias', match: '90 dias', grand: 'Ilimitado' },
                ].map((row, i) => (
                  <tr key={row.feature} className={i % 2 === 0 ? 'bg-white/[0.02]' : ''}>
                    <td className="p-4 text-sm text-slate-300">{row.feature}</td>
                    <td className="p-4 text-center text-sm">
                      {typeof row.rally === 'boolean' ? (
                        row.rally ? (
                          <Check className="w-4 h-4 text-green-500 mx-auto" />
                        ) : (
                          <span className="text-slate-600">—</span>
                        )
                      ) : (
                        <span className="text-slate-400">{row.rally}</span>
                      )}
                    </td>
                    <td className="p-4 text-center text-sm">
                      {typeof row.match === 'boolean' ? (
                        row.match ? (
                          <Check className="w-4 h-4 mx-auto" style={{ color: accentHex }} />
                        ) : (
                          <span className="text-slate-600">—</span>
                        )
                      ) : (
                        <span style={{ color: accentHex }}>{row.match}</span>
                      )}
                    </td>
                    <td className="p-4 text-center text-sm">
                      {typeof row.grand === 'boolean' ? (
                        row.grand ? (
                          <Check className="w-4 h-4 text-green-500 mx-auto" />
                        ) : (
                          <span className="text-slate-600">—</span>
                        )
                      ) : (
                        <span className="text-slate-400">{row.grand}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </motion.div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Quem Usa, <span style={{ color: accentHex }}>Aprova</span>
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((t, i) => (
              <motion.div
                key={t.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="rounded-2xl bg-[#111827] border border-white/5 p-6"
              >
                <div className="flex gap-1 mb-4">
                  {Array.from({ length: 5 }).map((_, s) => (
                    <Star
                      key={s}
                      className="w-4 h-4"
                      fill={s < t.rating ? accentHex : 'transparent'}
                      style={{ color: s < t.rating ? accentHex : '#475569' }}
                    />
                  ))}
                </div>
                <p className="text-sm text-slate-300 mb-4 leading-relaxed">"{t.text}"</p>
                <div>
                  <p className="text-sm font-semibold">{t.name}</p>
                  <p className="text-xs text-slate-500">{t.role}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Multi-platform */}
      <section className="py-20 px-4 bg-[#111827]/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold mb-4">
              Disponivel em <span style={{ color: accentHex }}>Todas as Plataformas</span>
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto">
              Acesse do navegador, mobile ou integre via API. Seus dados sincronizados em tempo real.
            </p>
          </motion.div>

          <div className="flex flex-wrap items-center justify-center gap-8">
            {[
              { icon: Monitor, label: 'Web App' },
              { icon: Smartphone, label: 'Mobile (PWA)' },
              { icon: Globe, label: 'API REST' },
              { icon: Shield, label: 'SSL/Seguro' },
            ].map((item, i) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="flex flex-col items-center gap-3"
              >
                <div
                  className="w-16 h-16 rounded-2xl flex items-center justify-center"
                  style={{ backgroundColor: `${accentHex}15` }}
                >
                  <item.icon className="w-7 h-7" style={{ color: accentHex }} />
                </div>
                <span className="text-sm text-slate-400">{item.label}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-20 px-4">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold mb-4">
              Perguntas <span style={{ color: accentHex }}>Frequentes</span>
            </h2>
          </motion.div>

          <div className="space-y-4">
            {[
              {
                q: 'Posso testar antes de assinar?',
                a: 'Sim! O plano Rally e gratuito para sempre e o Match Point tem 14 dias de teste gratis, sem cartao de credito.',
              },
              {
                q: 'Que tipo de video posso enviar?',
                a: 'Aceitamos MP4 de cameras fixas, drones ou transmissoes TV. A resolucao minima recomendada e 720p para melhores resultados.',
              },
              {
                q: 'Quanto tempo leva o processamento?',
                a: 'Depende da duracao do video. Em media, 1 minuto de video leva cerca de 2 minutos para processar com todos os modelos de IA.',
              },
              {
                q: 'Funciona com qualquer tipo de quadra?',
                a: 'Sim! O sistema detecta automaticamente linhas em quadras de saibro, grama, hard court e carpet. A camera deve capturar a quadra inteira.',
              },
              {
                q: 'Posso cancelar a assinatura a qualquer momento?',
                a: 'Sim, sem multa ou fidelidade. O acesso continua ate o final do periodo pago.',
              },
              {
                q: 'Os dados sao seguros?',
                a: 'Sim. Usamos criptografia SSL, armazenamento seguro na AWS e seus videos sao processados em ambiente isolado. Nao compartilhamos dados.',
              },
            ].map((faq, i) => (
              <motion.details
                key={faq.q}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="group rounded-xl bg-[#111827] border border-white/5 cursor-pointer"
              >
                <summary className="flex items-center justify-between p-5 text-sm font-medium list-none">
                  {faq.q}
                  <ChevronRight className="w-4 h-4 text-slate-500 transition-transform group-open:rotate-90" />
                </summary>
                <p className="px-5 pb-5 text-sm text-slate-400 leading-relaxed">{faq.a}</p>
              </motion.details>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-20 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Pronto para Elevar seu Jogo?
            </h2>
            <p className="text-slate-400 mb-8 max-w-lg mx-auto">
              Junte-se a treinadores e jogadores que ja usam IA para
              analisar e melhorar seu desempenho na quadra.
            </p>
            <button
              onClick={() => navigate('/login')}
              className="inline-flex items-center gap-2 px-8 py-4 rounded-xl text-white font-semibold text-lg transition-all hover:opacity-90 hover:scale-105"
              style={{ backgroundColor: accentHex }}
            >
              <Play className="w-5 h-5" />
              Comecar Agora — E Gratis
            </button>
            <p className="text-xs text-slate-600 mt-4">Sem cartao de credito. Sem compromisso.</p>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div
                  className="w-7 h-7 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: accentHex }}
                >
                  <Video className="w-3.5 h-3.5 text-white" />
                </div>
                <span className="font-bold">Tennis Tracking</span>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                Analise inteligente de partidas de tenis com visao computacional e deep learning.
              </p>
            </div>

            <div>
              <h4 className="text-sm font-semibold mb-3">Produto</h4>
              <ul className="space-y-2">
                {['Recursos', 'Planos', 'API', 'Changelog'].map((item) => (
                  <li key={item}>
                    <a href="#" className="text-xs text-slate-500 hover:text-slate-300 transition-colors">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-semibold mb-3">Empresa</h4>
              <ul className="space-y-2">
                {['Sobre', 'Blog', 'Carreiras', 'Contato'].map((item) => (
                  <li key={item}>
                    <a href="#" className="text-xs text-slate-500 hover:text-slate-300 transition-colors">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-semibold mb-3">Legal</h4>
              <ul className="space-y-2">
                {['Termos de Uso', 'Privacidade', 'Cookies', 'LGPD'].map((item) => (
                  <li key={item}>
                    <a href="#" className="text-xs text-slate-500 hover:text-slate-300 transition-colors">
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-xs text-slate-600">
              &copy; {new Date().getFullYear()} Tennis Tracking. Todos os direitos reservados.
            </p>
            <div className="flex items-center gap-2">
              {(Object.keys(courtColors) as CourtColor[]).map((color) => (
                <div
                  key={color}
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: courtColors[color].hex }}
                />
              ))}
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
