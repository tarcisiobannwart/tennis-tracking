import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useThemeStore, type CourtColor } from '@/stores/themeStore';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Check } from 'lucide-react';

const courtOptions = [
  {
    id: 'hard' as CourtColor,
    name: 'Hard Court',
    description: 'Superfície rápida e consistente',
    color: '#2196F3',
    hoverColor: '#1565C0',
    bgGradient: 'from-blue-500/20 to-blue-900/20',
  },
  {
    id: 'clay' as CourtColor,
    name: 'Clay Court',
    description: 'Superfície de saibro clássica',
    color: '#D4A373',
    hoverColor: '#8B5E3C',
    bgGradient: 'from-amber-600/20 to-orange-900/20',
  },
  {
    id: 'grass' as CourtColor,
    name: 'Grass Court',
    description: 'Grama natural tradicional',
    color: '#4CAF50',
    hoverColor: '#2E7D32',
    bgGradient: 'from-green-500/20 to-green-900/20',
  },
  {
    id: 'red_clay' as CourtColor,
    name: 'Red Clay',
    description: 'Saibro vermelho europeu',
    color: '#E53935',
    hoverColor: '#B71C1C',
    bgGradient: 'from-red-500/20 to-red-900/20',
  },
];

const Onboarding = () => {
  const navigate = useNavigate();
  const { courtColor, setCourtColor } = useThemeStore();
  const [selectedCourt, setSelectedCourt] = useState<CourtColor>(courtColor);
  const [isAnimating, setIsAnimating] = useState(false);

  // Pegar nome do usuário do localStorage
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const userName = user.name?.split(' ')[0] || 'Jogador';

  const handleSelectCourt = (court: CourtColor) => {
    setSelectedCourt(court);
    setIsAnimating(true);
    setCourtColor(court);

    setTimeout(() => {
      setIsAnimating(false);
    }, 300);
  };

  const handleContinue = () => {
    localStorage.setItem('onboardingCompleted', 'true');
    navigate('/');
  };

  const handleSkip = () => {
    localStorage.setItem('onboardingCompleted', 'true');
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f172a] p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-4xl"
      >
        <div className="text-center mb-12">
          <motion.h1
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="text-4xl md:text-5xl font-bold text-[#f1f5f9] mb-3"
          >
            Olá, {userName}!
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-lg text-[#94a3b8]"
          >
            Escolha a cor da quadra que melhor representa seu estilo
          </motion.p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          {courtOptions.map((court, index) => (
            <motion.div
              key={court.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + index * 0.1 }}
            >
              <Card
                className={`
                  relative overflow-hidden cursor-pointer transition-all duration-300
                  bg-[#1e293b] border-2 hover:scale-105
                  ${selectedCourt === court.id
                    ? 'border-current shadow-lg shadow-current/20'
                    : 'border-[#334155] hover:border-[#475569]'
                  }
                `}
                style={{
                  borderColor: selectedCourt === court.id ? court.color : undefined,
                }}
                onClick={() => handleSelectCourt(court.id)}
              >
                {/* Gradiente de fundo */}
                <div className={`absolute inset-0 bg-gradient-to-br ${court.bgGradient} opacity-50`} />

                {/* Conteúdo */}
                <div className="relative p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-[#f1f5f9] mb-1">
                        {court.name}
                      </h3>
                      <p className="text-sm text-[#94a3b8]">
                        {court.description}
                      </p>
                    </div>

                    {/* Checkbox animado */}
                    <motion.div
                      initial={false}
                      animate={{
                        scale: selectedCourt === court.id ? 1 : 0.8,
                        opacity: selectedCourt === court.id ? 1 : 0.3,
                      }}
                      className={`
                        flex items-center justify-center w-8 h-8 rounded-full
                        ${selectedCourt === court.id ? 'bg-current' : 'bg-[#334155]'}
                      `}
                      style={{
                        backgroundColor: selectedCourt === court.id ? court.color : undefined,
                      }}
                    >
                      {selectedCourt === court.id && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ type: 'spring', stiffness: 300 }}
                        >
                          <Check className="w-5 h-5 text-white" />
                        </motion.div>
                      )}
                    </motion.div>
                  </div>

                  {/* Preview da cor */}
                  <div className="flex items-center gap-2 mt-4">
                    <div className="flex gap-1">
                      <div
                        className="w-16 h-2 rounded-full"
                        style={{ backgroundColor: court.color }}
                      />
                      <div
                        className="w-10 h-2 rounded-full"
                        style={{ backgroundColor: court.hoverColor }}
                      />
                    </div>
                    <span className="text-xs text-[#94a3b8] ml-auto">
                      Preview do tema
                    </span>
                  </div>
                </div>

                {/* Efeito de brilho ao selecionar */}
                {selectedCourt === court.id && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: [0, 0.3, 0] }}
                    transition={{ duration: 0.6 }}
                    className="absolute inset-0 bg-current"
                    style={{ backgroundColor: court.color }}
                  />
                )}
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Botões de ação */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="flex flex-col sm:flex-row gap-3 justify-center"
        >
          <Button
            variant="outline"
            onClick={handleSkip}
            className="border-[#334155] text-[#94a3b8] hover:bg-[#1e293b] hover:text-[#f1f5f9]"
          >
            Pular por enquanto
          </Button>
          <Button
            onClick={handleContinue}
            className="px-8"
            style={{
              backgroundColor: courtOptions.find(c => c.id === selectedCourt)?.color,
            }}
          >
            Continuar
          </Button>
        </motion.div>

        {/* Indicador de progresso */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="flex justify-center gap-2 mt-8"
        >
          <div className="w-8 h-1 rounded-full bg-current" style={{
            backgroundColor: courtOptions.find(c => c.id === selectedCourt)?.color
          }} />
          <div className="w-8 h-1 rounded-full bg-[#334155]" />
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Onboarding;
