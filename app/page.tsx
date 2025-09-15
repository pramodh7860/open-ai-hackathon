"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import StudyPlanner from "@/components/study-planner"
import AISummarizer from "@/components/ai-summarizer"
import QuizGenerator from "@/components/quiz-generator"
import DoubtSolver from "@/components/doubt-solver"
import AuthModal from "@/components/auth-modal"
import UserProfile from "@/components/user-profile"
import {
  BookOpen,
  Brain,
  MessageCircle,
  Calendar,
  Clock,
  Target,
  TrendingUp,
  Award,
  ChevronRight,
  LogIn,
} from "lucide-react"

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview")
  const [isLoading, setIsLoading] = useState(true)
  const [user, setUser] = useState<any>(null)
  const [showAuthModal, setShowAuthModal] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 300)
    return () => clearTimeout(timer)
  }, [])

  const handleLogin = (userData: any) => {
    setUser(userData)
    setShowAuthModal(false)
  }

  const handleLogout = () => {
    setUser(null)
  }

  const todaysTasks = [
    { subject: "Mathematics", topic: "Calculus - Derivatives", time: "2:00 PM", status: "pending" },
    { subject: "Physics", topic: "Quantum Mechanics", time: "4:00 PM", status: "completed" },
    { subject: "Chemistry", topic: "Organic Reactions", time: "6:00 PM", status: "pending" },
  ]

  const weeklyProgress = [
    { subject: "Mathematics", progress: 85 },
    { subject: "Physics", progress: 72 },
    { subject: "Chemistry", progress: 68 },
    { subject: "Biology", progress: 91 },
  ]

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
            <Brain className="w-6 h-6 text-primary-foreground" />
          </div>
          <p className="text-muted-foreground">Loading StudyBuddy...</p>
        </div>
      </div>
    )
  }

  const renderContent = () => {
    switch (activeTab) {
      case "planner":
        return <StudyPlanner />
      case "summarizer":
        return <AISummarizer />
      case "quiz":
        return <QuizGenerator />
      case "chat":
        return <DoubtSolver />
      case "overview":
      default:
        return (
          <>
            <div className="relative mb-12 rounded-2xl overflow-hidden">
              <img
                src="/students-studying-together-in-modern-library-with-.jpg"
                alt="Students studying"
                className="w-full h-64 object-cover"
              />
              <div className="absolute inset-0 bg-slate-900/90 z-10" />
              <div className="absolute inset-0 z-20 flex items-center justify-center text-center p-8">
                <div className="animate-fade-in bg-slate-800/50 rounded-xl p-8 backdrop-blur-sm">
                  <h2 className="text-4xl font-bold text-white mb-4">
                    Good morning, {user ? user.name.split(" ")[0] : "Student"}!
                  </h2>
                  <p className="text-gray-100 text-xl animate-slide-up animate-delay-100 max-w-2xl">
                    {user
                      ? "You have 3 study sessions planned for today. Let's make today productive and achieve your learning goals."
                      : "Welcome to StudyBuddy! Sign in to track your progress and access personalized study tools."}
                  </p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card className="hover-lift animate-scale-in relative overflow-hidden">
                <div className="absolute inset-0 opacity-10">
                  <img
                    src="/target-achievement-success-illustration.jpg"
                    alt=""
                    className="w-full h-full object-cover"
                  />
                </div>
                <CardContent className="p-6 relative z-10">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Study Streak</p>
                      <p className="text-2xl font-bold text-primary">{user ? "12 days" : "--"}</p>
                    </div>
                    <Target className="w-8 h-8 text-primary" />
                  </div>
                </CardContent>
              </Card>

              <Card className="hover-lift animate-scale-in animate-delay-100 relative overflow-hidden">
                <div className="absolute inset-0 opacity-10">
                  <img src="/clock-time-management-productivity.jpg" alt="" className="w-full h-full object-cover" />
                </div>
                <CardContent className="p-6 relative z-10">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Hours Today</p>
                      <p className="text-2xl font-bold text-secondary">{user ? "3.5 hrs" : "--"}</p>
                    </div>
                    <Clock className="w-8 h-8 text-secondary" />
                  </div>
                </CardContent>
              </Card>

              <Card className="hover-lift animate-scale-in animate-delay-200 relative overflow-hidden">
                <div className="absolute inset-0 opacity-10">
                  <img src="/trophy-award-achievement-medal.jpg" alt="" className="w-full h-full object-cover" />
                </div>
                <CardContent className="p-6 relative z-10">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Quizzes Done</p>
                      <p className="text-2xl font-bold text-accent">{user ? "24" : "--"}</p>
                    </div>
                    <Award className="w-8 h-8 text-accent" />
                  </div>
                </CardContent>
              </Card>

              <Card className="hover-lift animate-scale-in animate-delay-300 relative overflow-hidden">
                <div className="absolute inset-0 opacity-10">
                  <img src="/growth-chart-progress-trending-up.jpg" alt="" className="w-full h-full object-cover" />
                </div>
                <CardContent className="p-6 relative z-10">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Progress</p>
                      <p className="text-2xl font-bold text-chart-1">{user ? "79%" : "--"}</p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-chart-1" />
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <Card className="hover-lift animate-slide-up">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Calendar className="w-5 h-5 text-primary" />
                      Today's Schedule
                    </CardTitle>
                    <CardDescription>
                      {user ? "Your study plan for today" : "Sign in to see your personalized schedule"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {user ? (
                      todaysTasks.map((task, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors animate-fade-in relative overflow-hidden"
                          style={{ animationDelay: `${(index + 1) * 0.1}s` }}
                        >
                          <div className="absolute inset-0 opacity-5">
                            <img
                              src={`/abstract-geometric-shapes.png?height=100&width=400&query=${task.subject.toLowerCase()} textbook study materials`}
                              alt=""
                              className="w-full h-full object-cover"
                            />
                          </div>
                          <div className="flex items-center gap-4 relative z-10">
                            <div
                              className={`w-3 h-3 rounded-full ${
                                task.status === "completed" ? "bg-primary" : "bg-muted-foreground"
                              }`}
                            />
                            <div>
                              <h4 className="font-semibold text-foreground">{task.subject}</h4>
                              <p className="text-sm text-muted-foreground">{task.topic}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-3 relative z-10">
                            <Badge variant={task.status === "completed" ? "default" : "secondary"}>
                              {task.status === "completed" ? "Done" : task.time}
                            </Badge>
                            <ChevronRight className="w-4 h-4 text-muted-foreground" />
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-muted-foreground mb-4">Sign in to access your personalized study schedule</p>
                        <Button onClick={() => setShowAuthModal(true)}>
                          <LogIn className="w-4 h-4 mr-2" />
                          Sign In
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-6">
                <Card className="hover-lift animate-slide-up animate-delay-100 relative overflow-hidden">
                  <div className="absolute inset-0 opacity-5">
                    <img
                      src="/artificial-intelligence-brain-technology-digital-l.jpg"
                      alt=""
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <CardHeader className="relative z-10">
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="w-5 h-5 text-primary" />
                      Study Tools
                    </CardTitle>
                    <CardDescription>AI-powered learning assistance</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3 relative z-10">
                    <Button
                      variant="outline"
                      className="w-full justify-start gap-3 h-12 hover-lift bg-transparent"
                      onClick={() => setActiveTab("summarizer")}
                    >
                      <BookOpen className="w-5 h-5 text-primary" />
                      Summarizer
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full justify-start gap-3 h-12 hover-lift bg-transparent"
                      onClick={() => setActiveTab("quiz")}
                    >
                      <Brain className="w-5 h-5 text-secondary" />
                      Quiz Generator
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full justify-start gap-3 h-12 hover-lift bg-transparent"
                      onClick={() => setActiveTab("chat")}
                    >
                      <MessageCircle className="w-5 h-5 text-accent" />
                      Ask Questions
                    </Button>
                  </CardContent>
                </Card>

                <Card className="hover-lift animate-slide-up animate-delay-200">
                  <CardHeader>
                    <CardTitle>Weekly Progress</CardTitle>
                    <CardDescription>
                      {user ? "How you're doing this week" : "Sign in to track your progress"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {user ? (
                      weeklyProgress.map((subject, index) => (
                        <div
                          key={index}
                          className="space-y-2 animate-fade-in"
                          style={{ animationDelay: `${(index + 3) * 0.1}s` }}
                        >
                          <div className="flex justify-between text-sm">
                            <span className="font-medium text-foreground">{subject.subject}</span>
                            <span className="text-muted-foreground">{subject.progress}%</span>
                          </div>
                          <Progress value={subject.progress} className="h-2" />
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-4">
                        <p className="text-muted-foreground text-sm">Sign in to see your progress</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>

            <div className="mt-12 text-center animate-slide-up animate-delay-300">
              <Card className="hover-lift relative overflow-hidden">
                <div className="absolute inset-0 opacity-10">
                  <img
                    src="/motivated-students-celebrating-success-graduation-.jpg"
                    alt=""
                    className="w-full h-full object-cover"
                  />
                </div>
                <CardContent className="p-8 relative z-10">
                  <h3 className="text-2xl font-bold text-foreground mb-4">Ready to study?</h3>
                  <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
                    Use our tools to create study plans, summarize your notes, practice with quizzes, and get help when
                    you're stuck.
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Button size="lg" className="btn-enhanced">
                      Start Studying
                    </Button>
                    <Button variant="outline" size="lg" className="btn-enhanced bg-transparent">
                      Browse Tools
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        )
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50 animate-slide-up">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-primary-foreground" />
              </div>
              <h1 className="text-2xl font-bold text-foreground">StudyBuddy</h1>
            </div>

            <div className="flex items-center gap-4">
              <nav className="hidden md:flex items-center gap-6">
                {[
                  { key: "overview", label: "Overview" },
                  { key: "planner", label: "Planner" },
                  { key: "summarizer", label: "Summarizer" },
                  { key: "quiz", label: "Quiz" },
                  { key: "chat", label: "Chat" },
                ].map((tab, index) => (
                  <Button
                    key={tab.key}
                    variant={activeTab === tab.key ? "default" : "ghost"}
                    onClick={() => setActiveTab(tab.key)}
                    className="transition-all duration-200 animate-fade-in"
                    style={{ animationDelay: `${index * 0.05}s` }}
                  >
                    {tab.label}
                  </Button>
                ))}
              </nav>

              {user ? (
                <UserProfile user={user} onLogout={handleLogout} />
              ) : (
                <Button onClick={() => setShowAuthModal(true)} className="flex items-center gap-2">
                  <LogIn className="w-4 h-4" />
                  Sign In
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">{renderContent()}</main>

      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} onLogin={handleLogin} />
    </div>
  )
}
