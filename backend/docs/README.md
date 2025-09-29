# Tennis Tracking API

Professional FastAPI backend for tennis video analysis and player tracking.

## Features

- **Complete Match Management**: Create, track, and analyze tennis matches
- **Player Profiles**: Comprehensive player management with statistics
- **Real-time Analysis**: Live video processing with WebSocket updates
- **Advanced Analytics**: Performance metrics, heatmaps, and trend analysis
- **Training Management**: Training sessions, drills, and progress tracking
- **Computer Vision Integration**: Ball tracking, player detection, court analysis
- **Professional Architecture**: Clean code, async/await, comprehensive testing

## Quick Start

### Prerequisites

- Python 3.11+
- Redis (for caching and background tasks)
- PostgreSQL (for production) or SQLite (for development)

### Installation

1. **Clone and setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment setup**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Database setup**:
```bash
alembic upgrade head
```

4. **Download required models** (for video analysis):
```bash
# Download YOLO weights (237MB)
wget -O ../Yolov3/yolov3.weights https://pjreddie.com/media/files/yolov3.weights
```

5. **Run the application**:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` with automatic documentation at `/docs`.

## API Endpoints

### Matches
- `GET /api/matches` - List matches
- `POST /api/matches` - Create match
- `GET /api/matches/{id}` - Get match details
- `PUT /api/matches/{id}` - Update match
- `DELETE /api/matches/{id}` - Delete match
- `GET /api/matches/{id}/stats` - Match statistics
- `GET /api/matches/{id}/events` - Match events
- `POST /api/matches/{id}/start` - Start match
- `POST /api/matches/{id}/finish` - Finish match

### Players
- `GET /api/players` - List players
- `POST /api/players` - Create player
- `GET /api/players/{id}` - Player profile
- `PUT /api/players/{id}` - Update player
- `GET /api/players/{id}/stats` - Player statistics
- `GET /api/players/{id}/matches` - Player matches

### Live Analysis
- `POST /api/analyze/video` - Upload video for analysis
- `GET /api/analyze/status/{task_id}` - Check analysis status
- `GET /api/analyze/result/{task_id}` - Get analysis results
- `DELETE /api/analyze/task/{task_id}` - Cancel analysis

### Analytics
- `GET /api/analytics/performance/{match_id}` - Performance analytics
- `GET /api/analytics/heatmap/{match_id}` - Court heatmap data
- `GET /api/analytics/comparison` - Compare players
- `GET /api/analytics/trends/{player_id}` - Trend analysis

### Training
- `GET /api/training/drills` - Available drill types
- `POST /api/training/sessions` - Create training session
- `GET /api/training/sessions` - List training sessions
- `GET /api/training/progress/{player_id}` - Training progress

### WebSocket
- `WS /ws/live/{match_id}` - Live match updates
- `WS /ws/global` - Global system updates

## Video Analysis

The API integrates with the existing tennis tracking computer vision pipeline:

### Supported Features
- **Ball Tracking**: Using TrackNet for precise ball position detection
- **Player Detection**: YOLO-based player detection and tracking
- **Court Detection**: Automatic court line detection and perspective correction
- **Rally Analysis**: Automatic rally segmentation and analysis
- **Serve Analysis**: Serve speed, placement, and outcome detection
- **Bounce Detection**: Ball bounce point identification

### Video Processing Pipeline
1. **Upload**: Video files up to 500MB via REST API
2. **Preprocessing**: Frame extraction and preprocessing
3. **Analysis**: Multi-stage computer vision processing
4. **Real-time Updates**: Progress updates via WebSocket
5. **Results**: Comprehensive analysis data and statistics

### Example Usage
```python
import httpx

# Upload video
files = {"file": ("match.mp4", open("match.mp4", "rb"), "video/mp4")}
response = httpx.post("http://localhost:8000/api/analyze/video", files=files)
task_id = response.json()["task_id"]

# Check status
status = httpx.get(f"http://localhost:8000/api/analyze/status/{task_id}")
print(status.json())

# Get results (when completed)
result = httpx.get(f"http://localhost:8000/api/analyze/result/{task_id}")
```

## Real-time Features

### WebSocket Events
- `point_scored` - Point completion
- `game_won` - Game completion
- `set_won` - Set completion
- `match_update` - Live match updates
- `analysis_update` - Video processing progress
- `player_stats_update` - Live statistics

### Example WebSocket Client
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/live/match-id');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Live update:', data);
};
```

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test type
pytest tests/unit/
pytest tests/integration/
```

### Code Quality
```bash
# Format code
black app/
isort app/

# Lint
flake8 app/
mypy app/
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Deployment

### Docker
```bash
# Build image
docker build -t tennis-tracking-api .

# Run container
docker run -p 8000:8000 tennis-tracking-api
```

### Production Configuration
- Use PostgreSQL for database
- Configure Redis for caching
- Set up proper CORS origins
- Use environment variables for secrets
- Enable SSL/HTTPS
- Configure logging and monitoring

## Architecture

### Key Components
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: Async ORM with database models
- **Pydantic**: Data validation and serialization
- **WebSockets**: Real-time communication
- **Background Tasks**: Video processing and analysis
- **Computer Vision**: Integration with existing tennis tracking modules

### Database Schema
- **Players**: Player profiles and metadata
- **Matches**: Match information and status
- **Sets/Games/Points**: Hierarchical match structure
- **Events**: Real-time match events
- **Training**: Training sessions and drills

### Security Features
- Input validation with Pydantic
- SQL injection prevention
- Rate limiting
- CORS configuration
- Error handling and logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the Tennis Tracking system and follows the same license terms.

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the test examples in `tests/`
- Check the existing codebase integration in `../src/`