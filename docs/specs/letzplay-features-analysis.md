# Analise de Funcionalidades - LetzPlay.me

## Referencia para Tennis Tracking (Projeto TT)

Documentacao das funcionalidades mapeadas no letzplay.me para servir de referencia
na implementacao de features similares no nosso sistema.

---

## 1. PERFIL DO JOGADOR (`/@username`)

### 1.1 Informacoes Basicas
- Avatar + capa (foto de fundo)
- Nome, @username
- Contadores: Jogos, Rankings, Torneios
- Informacoes: ultimo jogo, data de entrada, Instagram
- Genero, altura, lateralidade, backhand (1 ou 2 maos)

### 1.2 Tabs do Perfil
- **Principal**: Feed de atividades do jogador (partidas recentes)
- **Amigos**: Lista de amigos com avatar
- **Seguindo**: Quem o jogador segue
- **Fotos**: Galeria de fotos
- **Onde Joga**: Locais/academias/clubes associados

### 1.3 Estatisticas no Perfil
- Ultimos 20 jogos: Simples, Duplas, Rankings, Torneios (barra V/D)
- Resultado dos ultimos 20 jogos: Jogado, W.O., Desistencia
- Grafico: Jogos nos ultimos 12 meses (barras mensais)

### 1.4 Social
- Lista de amigos em comum com o visitante
- "Ja jogaram X vezes, veja o H2H" (link direto para Head to Head)
- Botao "Convidar Amigo"

---

## 2. FEED SOCIAL (`/u/feed`)

### 2.1 Criar Publicacao
- Textarea para texto livre
- Botao "Selecionar foto" para upload
- Botao "Publicar"

### 2.2 Cards de Partida no Feed
- Card visual com avatares dos jogadores (simples e duplas)
- Placar com sets (ex: 6-3, 2-6, 10-4)
- Indicacao de vencedor/perdedor (icone verde/vermelho)
- Nome do ranking/torneio de origem
- Data e local
- Botoes: Like, Torcer (para cada lado), Compartilhar, Ver estatisticas
- Secao de comentarios
- Contador de reacoes/visualizacoes

### 2.3 Atalhos Rapidos (Cards azuis no topo)
- Meus Jogos Pendentes
- Encontrar Torneios
- Meus Rankings
- Meus Torneios
- Minhas Estatisticas

---

## 3. PAINEL DE JOGOS (`/u/matches`)

### 3.1 Acoes
- **Chamar Amigo para Amistoso**: Encontrar amigo e convidar para jogo
- **Adicionar Jogo Amistoso**: Registrar resultado de jogo avulso
- **Meu Historico de Jogos**: Visualizar todos os jogos

---

## 4. RANKINGS (`/u/rankings`)

### 4.1 Meus Rankings
- Lista de todos os rankings que o jogador participa
- Cada ranking mostra: nome, categoria (Desafio/Pontos, Todos contra todos)
- Status: ativo/inativo/concluido
- Tipo: Simples, rodada atual
- Posicao atual (ex: 3o, 7o, 15o)
- Barra V/D (verde/vermelho)
- Mini grafico de evolucao de posicao (sparkline)
- Numero de jogadores
- Botao "Agendar" (para rodadas pendentes)
- Link "stats" para estatisticas do ranking
- Filtros

### 4.2 Classificacao do Ranking (`/rankings/{id}/table`)
- Tabela classificatoria com posicao, nome, pontos, jogos, V/D
- Navegacao por rodadas
- Regras de pontuacao

---

## 5. TORNEIOS (`/u/tournaments`)

### 5.1 Meus Torneios
- Lista de torneios inscritos com filtros

### 5.2 Encontre Torneios (`/u/tournaments/open`)
- Busca com filtros: esporte, estado, data, nome
- Secao "Meus Locais" (torneios dos meus clubes)
- Secao "Outros Locais" (torneios com inscricoes abertas)
- Cada torneio mostra: nome, organizador, categorias, inscricoes abertas, prazo, local
- Botao "Inscreva-se"

---

## 6. DESEMPENHO/ESTATISTICAS (`/u/dashboard`)

### 6.1 Resumo Geral
- Total de jogos, vitorias, derrotas
- Breakdown por tipo: Simples, Duplas, Torneios, Rankings, Amistosos
- Barras V/D para cada tipo

### 6.2 Por Tipo de Resultado
- Jogado, W.O. (walkover), Desistencia - separado V/D

### 6.3 Graficos
- **Jogos mes a mes**: Barras por mes (ultimos 12+ meses)
- **Vitorias e Derrotas nos ultimos 12 meses**: Linhas V/D sobrepostas
- **Por Idade do oponente**: Barras por faixa etaria (16-20, 21-30, 31-40, 40+, 50+)
- **Sequencia de Resultados**: Grid visual de V/D em sequencia
- **Por Tipo de Piso**: Barras H (Saibro, Rapida, etc.) com V/D
- **Vs. Destros / Vs. Canhotos**: Donut charts
- **Vs. BH Uma Mao / Vs. BH Duas Maos**: Donut charts

---

## 7. HEAD TO HEAD (`/u/h2h`)

