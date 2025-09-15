"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Checkbox } from "@/components/ui/checkbox"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Brain,
  Play,
  RotateCcw,
  CheckCircle,
  XCircle,
  Clock,
  Target,
  Trophy,
  Zap,
  BookOpen,
  Plus,
  Settings,
  BarChart3,
} from "lucide-react"

interface Question {
  id: string
  type: "mcq" | "true-false" | "fill-blank"
  question: string
  options?: string[]
  correctAnswer: string | number
  explanation: string
  difficulty: "easy" | "medium" | "hard"
  topic: string
}

interface QuizResult {
  questionId: string
  userAnswer: string | number
  isCorrect: boolean
  timeSpent: number
}

export default function QuizGenerator() {
  const [activeTab, setActiveTab] = useState("generate")
  const [quizSettings, setQuizSettings] = useState({
    subject: "",
    topic: "",
    numQuestions: 10,
    difficulty: "medium" as const,
    questionTypes: ["mcq", "true-false"],
    timeLimit: 15, // minutes
  })
  const [inputContent, setInputContent] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedQuiz, setGeneratedQuiz] = useState<Question[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [userAnswers, setUserAnswers] = useState<Record<string, string | number>>({})
  const [quizResults, setQuizResults] = useState<QuizResult[]>([])
  const [isQuizCompleted, setIsQuizCompleted] = useState(false)
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [isQuizActive, setIsQuizActive] = useState(false)

  const subjects = ["Mathematics", "Physics", "Chemistry", "Biology", "English", "History"]

  const sampleQuestions: Question[] = [
    {
      id: "1",
      type: "mcq",
      question: "What is the derivative of x²?",
      options: ["x", "2x", "x²", "2x²"],
      correctAnswer: 1,
      explanation: "The derivative of x² is 2x using the power rule: d/dx(xⁿ) = nxⁿ⁻¹",
      difficulty: "easy",
      topic: "Calculus",
    },
    {
      id: "2",
      type: "true-false",
      question: "The speed of light in vacuum is approximately 3 × 10⁸ m/s.",
      correctAnswer: "true",
      explanation:
        "This is correct. The speed of light in vacuum is exactly 299,792,458 m/s, approximately 3 × 10⁸ m/s.",
      difficulty: "easy",
      topic: "Physics",
    },
    {
      id: "3",
      type: "mcq",
      question: "Which organelle is responsible for photosynthesis in plant cells?",
      options: ["Mitochondria", "Chloroplast", "Nucleus", "Ribosome"],
      correctAnswer: 1,
      explanation: "Chloroplasts contain chlorophyll and are the sites where photosynthesis occurs in plant cells.",
      difficulty: "medium",
      topic: "Biology",
    },
  ]

  const generateQuiz = async () => {
    setIsGenerating(true)

    // Simulate AI quiz generation
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // For demo, use sample questions
    const quiz = sampleQuestions.slice(0, quizSettings.numQuestions)
    setGeneratedQuiz(quiz)
    setIsGenerating(false)
    setActiveTab("take")
  }

  const startQuiz = () => {
    setIsQuizActive(true)
    setTimeRemaining(quizSettings.timeLimit * 60) // Convert to seconds
    setCurrentQuestionIndex(0)
    setUserAnswers({})
    setQuizResults([])
    setIsQuizCompleted(false)
  }

  const handleAnswerSelect = (questionId: string, answer: string | number) => {
    setUserAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }))
  }

  const nextQuestion = () => {
    if (currentQuestionIndex < generatedQuiz.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1)
    } else {
      completeQuiz()
    }
  }

  const previousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prev) => prev - 1)
    }
  }

  const completeQuiz = () => {
    const results: QuizResult[] = generatedQuiz.map((question) => ({
      questionId: question.id,
      userAnswer: userAnswers[question.id] || "",
      isCorrect: userAnswers[question.id] === question.correctAnswer,
      timeSpent: 30, // Mock time spent
    }))

    setQuizResults(results)
    setIsQuizCompleted(true)
    setIsQuizActive(false)
    setActiveTab("results")
  }

  const resetQuiz = () => {
    setCurrentQuestionIndex(0)
    setUserAnswers({})
    setQuizResults([])
    setIsQuizCompleted(false)
    setIsQuizActive(false)
    setTimeRemaining(0)
  }

  const currentQuestion = generatedQuiz[currentQuestionIndex]
  const correctAnswers = quizResults.filter((r) => r.isCorrect).length
  const accuracy = quizResults.length > 0 ? Math.round((correctAnswers / quizResults.length) * 100) : 0

  const renderQuestion = (question: Question) => {
    const userAnswer = userAnswers[question.id]

    switch (question.type) {
      case "mcq":
        return (
          <RadioGroup
            value={userAnswer?.toString()}
            onValueChange={(value) => handleAnswerSelect(question.id, Number.parseInt(value))}
            className="space-y-3"
          >
            {question.options?.map((option, index) => (
              <div key={index} className="flex items-center space-x-2">
                <RadioGroupItem value={index.toString()} id={`option-${index}`} />
                <Label htmlFor={`option-${index}`} className="font-[family-name:var(--font-open-sans)] cursor-pointer">
                  {option}
                </Label>
              </div>
            ))}
          </RadioGroup>
        )

      case "true-false":
        return (
          <RadioGroup
            value={userAnswer?.toString()}
            onValueChange={(value) => handleAnswerSelect(question.id, value)}
            className="space-y-3"
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="true" id="true" />
              <Label htmlFor="true" className="font-[family-name:var(--font-open-sans)] cursor-pointer">
                True
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="false" id="false" />
              <Label htmlFor="false" className="font-[family-name:var(--font-open-sans)] cursor-pointer">
                False
              </Label>
            </div>
          </RadioGroup>
        )

      case "fill-blank":
        return (
          <Input
            value={userAnswer?.toString() || ""}
            onChange={(e) => handleAnswerSelect(question.id, e.target.value)}
            placeholder="Enter your answer"
            className="font-[family-name:var(--font-open-sans)]"
          />
        )

      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground font-[family-name:var(--font-work-sans)]">
            Quiz Generator
          </h2>
          <p className="text-muted-foreground font-[family-name:var(--font-open-sans)]">
            Create AI-powered quizzes from your study materials
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="gap-1">
            <Brain className="w-3 h-3" />
            AI Generated
          </Badge>
          <Badge variant="outline" className="gap-1">
            <Target className="w-3 h-3" />
            Adaptive Learning
          </Badge>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="generate" className="font-[family-name:var(--font-open-sans)]">
            Generate
          </TabsTrigger>
          <TabsTrigger
            value="take"
            disabled={generatedQuiz.length === 0}
            className="font-[family-name:var(--font-open-sans)]"
          >
            Take Quiz
          </TabsTrigger>
          <TabsTrigger value="results" disabled={!isQuizCompleted} className="font-[family-name:var(--font-open-sans)]">
            Results
          </TabsTrigger>
          <TabsTrigger value="history" className="font-[family-name:var(--font-open-sans)]">
            History
          </TabsTrigger>
        </TabsList>

        {/* Generate Quiz Tab */}
        <TabsContent value="generate" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 font-[family-name:var(--font-work-sans)]">
                    <Settings className="w-5 h-5 text-primary" />
                    Quiz Configuration
                  </CardTitle>
                  <CardDescription className="font-[family-name:var(--font-open-sans)]">
                    Set up your quiz parameters and content
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label className="font-[family-name:var(--font-open-sans)]">Subject</Label>
                      <Select
                        value={quizSettings.subject}
                        onValueChange={(value) => setQuizSettings({ ...quizSettings, subject: value })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select subject" />
                        </SelectTrigger>
                        <SelectContent>
                          {subjects.map((subject) => (
                            <SelectItem key={subject} value={subject}>
                              {subject}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="font-[family-name:var(--font-open-sans)]">Topic</Label>
                      <Input
                        value={quizSettings.topic}
                        onChange={(e) => setQuizSettings({ ...quizSettings, topic: e.target.value })}
                        placeholder="Enter specific topic"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label className="font-[family-name:var(--font-open-sans)]">Number of Questions</Label>
                      <Select
                        value={quizSettings.numQuestions.toString()}
                        onValueChange={(value) =>
                          setQuizSettings({ ...quizSettings, numQuestions: Number.parseInt(value) })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="5">5 Questions</SelectItem>
                          <SelectItem value="10">10 Questions</SelectItem>
                          <SelectItem value="15">15 Questions</SelectItem>
                          <SelectItem value="20">20 Questions</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="font-[family-name:var(--font-open-sans)]">Difficulty</Label>
                      <Select
                        value={quizSettings.difficulty}
                        onValueChange={(value: any) => setQuizSettings({ ...quizSettings, difficulty: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="easy">Easy</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="hard">Hard</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="font-[family-name:var(--font-open-sans)]">Time Limit (minutes)</Label>
                      <Select
                        value={quizSettings.timeLimit.toString()}
                        onValueChange={(value) =>
                          setQuizSettings({ ...quizSettings, timeLimit: Number.parseInt(value) })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="10">10 minutes</SelectItem>
                          <SelectItem value="15">15 minutes</SelectItem>
                          <SelectItem value="30">30 minutes</SelectItem>
                          <SelectItem value="60">60 minutes</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="font-[family-name:var(--font-open-sans)]">Question Types</Label>
                    <div className="flex flex-wrap gap-4">
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="mcq"
                          checked={quizSettings.questionTypes.includes("mcq")}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setQuizSettings({
                                ...quizSettings,
                                questionTypes: [...quizSettings.questionTypes, "mcq"],
                              })
                            } else {
                              setQuizSettings({
                                ...quizSettings,
                                questionTypes: quizSettings.questionTypes.filter((t) => t !== "mcq"),
                              })
                            }
                          }}
                        />
                        <Label htmlFor="mcq" className="font-[family-name:var(--font-open-sans)]">
                          Multiple Choice
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="true-false"
                          checked={quizSettings.questionTypes.includes("true-false")}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setQuizSettings({
                                ...quizSettings,
                                questionTypes: [...quizSettings.questionTypes, "true-false"],
                              })
                            } else {
                              setQuizSettings({
                                ...quizSettings,
                                questionTypes: quizSettings.questionTypes.filter((t) => t !== "true-false"),
                              })
                            }
                          }}
                        />
                        <Label htmlFor="true-false" className="font-[family-name:var(--font-open-sans)]">
                          True/False
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="fill-blank"
                          checked={quizSettings.questionTypes.includes("fill-blank")}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setQuizSettings({
                                ...quizSettings,
                                questionTypes: [...quizSettings.questionTypes, "fill-blank"],
                              })
                            } else {
                              setQuizSettings({
                                ...quizSettings,
                                questionTypes: quizSettings.questionTypes.filter((t) => t !== "fill-blank"),
                              })
                            }
                          }}
                        />
                        <Label htmlFor="fill-blank" className="font-[family-name:var(--font-open-sans)]">
                          Fill in the Blank
                        </Label>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="font-[family-name:var(--font-open-sans)]">Study Material (Optional)</Label>
                    <Textarea
                      value={inputContent}
                      onChange={(e) => setInputContent(e.target.value)}
                      placeholder="Paste your notes, textbook content, or study material here to generate targeted questions..."
                      className="min-h-[150px] font-[family-name:var(--font-open-sans)]"
                    />
                    <p className="text-sm text-muted-foreground font-[family-name:var(--font-open-sans)]">
                      {inputContent.split(" ").filter((word) => word.length > 0).length} words
                    </p>
                  </div>

                  <Button
                    onClick={generateQuiz}
                    disabled={isGenerating || !quizSettings.subject}
                    className="w-full gap-2 font-[family-name:var(--font-open-sans)]"
                    size="lg"
                  >
                    {isGenerating ? (
                      <>
                        <Zap className="w-4 h-4 animate-pulse" />
                        Generating Quiz...
                      </>
                    ) : (
                      <>
                        <Brain className="w-4 h-4" />
                        Generate AI Quiz
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Preview/Tips Sidebar */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="font-[family-name:var(--font-work-sans)]">Quiz Preview</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="font-[family-name:var(--font-open-sans)]">Questions:</span>
                    <span className="font-semibold">{quizSettings.numQuestions}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="font-[family-name:var(--font-open-sans)]">Difficulty:</span>
                    <Badge variant="outline">{quizSettings.difficulty}</Badge>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="font-[family-name:var(--font-open-sans)]">Time Limit:</span>
                    <span className="font-semibold">{quizSettings.timeLimit} min</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="font-[family-name:var(--font-open-sans)]">Question Types:</span>
                    <span className="font-semibold">{quizSettings.questionTypes.length}</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="font-[family-name:var(--font-work-sans)]">Pro Tips</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="p-3 bg-primary/10 rounded-lg border border-primary/20">
                    <p className="text-sm font-[family-name:var(--font-open-sans)]">
                      <strong>Better Questions:</strong> Provide study material for more targeted and relevant
                      questions.
                    </p>
                  </div>
                  <div className="p-3 bg-secondary/10 rounded-lg border border-secondary/20">
                    <p className="text-sm font-[family-name:var(--font-open-sans)]">
                      <strong>Mixed Types:</strong> Use different question types to test various aspects of knowledge.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Take Quiz Tab */}
        <TabsContent value="take" className="space-y-6">
          {!isQuizActive ? (
            <Card>
              <CardHeader className="text-center">
                <CardTitle className="font-[family-name:var(--font-work-sans)]">Ready to Start?</CardTitle>
                <CardDescription className="font-[family-name:var(--font-open-sans)]">
                  You have {generatedQuiz.length} questions to complete in {quizSettings.timeLimit} minutes
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center">
                <Button onClick={startQuiz} size="lg" className="gap-2 font-[family-name:var(--font-open-sans)]">
                  <Play className="w-4 h-4" />
                  Start Quiz
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {/* Quiz Header */}
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Badge variant="outline">
                        Question {currentQuestionIndex + 1} of {generatedQuiz.length}
                      </Badge>
                      <Badge variant="secondary" className="gap-1">
                        <Clock className="w-3 h-3" />
                        {Math.floor(timeRemaining / 60)}:{(timeRemaining % 60).toString().padStart(2, "0")}
                      </Badge>
                    </div>
                    <Progress value={((currentQuestionIndex + 1) / generatedQuiz.length) * 100} className="w-32" />
                  </div>
                </CardContent>
              </Card>

              {/* Current Question */}
              {currentQuestion && (
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <Badge variant="outline">{currentQuestion.difficulty}</Badge>
                      <Badge variant="secondary">{currentQuestion.topic}</Badge>
                    </div>
                    <CardTitle className="text-xl font-[family-name:var(--font-work-sans)]">
                      {currentQuestion.question}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {renderQuestion(currentQuestion)}

                    <div className="flex justify-between">
                      <Button
                        variant="outline"
                        onClick={previousQuestion}
                        disabled={currentQuestionIndex === 0}
                        className="font-[family-name:var(--font-open-sans)] bg-transparent"
                      >
                        Previous
                      </Button>
                      <Button
                        onClick={nextQuestion}
                        disabled={!userAnswers[currentQuestion.id]}
                        className="font-[family-name:var(--font-open-sans)]"
                      >
                        {currentQuestionIndex === generatedQuiz.length - 1 ? "Finish Quiz" : "Next"}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </TabsContent>

        {/* Results Tab */}
        <TabsContent value="results" className="space-y-6">
          {isQuizCompleted && (
            <>
              {/* Results Summary */}
              <Card>
                <CardHeader className="text-center">
                  <CardTitle className="flex items-center justify-center gap-2 font-[family-name:var(--font-work-sans)]">
                    <Trophy className="w-6 h-6 text-primary" />
                    Quiz Completed!
                  </CardTitle>
                  <CardDescription className="font-[family-name:var(--font-open-sans)]">
                    Here's how you performed
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                    <div>
                      <p className="text-3xl font-bold text-primary">
                        {correctAnswers}/{quizResults.length}
                      </p>
                      <p className="text-sm text-muted-foreground font-[family-name:var(--font-open-sans)]">
                        Correct Answers
                      </p>
                    </div>
                    <div>
                      <p className="text-3xl font-bold text-secondary">{accuracy}%</p>
                      <p className="text-sm text-muted-foreground font-[family-name:var(--font-open-sans)]">Accuracy</p>
                    </div>
                    <div>
                      <p className="text-3xl font-bold text-accent">{quizSettings.timeLimit} min</p>
                      <p className="text-sm text-muted-foreground font-[family-name:var(--font-open-sans)]">
                        Time Taken
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Detailed Results */}
              <Card>
                <CardHeader>
                  <CardTitle className="font-[family-name:var(--font-work-sans)]">Detailed Results</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {generatedQuiz.map((question, index) => {
                    const result = quizResults.find((r) => r.questionId === question.id)
                    const isCorrect = result?.isCorrect || false

                    return (
                      <div key={question.id} className="p-4 rounded-lg border border-border">
                        <div className="flex items-start gap-3">
                          {isCorrect ? (
                            <CheckCircle className="w-5 h-5 text-primary mt-1" />
                          ) : (
                            <XCircle className="w-5 h-5 text-destructive mt-1" />
                          )}
                          <div className="flex-1">
                            <h4 className="font-semibold font-[family-name:var(--font-work-sans)]">
                              {index + 1}. {question.question}
                            </h4>
                            <div className="mt-2 space-y-1 text-sm">
                              <p className="font-[family-name:var(--font-open-sans)]">
                                <strong>Your Answer:</strong>{" "}
                                {question.type === "mcq"
                                  ? question.options?.[result?.userAnswer as number] || "Not answered"
                                  : result?.userAnswer || "Not answered"}
                              </p>
                              <p className="font-[family-name:var(--font-open-sans)]">
                                <strong>Correct Answer:</strong>{" "}
                                {question.type === "mcq"
                                  ? question.options?.[question.correctAnswer as number]
                                  : question.correctAnswer}
                              </p>
                              <p className="text-muted-foreground font-[family-name:var(--font-open-sans)]">
                                <strong>Explanation:</strong> {question.explanation}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </CardContent>
              </Card>

              <div className="flex justify-center gap-4">
                <Button
                  onClick={resetQuiz}
                  variant="outline"
                  className="gap-2 font-[family-name:var(--font-open-sans)] bg-transparent"
                >
                  <RotateCcw className="w-4 h-4" />
                  Retake Quiz
                </Button>
                <Button
                  onClick={() => setActiveTab("generate")}
                  className="gap-2 font-[family-name:var(--font-open-sans)]"
                >
                  <Plus className="w-4 h-4" />
                  Generate New Quiz
                </Button>
              </div>
            </>
          )}
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-[family-name:var(--font-work-sans)]">
                <BarChart3 className="w-5 h-5 text-primary" />
                Quiz History
              </CardTitle>
              <CardDescription className="font-[family-name:var(--font-open-sans)]">
                Track your progress over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <BookOpen className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground font-[family-name:var(--font-open-sans)]">
                  No quiz history yet. Complete some quizzes to see your progress!
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
