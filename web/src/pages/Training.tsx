import { useState } from 'react'
import {
  Target,
  Play,
  Pause,
  RotateCcw,
  Settings,
  BookOpen,
  Trophy,
  Brain,
  Activity,
  Clock,
  CheckCircle
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

const Training = () => {
  const [selectedModule, setSelectedModule] = useState('shot-accuracy')
  const [isTraining, setIsTraining] = useState(false)

  // Mock training data
  const trainingModules = [
    {
      id: 'shot-accuracy',
      title: 'Shot Accuracy Training',
      description: 'Improve shot placement and accuracy with target practice',
      duration: '15-30 min',
      difficulty: 'Beginner',
      icon: Target,
      completed: false,
      progress: 65
    },
    {
      id: 'footwork',
      title: 'Footwork & Movement',
      description: 'Enhance court coverage and movement efficiency',
      duration: '20-40 min',
      difficulty: 'Intermediate',
      icon: Activity,
      completed: true,
      progress: 100
    },
    {
      id: 'serve-technique',
      title: 'Serve Technique',
      description: 'Perfect your serve with form analysis and feedback',
      duration: '25-35 min',
      difficulty: 'Advanced',
      icon: Trophy,
      completed: false,
      progress: 30
    },
    {
      id: 'strategy',
      title: 'Match Strategy',
      description: 'Learn tactical approaches and decision making',
      duration: '30-45 min',
      difficulty: 'Intermediate',
      icon: Brain,
      completed: false,
      progress: 0
    }
  ]

  const currentModule = trainingModules.find(m => m.id === selectedModule)

  const trainingExercises = {
    'shot-accuracy': [
      {
        id: 1,
        name: 'Corner Target Practice',
        description: 'Hit 10 consecutive shots to corner targets',
        target: 10,
        achieved: 7,
        status: 'in-progress'
      },
      {
        id: 2,
        name: 'Cross-Court Precision',
        description: 'Land 8/10 shots in designated cross-court zones',
        target: 8,
        achieved: 8,
        status: 'completed'
      },
      {
        id: 3,
        name: 'Down-the-Line Accuracy',
        description: 'Maintain accuracy on down-the-line shots',
        target: 6,
        achieved: 4,
        status: 'in-progress'
      }
    ],
    'footwork': [
      {
        id: 1,
        name: 'Ladder Drills',
        description: 'Complete agility ladder sequences',
        target: 5,
        achieved: 5,
        status: 'completed'
      },
      {
        id: 2,
        name: 'Court Coverage',
        description: 'Practice baseline to net movements',
        target: 15,
        achieved: 15,
        status: 'completed'
      }
    ],
    'serve-technique': [
      {
        id: 1,
        name: 'Serve Form Analysis',
        description: 'Record and analyze serve technique',
        target: 1,
        achieved: 0,
        status: 'pending'
      },
      {
        id: 2,
        name: 'Power Progression',
        description: 'Gradually increase serve power',
        target: 10,
        achieved: 3,
        status: 'in-progress'
      }
    ],
    'strategy': [
      {
        id: 1,
        name: 'Pattern Recognition',
        description: 'Identify and exploit opponent patterns',
        target: 5,
        achieved: 0,
        status: 'pending'
      }
    ]
  }

  const currentExercises = trainingExercises[selectedModule as keyof typeof trainingExercises] || []

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner': return 'text-green-600 bg-green-100 dark:bg-green-900'
      case 'Intermediate': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900'
      case 'Advanced': return 'text-red-600 bg-red-100 dark:bg-red-900'
      default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'in-progress': return <Clock className="w-4 h-4 text-yellow-500" />
      default: return <Target className="w-4 h-4 text-gray-400" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Training Center</h1>
          <p className="text-muted-foreground">
            AI-powered training modules to improve your tennis skills
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Button>
          <Button variant="outline">
            <BookOpen className="w-4 h-4 mr-2" />
            Guide
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-4">
        {/* Training Modules */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="w-5 h-5 mr-2" />
                Training Modules
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {trainingModules.map((module) => {
                  const Icon = module.icon
                  return (
                    <div
                      key={module.id}
                      onClick={() => setSelectedModule(module.id)}
                      className={`p-3 rounded-lg cursor-pointer transition-colors ${
                        selectedModule === module.id
                          ? 'bg-primary text-primary-foreground'
                          : 'hover:bg-accent'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <Icon className="w-5 h-5" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{module.title}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            <span className={`px-2 py-0.5 rounded text-xs ${getDifficultyColor(module.difficulty)}`}>
                              {module.difficulty}
                            </span>
                            {module.completed && (
                              <CheckCircle className="w-3 h-3 text-green-500" />
                            )}
                          </div>
                          <div className="mt-2">
                            <div className="w-full bg-secondary rounded-full h-1.5">
                              <div
                                className="bg-primary h-1.5 rounded-full"
                                style={{ width: `${module.progress}%` }}
                              />
                            </div>
                            <span className="text-xs opacity-75">{module.progress}% complete</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Training Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Module Header */}
          {currentModule && (
            <Card>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
                      <currentModule.icon className="w-6 h-6 text-primary-foreground" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold mb-2">{currentModule.title}</h2>
                      <p className="text-muted-foreground mb-4">{currentModule.description}</p>
                      <div className="flex items-center space-x-4 text-sm">
                        <div className="flex items-center space-x-1">
                          <Clock className="w-4 h-4" />
                          <span>{currentModule.duration}</span>
                        </div>
                        <span className={`px-2 py-1 rounded ${getDifficultyColor(currentModule.difficulty)}`}>
                          {currentModule.difficulty}
                        </span>
                        <div className="flex items-center space-x-1">
                          <Target className="w-4 h-4" />
                          <span>{currentModule.progress}% Complete</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    {!isTraining ? (
                      <Button onClick={() => setIsTraining(true)}>
                        <Play className="w-4 h-4 mr-2" />
                        Start Training
                      </Button>
                    ) : (
                      <>
                        <Button onClick={() => setIsTraining(false)} variant="outline">
                          <Pause className="w-4 h-4 mr-2" />
                          Pause
                        </Button>
                        <Button variant="outline">
                          <RotateCcw className="w-4 h-4 mr-2" />
                          Reset
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Training Interface */}
          {isTraining ? (
            <Card>
              <CardHeader>
                <CardTitle>Training in Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-96 bg-muted rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <Activity className="w-16 h-16 mx-auto text-primary mb-4 animate-pulse" />
                    <h3 className="text-xl font-semibold mb-2">AI Analysis Active</h3>
                    <p className="text-muted-foreground mb-4">
                      Real-time feedback and analysis in progress
                    </p>
                    <div className="space-y-2">
                      <div className="w-64 bg-secondary rounded-full h-2 mx-auto">
                        <div className="bg-primary h-2 rounded-full w-3/4 animate-pulse"></div>
                      </div>
                      <p className="text-sm text-muted-foreground">Analyzing technique...</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Exercises List */}
              <Card>
                <CardHeader>
                  <CardTitle>Training Exercises</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {currentExercises.map((exercise) => (
                      <div
                        key={exercise.id}
                        className="flex items-center justify-between p-4 border rounded-lg"
                      >
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(exercise.status)}
                          <div>
                            <h4 className="font-medium">{exercise.name}</h4>
                            <p className="text-sm text-muted-foreground">
                              {exercise.description}
                            </p>
                          </div>
                        </div>

                        <div className="text-right">
                          <div className="text-sm font-medium">
                            {exercise.achieved}/{exercise.target}
                          </div>
                          <div className="w-16 bg-secondary rounded-full h-2 mt-1">
                            <div
                              className={`h-2 rounded-full ${
                                exercise.status === 'completed' ? 'bg-green-500' :
                                exercise.status === 'in-progress' ? 'bg-yellow-500' :
                                'bg-gray-300'
                              }`}
                              style={{ width: `${(exercise.achieved / exercise.target) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* AI Feedback */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Brain className="w-5 h-5 mr-2" />
                    AI Feedback & Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="border-l-4 border-blue-500 pl-4">
                      <h4 className="font-medium text-blue-700 dark:text-blue-300">
                        Technique Improvement
                      </h4>
                      <p className="text-sm text-muted-foreground">
                        Your follow-through could be more consistent. Focus on completing the swing motion.
                      </p>
                    </div>

                    <div className="border-l-4 border-green-500 pl-4">
                      <h4 className="font-medium text-green-700 dark:text-green-300">
                        Strength
                      </h4>
                      <p className="text-sm text-muted-foreground">
                        Excellent footwork positioning. Your court coverage has improved by 15%.
                      </p>
                    </div>

                    <div className="border-l-4 border-yellow-500 pl-4">
                      <h4 className="font-medium text-yellow-700 dark:text-yellow-300">
                        Focus Area
                      </h4>
                      <p className="text-sm text-muted-foreground">
                        Work on serve consistency. Consider practicing the ball toss motion.
                      </p>
                    </div>
                  </div>

                  <Button variant="outline" className="w-full mt-4">
                    <BookOpen className="w-4 h-4 mr-2" />
                    View Detailed Analysis
                  </Button>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Training