# Tennis Tracking Web Application

A modern React application for real-time tennis analysis and match tracking, built to replace the Streamlit interface with a professional, responsive web platform.

## 🚀 Features

- **Real-time Analysis**: Live video analysis with WebSocket integration
- **Match Management**: Comprehensive match tracking and statistics
- **Player Profiles**: Detailed player statistics and performance metrics
- **Advanced Analytics**: Interactive charts and performance insights
- **Training Modules**: AI-powered training assistance and feedback
- **Court Visualization**: 2D/3D court views with ball and player tracking
- **Video Player**: Custom video player with overlay annotations
- **Responsive Design**: Modern UI that works on all devices

## 🛠️ Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type safety and better DX
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Shadcn/ui** - Modern component library
- **React Query** - Server state management
- **Zustand** - Client state management
- **React Router** - Client-side routing
- **Socket.io** - Real-time communication
- **Chart.js/Recharts** - Data visualization
- **Framer Motion** - Animations

## 📁 Project Structure

```
web/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # Base UI components (shadcn/ui)
│   │   ├── layout/         # Layout components
│   │   ├── video/          # Video player components
│   │   ├── court/          # Court visualization
│   │   ├── stats/          # Statistics components
│   │   └── player/         # Player-related components
│   ├── pages/              # Page components
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API and external services
│   ├── stores/             # Zustand stores
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Utility functions
│   └── assets/             # Static assets
├── tests/                  # Test files (NOT in src/)
├── docs/                   # Documentation
└── scripts/                # Build and deployment scripts
```

## 🚦 Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Running Python backend (see main README)

### Installation

1. **Install dependencies:**
   ```bash
   cd web
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open in browser:**
   ```
   http://localhost:3000
   ```

### Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

## 🔧 Configuration

### Environment Variables

Create `.env.local` file:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### API Integration

The app connects to the Python backend API running on port 8000. Ensure the backend is running before starting the frontend.

## 📱 Pages Overview

### Dashboard (`/`)
- System overview and live match monitoring
- Quick access to recent matches and statistics
- Real-time system status indicators

### Live Analysis (`/live`)
- Real-time video analysis interface
- Camera input and video upload
- Live statistics and court visualization
- WebSocket integration for real-time updates

### Matches (`/matches`)
- Match listing with filtering and search
- Match creation and management
- Export and sharing capabilities

### Match Detail (`/match/:id`)
- Detailed match view with video player
- Comprehensive statistics and analytics
- Court visualization and shot analysis

### Players (`/players`)
- Player profile management
- Performance statistics and trends
- Player comparison tools

### Analytics (`/analytics`)
- Advanced performance analytics
- Interactive charts and visualizations
- Performance trends and insights

### Training (`/training`)
- AI-powered training modules
- Technique analysis and feedback
- Progress tracking and recommendations

## 🎨 Design System

### Theme
- Dark/Light mode support
- Tennis-inspired color palette
- Consistent spacing and typography

### Components
- Built on Shadcn/ui foundation
- Custom tennis-specific components
- Responsive and accessible design

## 🔌 API Integration

### REST API
- Axios-based HTTP client
- Automatic error handling
- Request/response interceptors

### WebSocket
- Real-time live analysis data
- Automatic reconnection
- Event-based message handling

## 🧪 Testing

```bash
npm run test        # Run tests
npm run test:ui     # Run tests with UI
npm run lint        # Run linter
```

## 🚀 Deployment

### Build
```bash
npm run build
```

### Deploy
The built files in `dist/` can be served by any static hosting service:
- Nginx
- Apache
- Vercel
- Netlify
- AWS S3 + CloudFront

## 🔄 Development Workflow

1. **Feature Development**
   - Create feature branch
   - Implement component/page
   - Add TypeScript types
   - Write tests
   - Update documentation

2. **Code Quality**
   - ESLint for code quality
   - TypeScript for type safety
   - Prettier for formatting
   - Husky for pre-commit hooks

## 🤝 Contributing

1. Follow the established project structure
2. Use TypeScript for all new code
3. Follow the component naming conventions
4. Write tests for new features
5. Update documentation as needed

## 📚 Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Shadcn/ui](https://ui.shadcn.com)
- [React Query](https://tanstack.com/query/latest)
- [Zustand](https://github.com/pmndrs/zustand)

## 🔧 Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Ensure Python backend is running
   - Check API URL in environment variables
   - Verify CORS configuration

2. **WebSocket Connection Issues**
   - Check WebSocket URL configuration
   - Ensure proper proxy setup in Vite config
   - Verify backend WebSocket implementation

3. **Build Errors**
   - Clear node_modules and reinstall
   - Check TypeScript errors
   - Verify all imports are correct

For more help, check the main project documentation or create an issue.