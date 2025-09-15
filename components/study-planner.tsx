"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Calendar, Clock, Plus, BookOpen, Target, Zap, ChevronLeft, ChevronRight, Edit, Trash2 } from "lucide-react"

interface StudyTask {
  id: string
  subject: string
  topic: string
  duration: number
  priority: "high" | "medium" | "low"
  date: string
  time: string
  status: "pending" | "completed" | "in-progress"
  description?: string
}

export default function StudyPlanner() {
  const [currentWeek, setCurrentWeek] = useState(0)
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0])
  const [isAddTaskOpen, setIsAddTaskOpen] = useState(false)
  const [newTask, setNewTask] = useState({
    subject: "",
    topic: "",
    duration: 60,
    priority: "medium" as const,
    description: "",
  })

  const [tasks, setTasks] = useState<StudyTask[]>([
    {
      id: "1",
      subject: "Mathematics",
      topic: "Calculus - Derivatives",
      duration: 120,
      priority: "high",
      date: "2024-01-15",
      time: "14:00",
      status: "pending",
      description: "Focus on chain rule and product rule applications",
    },
    {
      id: "2",
      subject: "Physics",
      topic: "Quantum Mechanics",
      duration: 90,
      priority: "medium",
      date: "2024-01-15",
      time: "16:00",
      status: "completed",
      description: "Wave-particle duality and uncertainty principle",
    },
    {
      id: "3",
      subject: "Chemistry",
      topic: "Organic Reactions",
      duration: 75,
      priority: "medium",
      date: "2024-01-16",
      time: "10:00",
      status: "pending",
      description: "Substitution and elimination reactions",
    },
  ])

  const weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
  const subjects = ["Mathematics", "Physics", "Chemistry", "Biology", "English", "History"]

  const getWeekDates = (weekOffset: number) => {
    const today = new Date()
    const startOfWeek = new Date(today.setDate(today.getDate() - today.getDay() + 1 + weekOffset * 7))
    return Array.from({ length: 7 }, (_, i) => {
      const date = new Date(startOfWeek)
      date.setDate(startOfWeek.getDate() + i)
      return date.toISOString().split("T")[0]
    })
  }

  const currentWeekDates = getWeekDates(currentWeek)
  const tasksForSelectedDate = tasks.filter((task) => task.date === selectedDate)

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-destructive text-destructive-foreground"
      case "medium":
        return "bg-secondary text-secondary-foreground"
      case "low":
        return "bg-muted text-muted-foreground"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-primary text-primary-foreground"
      case "in-progress":
        return "bg-accent text-accent-foreground"
      case "pending":
        return "bg-muted text-muted-foreground"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  const handleAddTask = () => {
    const task: StudyTask = {
      id: Date.now().toString(),
      ...newTask,
      date: selectedDate,
      time: "09:00",
      status: "pending",
    }
    setTasks([...tasks, task])
    setNewTask({
      subject: "",
      topic: "",
      duration: 60,
      priority: "medium",
      description: "",
    })
    setIsAddTaskOpen(false)
  }

  const toggleTaskStatus = (taskId: string) => {
    setTasks(
      tasks.map((task) => {
        if (task.id === taskId) {
          const newStatus = task.status === "pending" ? "completed" : "pending"
          return { ...task, status: newStatus }
        }
        return task
      }),
    )
  }

  const generateAISchedule = () => {
    // Simulate AI schedule generation
    alert("AI is generating your personalized study schedule based on your learning patterns and upcoming exams!")
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground font-[family-name:var(--font-work-sans)]">
            Smart Study Planner
          </h2>
          <p className="text-muted-foreground font-[family-name:var(--font-open-sans)]">
            AI-powered personalized study scheduling
          </p>
        </div>
        <div className="flex gap-3">
          <Button onClick={generateAISchedule} className="gap-2 font-[family-name:var(--font-open-sans)]">
            <Zap className="w-4 h-4" />
            Generate AI Schedule
          </Button>
          <Dialog open={isAddTaskOpen} onOpenChange={setIsAddTaskOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="gap-2 font-[family-name:var(--font-open-sans)] bg-transparent">
                <Plus className="w-4 h-4" />
                Add Task
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle className="font-[family-name:var(--font-work-sans)]">Add Study Task</DialogTitle>
                <DialogDescription className="font-[family-name:var(--font-open-sans)]">
                  Create a new study task for your schedule
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="subject" className="font-[family-name:var(--font-open-sans)]">
                    Subject
                  </Label>
                  <Select value={newTask.subject} onValueChange={(value) => setNewTask({ ...newTask, subject: value })}>
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
                  <Label htmlFor="topic" className="font-[family-name:var(--font-open-sans)]">
                    Topic
                  </Label>
                  <Input
                    id="topic"
                    value={newTask.topic}
                    onChange={(e) => setNewTask({ ...newTask, topic: e.target.value })}
                    placeholder="Enter topic to study"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="duration" className="font-[family-name:var(--font-open-sans)]">
                      Duration (minutes)
                    </Label>
                    <Input
                      id="duration"
                      type="number"
                      value={newTask.duration}
                      onChange={(e) => setNewTask({ ...newTask, duration: Number.parseInt(e.target.value) })}
                      min="15"
                      max="300"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="priority" className="font-[family-name:var(--font-open-sans)]">
                      Priority
                    </Label>
                    <Select
                      value={newTask.priority}
                      onValueChange={(value: any) => setNewTask({ ...newTask, priority: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="low">Low</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description" className="font-[family-name:var(--font-open-sans)]">
                    Description (Optional)
                  </Label>
                  <Textarea
                    id="description"
                    value={newTask.description}
                    onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                    placeholder="Add notes or specific focus areas"
                    rows={3}
                  />
                </div>
                <Button onClick={handleAddTask} className="w-full font-[family-name:var(--font-open-sans)]">
                  Add Task
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Week Navigation */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 font-[family-name:var(--font-work-sans)]">
              <Calendar className="w-5 h-5 text-primary" />
              Weekly View
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentWeek(currentWeek - 1)}
                className="font-[family-name:var(--font-open-sans)]"
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentWeek(0)}
                className="font-[family-name:var(--font-open-sans)]"
              >
                Today
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentWeek(currentWeek + 1)}
                className="font-[family-name:var(--font-open-sans)]"
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-7 gap-2">
            {weekDays.map((day, index) => {
              const date = currentWeekDates[index]
              const dayTasks = tasks.filter((task) => task.date === date)
              const isSelected = date === selectedDate
              const isToday = date === new Date().toISOString().split("T")[0]

              return (
                <div
                  key={day}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-primary text-primary-foreground border-primary"
                      : isToday
                        ? "bg-accent text-accent-foreground border-accent"
                        : "bg-card hover:bg-muted border-border"
                  }`}
                  onClick={() => setSelectedDate(date)}
                >
                  <div className="text-center">
                    <p className="text-sm font-medium font-[family-name:var(--font-open-sans)]">{day}</p>
                    <p className="text-lg font-bold font-[family-name:var(--font-work-sans)]">
                      {new Date(date).getDate()}
                    </p>
                    <div className="mt-2 space-y-1">
                      {dayTasks.slice(0, 2).map((task) => (
                        <div
                          key={task.id}
                          className={`w-full h-1 rounded-full ${
                            task.status === "completed" ? "bg-green-500" : "bg-orange-500"
                          }`}
                        />
                      ))}
                      {dayTasks.length > 2 && <p className="text-xs opacity-70">+{dayTasks.length - 2} more</p>}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Selected Date Tasks */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="font-[family-name:var(--font-work-sans)]">
                Tasks for{" "}
                {new Date(selectedDate).toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </CardTitle>
              <CardDescription className="font-[family-name:var(--font-open-sans)]">
                {tasksForSelectedDate.length} tasks scheduled
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {tasksForSelectedDate.length === 0 ? (
                <div className="text-center py-8">
                  <BookOpen className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground font-[family-name:var(--font-open-sans)]">
                    No tasks scheduled for this date. Add a task to get started!
                  </p>
                </div>
              ) : (
                tasksForSelectedDate.map((task) => (
                  <div
                    key={task.id}
                    className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <button
                        onClick={() => toggleTaskStatus(task.id)}
                        className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                          task.status === "completed"
                            ? "bg-primary border-primary"
                            : "border-muted-foreground hover:border-primary"
                        }`}
                      >
                        {task.status === "completed" && <div className="w-2 h-2 bg-primary-foreground rounded-full" />}
                      </button>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold text-foreground font-[family-name:var(--font-work-sans)]">
                            {task.subject}
                          </h4>
                          <Badge className={getPriorityColor(task.priority)}>{task.priority}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground font-[family-name:var(--font-open-sans)]">
                          {task.topic}
                        </p>
                        {task.description && (
                          <p className="text-xs text-muted-foreground mt-1 font-[family-name:var(--font-open-sans)]">
                            {task.description}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <Clock className="w-4 h-4" />
                          {task.duration}min
                        </div>
                        <Badge className={getStatusColor(task.status)}>{task.status}</Badge>
                      </div>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm">
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>

        {/* Study Stats */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-[family-name:var(--font-work-sans)]">
                <Target className="w-5 h-5 text-primary" />
                Daily Goals
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-[family-name:var(--font-open-sans)]">Study Hours</span>
                <span className="font-semibold">3.5 / 6 hrs</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-primary h-2 rounded-full" style={{ width: "58%" }} />
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm font-[family-name:var(--font-open-sans)]">Tasks Completed</span>
                <span className="font-semibold">2 / 5</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-secondary h-2 rounded-full" style={{ width: "40%" }} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="font-[family-name:var(--font-work-sans)]">AI Insights</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-3 bg-primary/10 rounded-lg border border-primary/20">
                <p className="text-sm font-[family-name:var(--font-open-sans)]">
                  <strong>Tip:</strong> Your focus is highest between 2-4 PM. Schedule challenging topics during this
                  time.
                </p>
              </div>
              <div className="p-3 bg-secondary/10 rounded-lg border border-secondary/20">
                <p className="text-sm font-[family-name:var(--font-open-sans)]">
                  <strong>Reminder:</strong> Take a 15-minute break every hour for better retention.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
