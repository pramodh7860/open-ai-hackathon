"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  MessageCircle,
  Send,
  Bot,
  User,
  Lightbulb,
  BookOpen,
  Calculator,
  Atom,
  Beaker,
  Dna,
  Globe,
  Clock,
  ThumbsUp,
  ThumbsDown,
  Copy,
  Sparkles,
  Mic,
  ImageIcon,
} from "lucide-react"

interface Message {
  id: string
  type: "user" | "bot"
  content: string
  timestamp: Date
  subject?: string
  helpful?: boolean
  attachments?: string[]
}

interface QuickQuestion {
  id: string
  question: string
  subject: string
  icon: any
}

export default function DoubtSolver() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "bot",
      content:
        "Hi! I'm your AI study assistant. I'm here to help you with any doubts or questions you have about your studies. What would you like to learn about today?",
      timestamp: new Date(),
    },
  ])
  const [inputMessage, setInputMessage] = useState("")
  const [selectedSubject, setSelectedSubject] = useState("general")
  const [isTyping, setIsTyping] = useState(false)
  const [activeTab, setActiveTab] = useState("chat")
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const subjects = [
    { value: "general", label: "General", icon: MessageCircle },
    { value: "mathematics", label: "Mathematics", icon: Calculator },
    { value: "physics", label: "Physics", icon: Atom },
    { value: "chemistry", label: "Chemistry", icon: Beaker },
    { value: "biology", label: "Biology", icon: Dna },
    { value: "english", label: "English", icon: BookOpen },
    { value: "history", label: "History", icon: Globe },
  ]

  const quickQuestions: QuickQuestion[] = [
    {
      id: "1",
      question: "Explain the concept of derivatives in calculus",
      subject: "Mathematics",
      icon: Calculator,
    },
    {
      id: "2",
      question: "What is Newton's second law of motion?",
      subject: "Physics",
      icon: Atom,
    },
    {
      id: "3",
      question: "How does photosynthesis work?",
      subject: "Biology",
      icon: Dna,
    },
    {
      id: "4",
      question: "What are the types of chemical bonds?",
      subject: "Chemistry",
      icon: Beaker,
    },
  ]

  const recentChats = [
    {
      id: "1",
      title: "Calculus Derivatives",
      lastMessage: "Thanks for explaining the chain rule!",
      timestamp: new Date("2024-01-15T14:30:00"),
      subject: "Mathematics",
    },
    {
      id: "2",
      title: "Quantum Physics",
      lastMessage: "What is wave-particle duality?",
      timestamp: new Date("2024-01-14T16:45:00"),
      subject: "Physics",
    },
    {
      id: "3",
      title: "Organic Chemistry",
      lastMessage: "Explain substitution reactions",
      timestamp: new Date("2024-01-13T10:20:00"),
      subject: "Chemistry",
    },
  ]

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputMessage,
      timestamp: new Date(),
      subject: selectedSubject,
    }

    setMessages((prev) => [...prev, userMessage])
    setInputMessage("")
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      const botResponse = generateBotResponse(inputMessage, selectedSubject)
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: botResponse,
        timestamp: new Date(),
        subject: selectedSubject,
      }
      setMessages((prev) => [...prev, botMessage])
      setIsTyping(false)
    }, 1500)
  }

  const generateBotResponse = (question: string, subject: string): string => {
    // Simple mock responses based on subject and keywords
    const lowerQuestion = question.toLowerCase()

    if (lowerQuestion.includes("derivative") || lowerQuestion.includes("calculus")) {
      return "Great question about derivatives! A derivative represents the rate of change of a function. For example, if f(x) = x², then f'(x) = 2x. This means at any point x, the slope of the tangent line is 2x. The derivative tells us how fast the function is changing at that specific point. Would you like me to explain any specific derivative rules like the power rule, product rule, or chain rule?"
    }

    if (lowerQuestion.includes("newton") || lowerQuestion.includes("force")) {
      return "Newton's laws are fundamental to understanding motion! Newton's Second Law states that F = ma, where F is the net force, m is mass, and a is acceleration. This means that the acceleration of an object is directly proportional to the net force acting on it and inversely proportional to its mass. For example, if you push a heavy box and a light box with the same force, the light box will accelerate more. Would you like examples or want to discuss the other laws of motion?"
    }

    if (lowerQuestion.includes("photosynthesis") || lowerQuestion.includes("plant")) {
      return "Photosynthesis is how plants make their own food! The process can be summarized as: 6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂. It happens in two main stages: Light reactions (in thylakoids) capture light energy and produce ATP and NADPH, while the Calvin cycle (in stroma) uses this energy to convert CO₂ into glucose. Chlorophyll is the green pigment that captures light energy. Would you like me to explain either stage in more detail?"
    }

    if (lowerQuestion.includes("bond") || lowerQuestion.includes("chemical")) {
      return "Chemical bonds hold atoms together! There are three main types: 1) Ionic bonds - formed when electrons are transferred between atoms (like NaCl), 2) Covalent bonds - formed when electrons are shared between atoms (like H₂O), and 3) Metallic bonds - found in metals where electrons move freely. The type of bond depends on the electronegativity difference between atoms. Would you like me to explain any specific type in more detail or give more examples?"
    }

    // Default response
    return `That's an interesting question about ${subject}! I'd be happy to help you understand this concept better. Could you provide a bit more context or specify which aspect you'd like me to focus on? This will help me give you a more detailed and targeted explanation.`
  }

  const handleQuickQuestion = (question: string) => {
    setInputMessage(question)
    inputRef.current?.focus()
  }

  const handleMessageFeedback = (messageId: string, helpful: boolean) => {
    setMessages((prev) => prev.map((msg) => (msg.id === messageId ? { ...msg, helpful } : msg)))
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground font-[family-name:var(--font-work-sans)]">Doubt Solver</h2>
          <p className="text-muted-foreground font-[family-name:var(--font-open-sans)]">
            Get instant help with your study questions from AI
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="gap-1">
            <Sparkles className="w-3 h-3" />
            AI Powered
          </Badge>
          <Badge variant="outline" className="gap-1">
            <Clock className="w-3 h-3" />
            24/7 Available
          </Badge>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="chat" className="font-[family-name:var(--font-open-sans)]">
            Chat
          </TabsTrigger>
          <TabsTrigger value="quick" className="font-[family-name:var(--font-open-sans)]">
            Quick Help
          </TabsTrigger>
          <TabsTrigger value="history" className="font-[family-name:var(--font-open-sans)]">
            History
          </TabsTrigger>
        </TabsList>

        {/* Chat Tab */}
        <TabsContent value="chat" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Main Chat Area */}
            <div className="lg:col-span-3">
              <Card className="h-[600px] flex flex-col">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 font-[family-name:var(--font-work-sans)]">
                      <Bot className="w-5 h-5 text-primary" />
                      AI Study Assistant
                    </CardTitle>
                    <Select value={selectedSubject} onValueChange={setSelectedSubject}>
                      <SelectTrigger className="w-40">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {subjects.map((subject) => (
                          <SelectItem key={subject.value} value={subject.value}>
                            <div className="flex items-center gap-2">
                              <subject.icon className="w-4 h-4" />
                              {subject.label}
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </CardHeader>

                <CardContent className="flex-1 flex flex-col p-0">
                  {/* Messages */}
                  <ScrollArea className="flex-1 p-4">
                    <div className="space-y-4">
                      {messages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex gap-3 ${message.type === "user" ? "justify-end" : "justify-start"}`}
                        >
                          {message.type === "bot" && (
                            <Avatar className="w-8 h-8 bg-primary">
                              <AvatarFallback>
                                <Bot className="w-4 h-4 text-primary-foreground" />
                              </AvatarFallback>
                            </Avatar>
                          )}

                          <div className={`max-w-[80%] ${message.type === "user" ? "order-first" : ""}`}>
                            <div
                              className={`rounded-lg p-3 ${
                                message.type === "user" ? "bg-primary text-primary-foreground ml-auto" : "bg-muted"
                              }`}
                            >
                              <p className="text-sm font-[family-name:var(--font-open-sans)] leading-relaxed">
                                {message.content}
                              </p>
                            </div>

                            <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                              <span>{formatTime(message.timestamp)}</span>
                              {message.subject && message.subject !== "general" && (
                                <Badge variant="outline" className="text-xs">
                                  {subjects.find((s) => s.value === message.subject)?.label}
                                </Badge>
                              )}

                              {message.type === "bot" && (
                                <div className="flex items-center gap-1 ml-auto">
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-6 w-6 p-0"
                                    onClick={() => copyMessage(message.content)}
                                  >
                                    <Copy className="w-3 h-3" />
                                  </Button>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className={`h-6 w-6 p-0 ${message.helpful === true ? "text-primary" : ""}`}
                                    onClick={() => handleMessageFeedback(message.id, true)}
                                  >
                                    <ThumbsUp className="w-3 h-3" />
                                  </Button>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className={`h-6 w-6 p-0 ${message.helpful === false ? "text-destructive" : ""}`}
                                    onClick={() => handleMessageFeedback(message.id, false)}
                                  >
                                    <ThumbsDown className="w-3 h-3" />
                                  </Button>
                                </div>
                              )}
                            </div>
                          </div>

                          {message.type === "user" && (
                            <Avatar className="w-8 h-8 bg-secondary">
                              <AvatarFallback>
                                <User className="w-4 h-4 text-secondary-foreground" />
                              </AvatarFallback>
                            </Avatar>
                          )}
                        </div>
                      ))}

                      {isTyping && (
                        <div className="flex gap-3 justify-start">
                          <Avatar className="w-8 h-8 bg-primary">
                            <AvatarFallback>
                              <Bot className="w-4 h-4 text-primary-foreground" />
                            </AvatarFallback>
                          </Avatar>
                          <div className="bg-muted rounded-lg p-3">
                            <div className="flex gap-1">
                              <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                              <div
                                className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                                style={{ animationDelay: "0.1s" }}
                              />
                              <div
                                className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                                style={{ animationDelay: "0.2s" }}
                              />
                            </div>
                          </div>
                        </div>
                      )}
                      <div ref={messagesEndRef} />
                    </div>
                  </ScrollArea>

                  {/* Input Area */}
                  <div className="border-t p-4">
                    <div className="flex gap-2">
                      <div className="flex-1 relative">
                        <Input
                          ref={inputRef}
                          value={inputMessage}
                          onChange={(e) => setInputMessage(e.target.value)}
                          placeholder="Ask me anything about your studies..."
                          className="pr-20 font-[family-name:var(--font-open-sans)]"
                          onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                        />
                        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-1">
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                            <ImageIcon className="w-3 h-3" />
                          </Button>
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                            <ImageIcon className="w-3 h-3" />
                          </Button>
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                            <Mic className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                      <Button
                        onClick={handleSendMessage}
                        disabled={!inputMessage.trim() || isTyping}
                        className="gap-2 font-[family-name:var(--font-open-sans)]"
                      >
                        <Send className="w-4 h-4" />
                        Send
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="space-y-4">
              {/* Quick Questions */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-[family-name:var(--font-work-sans)]">Quick Questions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {quickQuestions.map((q) => (
                    <Button
                      key={q.id}
                      variant="outline"
                      className="w-full justify-start text-left h-auto p-3 font-[family-name:var(--font-open-sans)] bg-transparent"
                      onClick={() => handleQuickQuestion(q.question)}
                    >
                      <div className="flex items-start gap-2">
                        <q.icon className="w-4 h-4 mt-0.5 text-primary" />
                        <div>
                          <p className="text-xs text-muted-foreground">{q.subject}</p>
                          <p className="text-sm">{q.question}</p>
                        </div>
                      </div>
                    </Button>
                  ))}
                </CardContent>
              </Card>

              {/* Study Tips */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm font-[family-name:var(--font-work-sans)]">
                    <Lightbulb className="w-4 h-4 text-primary" />
                    Study Tips
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="p-3 bg-primary/10 rounded-lg border border-primary/20">
                    <p className="text-sm font-[family-name:var(--font-open-sans)]">
                      <strong>Be Specific:</strong> Ask detailed questions for better explanations.
                    </p>
                  </div>
                  <div className="p-3 bg-secondary/10 rounded-lg border border-secondary/20">
                    <p className="text-sm font-[family-name:var(--font-open-sans)]">
                      <strong>Follow Up:</strong> Ask for examples or clarifications if needed.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Quick Help Tab */}
        <TabsContent value="quick" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {subjects.slice(1).map((subject) => (
              <Card key={subject.value} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 font-[family-name:var(--font-work-sans)]">
                    <subject.icon className="w-5 h-5 text-primary" />
                    {subject.label}
                  </CardTitle>
                  <CardDescription className="font-[family-name:var(--font-open-sans)]">
                    Get help with {subject.label.toLowerCase()} concepts
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="outline"
                    className="w-full font-[family-name:var(--font-open-sans)] bg-transparent"
                    onClick={() => {
                      setSelectedSubject(subject.value)
                      setActiveTab("chat")
                    }}
                  >
                    Start {subject.label} Chat
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="font-[family-name:var(--font-work-sans)]">Recent Conversations</CardTitle>
              <CardDescription className="font-[family-name:var(--font-open-sans)]">
                Your previous chat sessions
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {recentChats.map((chat) => (
                <div
                  key={chat.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                      <MessageCircle className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-foreground font-[family-name:var(--font-work-sans)]">
                        {chat.title}
                      </h4>
                      <p className="text-sm text-muted-foreground font-[family-name:var(--font-open-sans)]">
                        {chat.lastMessage}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant="outline">{chat.subject}</Badge>
                    <p className="text-xs text-muted-foreground mt-1">{chat.timestamp.toLocaleDateString()}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
