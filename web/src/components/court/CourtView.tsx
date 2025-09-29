import { useEffect, useRef } from 'react'
import { Position, CourtDetection } from '@/types'

interface CourtViewProps {
  ballPosition?: Position
  player1Position?: Position
  player2Position?: Position
  courtDetection?: CourtDetection
  showTrajectory?: boolean
  className?: string
}

const CourtView = ({
  ballPosition,
  player1Position,
  player2Position,
  courtDetection,
  showTrajectory = true,
  className = ''
}: CourtViewProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const ballTrajectory = useRef<Position[]>([])

  // Court dimensions (proportional to real tennis court)
  const COURT_WIDTH = 400
  const COURT_HEIGHT = 200
  const COURT_PADDING = 20

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    canvas.width = COURT_WIDTH + (COURT_PADDING * 2)
    canvas.height = COURT_HEIGHT + (COURT_PADDING * 2)

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Draw court
    drawCourt(ctx)

    // Draw elements
    if (ballPosition) {
      // Add to trajectory
      if (showTrajectory) {
        ballTrajectory.current.push(ballPosition)
        // Keep only last 50 positions
        if (ballTrajectory.current.length > 50) {
          ballTrajectory.current = ballTrajectory.current.slice(-50)
        }
        drawBallTrajectory(ctx)
      }
      drawBall(ctx, ballPosition)
    }

    if (player1Position) {
      drawPlayer(ctx, player1Position, '#2196F3', 'P1')
    }

    if (player2Position) {
      drawPlayer(ctx, player2Position, '#F44336', 'P2')
    }

    // Draw court detection overlay if available
    if (courtDetection) {
      drawCourtDetection(ctx, courtDetection)
    }
  }, [ballPosition, player1Position, player2Position, courtDetection, showTrajectory])

  const drawCourt = (ctx: CanvasRenderingContext2D) => {
    const x = COURT_PADDING
    const y = COURT_PADDING

    // Court surface
    ctx.fillStyle = '#4CAF50'
    ctx.fillRect(x, y, COURT_WIDTH, COURT_HEIGHT)

    // Court lines
    ctx.strokeStyle = '#FFFFFF'
    ctx.lineWidth = 2

    // Outer boundary
    ctx.strokeRect(x, y, COURT_WIDTH, COURT_HEIGHT)

    // Service lines
    const serviceLineY1 = y + COURT_HEIGHT * 0.25
    const serviceLineY2 = y + COURT_HEIGHT * 0.75

    ctx.beginPath()
    ctx.moveTo(x, serviceLineY1)
    ctx.lineTo(x + COURT_WIDTH, serviceLineY1)
    ctx.moveTo(x, serviceLineY2)
    ctx.lineTo(x + COURT_WIDTH, serviceLineY2)
    ctx.stroke()

    // Center line
    const centerX = x + COURT_WIDTH / 2
    ctx.beginPath()
    ctx.moveTo(centerX, serviceLineY1)
    ctx.lineTo(centerX, serviceLineY2)
    ctx.stroke()

    // Net
    ctx.strokeStyle = '#D4AF37'
    ctx.lineWidth = 3
    const netY = y + COURT_HEIGHT / 2
    ctx.beginPath()
    ctx.moveTo(x, netY)
    ctx.lineTo(x + COURT_WIDTH, netY)
    ctx.stroke()

    // Court labels
    ctx.fillStyle = '#FFFFFF'
    ctx.font = '12px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('Player 1', centerX, y + 15)
    ctx.fillText('Player 2', centerX, y + COURT_HEIGHT - 5)
  }

  const drawBall = (ctx: CanvasRenderingContext2D, position: Position) => {
    // Convert world coordinates to court coordinates
    const courtPos = worldToCourtCoordinates(position)

    // Ball shadow
    ctx.beginPath()
    ctx.arc(courtPos.x + 2, courtPos.y + 2, 6, 0, 2 * Math.PI)
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)'
    ctx.fill()

    // Ball
    ctx.beginPath()
    ctx.arc(courtPos.x, courtPos.y, 6, 0, 2 * Math.PI)
    ctx.fillStyle = '#FFEB3B'
    ctx.fill()
    ctx.strokeStyle = '#FF9800'
    ctx.lineWidth = 1
    ctx.stroke()

    // Ball highlight
    ctx.beginPath()
    ctx.arc(courtPos.x - 2, courtPos.y - 2, 2, 0, 2 * Math.PI)
    ctx.fillStyle = '#FFFFFF'
    ctx.fill()
  }

  const drawPlayer = (ctx: CanvasRenderingContext2D, position: Position, color: string, label: string) => {
    const courtPos = worldToCourtCoordinates(position)

    // Player circle
    ctx.beginPath()
    ctx.arc(courtPos.x, courtPos.y, 12, 0, 2 * Math.PI)
    ctx.fillStyle = color
    ctx.fill()
    ctx.strokeStyle = '#FFFFFF'
    ctx.lineWidth = 2
    ctx.stroke()

    // Player label
    ctx.fillStyle = '#FFFFFF'
    ctx.font = 'bold 10px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(label, courtPos.x, courtPos.y + 3)
  }

  const drawBallTrajectory = (ctx: CanvasRenderingContext2D) => {
    if (ballTrajectory.current.length < 2) return

    ctx.strokeStyle = 'rgba(255, 235, 59, 0.6)'
    ctx.lineWidth = 2
    ctx.setLineDash([2, 2])

    ctx.beginPath()
    const firstPos = worldToCourtCoordinates(ballTrajectory.current[0])
    ctx.moveTo(firstPos.x, firstPos.y)

    for (let i = 1; i < ballTrajectory.current.length; i++) {
      const pos = worldToCourtCoordinates(ballTrajectory.current[i])
      ctx.lineTo(pos.x, pos.y)
    }

    ctx.stroke()
    ctx.setLineDash([])
  }

  const drawCourtDetection = (ctx: CanvasRenderingContext2D, detection: CourtDetection) => {
    if (!detection.lines || detection.confidence < 0.5) return

    ctx.strokeStyle = `rgba(255, 255, 255, ${detection.confidence})`
    ctx.lineWidth = 1

    detection.lines.forEach(line => {
      const start = worldToCourtCoordinates(line.start)
      const end = worldToCourtCoordinates(line.end)

      ctx.beginPath()
      ctx.moveTo(start.x, start.y)
      ctx.lineTo(end.x, end.y)
      ctx.stroke()
    })

    // Confidence indicator
    ctx.fillStyle = '#FFFFFF'
    ctx.font = '10px Arial'
    ctx.textAlign = 'left'
    ctx.fillText(
      `Court Detection: ${(detection.confidence * 100).toFixed(0)}%`,
      COURT_PADDING,
      COURT_PADDING + COURT_HEIGHT + 15
    )
  }

  const worldToCourtCoordinates = (worldPos: Position): Position => {
    // Simple mapping - in real implementation, this would use camera calibration
    // and court detection to map pixel coordinates to court coordinates

    // For now, assume worldPos is already normalized to court dimensions
    const x = COURT_PADDING + (worldPos.x / 1280) * COURT_WIDTH
    const y = COURT_PADDING + (worldPos.y / 720) * COURT_HEIGHT

    return { x, y }
  }

  return (
    <div className={`flex justify-center ${className}`}>
      <canvas
        ref={canvasRef}
        className="border border-border rounded-lg bg-court-green"
        style={{ imageRendering: 'crisp-edges' }}
      />
    </div>
  )
}

export default CourtView