### 7.1 Comparativo
- Fotos lado a lado dos jogadores
- Placar H2H (ex: 0/1)
- Tabela comparativa: Genero, Altura, Joga ha, Lateralidade, Backhand
- Vitorias/Derrotas e Aproveitamento de cada um
- Quantidade de Torcedores (barra)
- Graficos: Sets disputados, Games disputados (ao longo do tempo)
- Historico de confrontos diretos

---

## 8. AULAS E AGENDAMENTOS

### 8.1 Minhas Aulas (`/TarcisioBannwart/student/places`)
- Lista de aulas agendadas

### 8.2 Agendar uma Aula (`/u/lessons`)
- Tabs: Locais / Minhas Aulas
- Vinculacao com academias/clubes
- Selecao de horarios disponiveis

### 8.3 Agendar Reposicao (`/TarcisioBannwart/replacements`)
- Sistema para repor aulas perdidas

### 8.4 Alugar Quadra (`/u/locations`)
- Busca de academias/quadras com locacao online
- Tabs: Locais / Minhas Locacoes

### 8.5 Reservar Horario de Clube (`/u/clubs`)
- Reserva de horario em clubes associados

---

## 9. PERFIL DE LOCAL/CLUBE (`/@local`)

### 9.1 Informacoes
- Avatar + capa
- Nome, @username, tipo (Condominio, Academia, Clube)
- Contadores: Jogadores, Rankings, Torneios
- Tabs: Principal, Agenda, Jogos, Seguidores, Fotos
- Sobre: data de fundacao, contatos

### 9.2 Acoes para Jogador
- Botao "Associar-se"
- Botao "Quero participar do ranking"

### 9.3 Sidebar do Local
- Reservar horario de clube
- Marcar horario de ranking
- Rankings (X em andamento, Y concluidos)
- Torneios (X categorias em andamento)

---

## 10. NOTIFICACOES (`/u/notifications`)
- Feed cronologico de notificacoes
- Tipos: winner no jogo, aceitou amizade, novo jogo agendado, nova rodada
- Avatar do remetente + mensagem + timestamp

---

## 11. PAGAMENTOS (`/u/chargings/users`)
- Historico de pagamentos (inscricoes, aulas, locacoes)

---

## 12. NAVEGACAO E UX

### 12.1 Navbar Superior
- Logo LetzPlay
- Campo de busca global ("Procurar na LetzPlay")
- Icones: Home, Amigos, Calendario, Ranking, Torneios, Notificacoes, Perfil

### 12.2 Sidebar Esquerda (logado)
- Avatar + nome + @username
- Busca
- **Geral**: Pagina Inicial, Meu Perfil, Notificacoes, Painel de Jogos, Pagamentos
- **Competicoes**: Meus Rankings, Meus Torneios, Encontre Torneios
- **Jogue Mais**: Minhas Aulas, Agende uma Aula, Agende sua Reposicao, Alugue uma Quadra, Reserve um Horario de Clube
- **Desempenho**: Historico de Jogos, Estatisticas, Head to Head
- **Outros**: Convidar Amigo, Quero ser Gestor, Enviar Feedback
- **Config**: Editar e Configurar, Sair

### 12.3 Sidebar Direita (perfil)
- Suas Informacoes resumidas
- Ultimos 20 jogos (barras V/D)
- Resultado dos ultimos 20 jogos
- Grafico de jogos nos ultimos 12 meses

---

## 13. FUNCIONALIDADES TRANSVERSAIS

### 13.1 Sistema Social
- Amizades (solicitar, aceitar)
- Seguir perfis (jogadores e locais)
- Feed com publicacoes e resultados
- Comentarios em partidas
- Reacoes (like, torcer)
- Compartilhamento

### 13.2 Busca Global
- Busca por jogadores, locais, rankings, torneios

### 13.3 Multi-Esporte
- Tenis, Beach Tennis, Padel (filtro por esporte)

### 13.4 Gestao de Local (lado gestor)
- Criacao e gerenciamento de rankings
- Criacao e gerenciamento de torneios
- Agenda de quadras/horarios
- Gestao de alunos/aulas
- Pagamentos/cobranças

---

## Mapeamento para Issues TT

| # | Feature LetzPlay | Epic Sugerido | Prioridade |
|---|-----------------|---------------|------------|
| 1 | Perfil do Jogador (social) | Social Profile | Alta |
| 2 | Feed Social (publicacoes + resultados) | Social Feed | Media |
| 3 | Sistema de Rankings (classificacao, rodadas) | Rankings System | Alta |
| 4 | Sistema de Torneios (inscricao, chaves) | Tournament System | Alta |
| 5 | Dashboard de Estatisticas | Player Analytics | Alta |
| 6 | Head to Head (comparativo) | H2H Comparisons | Media |
| 7 | Historico de Jogos (placares, filtros) | Match History | Alta |
| 8 | Gestao de Locais/Clubes | Venue Management | Media |
| 9 | Agendamento (aulas, quadras, reposicoes) | Booking System | Baixa |
| 10 | Notificacoes | Notification System | Media |
| 11 | Pagamentos | Payment Integration | Baixa |
| 12 | Busca Global | Global Search | Media |
