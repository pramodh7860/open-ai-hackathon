"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import {
  FileText,
  Upload,
  Sparkles,
  Copy,
  Download,
  Languages,
  BookOpen,
  Clock,
  Target,
  Zap,
  CheckCircle,
} from "lucide-react"

interface Summary {
  id: string
  title: string
  originalLength: number
  summaryLength: number
  language: string
  type: "bullet" | "paragraph" | "detailed"
  content: string
  timestamp: Date
}

export default function AISummarizer() {
  const [inputText, setInputText] = useState("")
  const [summaryType, setSummaryType] = useState<"bullet" | "paragraph" | "detailed">("bullet")
  const [language, setLanguage] = useState("english")
  const [isGenerating, setIsGenerating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentSummary, setCurrentSummary] = useState<Summary | null>(null)
  const [recentSummaries, setRecentSummaries] = useState<Summary[]>([
    {
      id: "1",
      title: "Quantum Mechanics Basics",
      originalLength: 2500,
      summaryLength: 450,
      language: "english",
      type: "bullet",
      content:
        "• Quantum mechanics describes the behavior of matter and energy at atomic and subatomic scales\n• Wave-particle duality shows that particles exhibit both wave and particle properties\n• The uncertainty principle states that position and momentum cannot be precisely determined simultaneously\n• Quantum superposition allows particles to exist in multiple states until observed\n• Quantum entanglement creates correlations between particles regardless of distance",
      timestamp: new Date("2024-01-15T10:30:00"),
    },
    {
      id: "2",
      title: "Photosynthesis Process",
      originalLength: 1800,
      summaryLength: 320,
      language: "english",
      type: "paragraph",
      content:
        "Photosynthesis is the process by which plants convert light energy into chemical energy. It occurs in two main stages: light-dependent reactions in the thylakoids and light-independent reactions in the stroma. During the light reactions, chlorophyll absorbs photons and splits water molecules, releasing oxygen and generating ATP and NADPH. The Calvin cycle then uses these energy carriers to fix carbon dioxide into glucose through a series of enzymatic reactions.",
      timestamp: new Date("2024-01-14T15:45:00"),
    },
  ])

  const languages = [
    { value: "english", label: "English" },
    { value: "hindi", label: "हिंदी (Hindi)" },
    { value: "tamil", label: "தமிழ் (Tamil)" },
    { value: "bengali", label: "বাংলা (Bengali)" },
    { value: "telugu", label: "తెలుగు (Telugu)" },
    { value: "marathi", label: "मराठी (Marathi)" },
  ]

  const generateSummary = async () => {
    if (!inputText.trim()) return

    setIsGenerating(true)
    setProgress(0)

    // Simulate AI processing with progress updates
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + 10
      })
    }, 200)

    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 2000))

    setProgress(100)

    // Generate mock summary based on type
    let summaryContent = ""
    const wordCount = inputText.split(" ").length

    switch (summaryType) {
      case "bullet":
        summaryContent = `• Key concept 1: ${inputText.substring(0, 50)}...\n• Key concept 2: Advanced principles and applications\n• Key concept 3: Practical implications and examples\n• Key concept 4: Related theories and connections\n• Key concept 5: Future developments and research`
        break
      case "paragraph":
        summaryContent = `This content discusses ${inputText.substring(0, 30)}... The main themes include fundamental principles, practical applications, and theoretical frameworks. Key insights reveal important connections between concepts and their real-world implications. The material covers essential knowledge areas that form the foundation for advanced understanding.`
        break
      case "detailed":
        summaryContent = `Comprehensive Analysis:\n\nMain Topic: ${inputText.substring(0, 40)}...\n\nKey Points:\n1. Fundamental concepts and definitions\n2. Core principles and mechanisms\n3. Practical applications and examples\n4. Theoretical implications\n\nConclusion:\nThis material provides essential knowledge for understanding the subject matter and its broader applications in the field.`
        break
    }

    const newSummary: Summary = {
      id: Date.now().toString(),
      title: `Summary ${recentSummaries.length + 1}`,
      originalLength: wordCount,
      summaryLength: summaryContent.split(" ").length,
      language,
      type: summaryType,
      content: summaryContent,
      timestamp: new Date(),
    }

    setCurrentSummary(newSummary)
    setRecentSummaries([newSummary, ...recentSummaries])
    setIsGenerating(false)
    setProgress(0)
  }

  const copySummary = () => {
    if (currentSummary) {
      navigator.clipboard.writeText(currentSummary.content)
    }
  }

  const downloadSummary = () => {
    if (currentSummary) {
      const blob = new Blob([currentSummary.content], { type: "text/plain" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `${currentSummary.title}.txt`
      a.click()
      URL.revokeObjectURL(url)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground font-[family-name:var(--font-work-sans)]">AI Summarizer</h2>
          <p className="text-muted-foreground font-[family-name:var(--font-open-sans)]">
            Transform lengthy content into concise, multilingual summaries
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="gap-1">
            <Languages className="w-3 h-3" />
            Multilingual Support
          </Badge>
          <Badge variant="outline" className="gap-1">
            <Sparkles className="w-3 h-3" />
            AI Powered
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Section */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-[family-name:var(--font-work-sans)]">
                <FileText className="w-5 h-5 text-primary" />
                Input Content
              </CardTitle>
              <CardDescription className="font-[family-name:var(--font-open-sans)]">
                Paste your text, notes, or upload a document to summarize
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Tabs defaultValue="text" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="text" className="font-[family-name:var(--font-open-sans)]">
                    Text Input
                  </TabsTrigger>
                  <TabsTrigger value="upload" className="font-[family-name:var(--font-open-sans)]">
                    Upload File
                  </TabsTrigger>
                </TabsList>
                <TabsContent value="text" className="space-y-4">
                  <Textarea
                    placeholder="Paste your content here... (minimum 100 words for best results)"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    className="min-h-[300px] font-[family-name:var(--font-open-sans)]"
                  />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>{inputText.split(" ").filter((word) => word.length > 0).length} words</span>
                    <span>{inputText.length} characters</span>
                  </div>
                </TabsContent>
                <TabsContent value="upload" className="space-y-4">
                  <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
                    <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground mb-2 font-[family-name:var(--font-open-sans)]">
                      Drag and drop your file here, or click to browse
                    </p>
                    <p className="text-sm text-muted-foreground font-[family-name:var(--font-open-sans)]">
                      Supports PDF, DOCX, TXT files (max 10MB)
                    </p>
                    <Button variant="outline" className="mt-4 font-[family-name:var(--font-open-sans)] bg-transparent">
                      Choose File
                    </Button>
                  </div>
                </TabsContent>
              </Tabs>

              {/* Summary Options */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium font-[family-name:var(--font-open-sans)]">Summary Type</label>
                  <Select value={summaryType} onValueChange={(value: any) => setSummaryType(value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="bullet">Bullet Points</SelectItem>
                      <SelectItem value="paragraph">Paragraph</SelectItem>
                      <SelectItem value="detailed">Detailed Analysis</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium font-[family-name:var(--font-open-sans)]">Language</label>
                  <Select value={language} onValueChange={setLanguage}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {languages.map((lang) => (
                        <SelectItem key={lang.value} value={lang.value}>
                          {lang.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button
                onClick={generateSummary}
                disabled={!inputText.trim() || isGenerating}
                className="w-full gap-2 font-[family-name:var(--font-open-sans)]"
                size="lg"
              >
                {isGenerating ? (
                  <>
                    <Zap className="w-4 h-4 animate-pulse" />
                    Generating Summary...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate AI Summary
                  </>
                )}
              </Button>

              {isGenerating && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-[family-name:var(--font-open-sans)]">Processing content...</span>
                    <span className="font-[family-name:var(--font-open-sans)]">{progress}%</span>
                  </div>
                  <Progress value={progress} className="h-2" />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Generated Summary */}
          {currentSummary && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2 font-[family-name:var(--font-work-sans)]">
                    <CheckCircle className="w-5 h-5 text-primary" />
                    Generated Summary
                  </CardTitle>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={copySummary}
                      className="gap-1 font-[family-name:var(--font-open-sans)] bg-transparent"
                    >
                      <Copy className="w-4 h-4" />
                      Copy
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={downloadSummary}
                      className="gap-1 font-[family-name:var(--font-open-sans)] bg-transparent"
                    >
                      <Download className="w-4 h-4" />
                      Download
                    </Button>
                  </div>
                </div>
                <CardDescription className="font-[family-name:var(--font-open-sans)]">
                  Reduced from {currentSummary.originalLength} to {currentSummary.summaryLength} words (
                  {Math.round((1 - currentSummary.summaryLength / currentSummary.originalLength) * 100)}% reduction)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-muted/50 rounded-lg p-4 border">
                  <pre className="whitespace-pre-wrap text-sm font-[family-name:var(--font-open-sans)] leading-relaxed">
                    {currentSummary.content}
                  </pre>
                </div>
                <div className="flex items-center gap-4 mt-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {currentSummary.timestamp.toLocaleTimeString()}
                  </div>
                  <div className="flex items-center gap-1">
                    <Target className="w-4 h-4" />
                    {currentSummary.type} format
                  </div>
                  <div className="flex items-center gap-1">
                    <Languages className="w-4 h-4" />
                    {languages.find((l) => l.value === currentSummary.language)?.label}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="font-[family-name:var(--font-work-sans)]">Summary Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-[family-name:var(--font-open-sans)]">Total Summaries</span>
                <span className="font-semibold">{recentSummaries.length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-[family-name:var(--font-open-sans)]">Words Processed</span>
                <span className="font-semibold">
                  {recentSummaries.reduce((acc, s) => acc + s.originalLength, 0).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-[family-name:var(--font-open-sans)]">Time Saved</span>
                <span className="font-semibold">~2.5 hours</span>
              </div>
            </CardContent>
          </Card>

          {/* Recent Summaries */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-[family-name:var(--font-work-sans)]">
                <BookOpen className="w-5 h-5 text-primary" />
                Recent Summaries
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {recentSummaries.slice(0, 5).map((summary) => (
                <div
                  key={summary.id}
                  className="p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors cursor-pointer"
                  onClick={() => setCurrentSummary(summary)}
                >
                  <h4 className="font-semibold text-sm text-foreground font-[family-name:var(--font-work-sans)]">
                    {summary.title}
                  </h4>
                  <p className="text-xs text-muted-foreground mt-1 font-[family-name:var(--font-open-sans)]">
                    {summary.originalLength} → {summary.summaryLength} words
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="outline" className="text-xs">
                      {summary.type}
                    </Badge>
                    <span className="text-xs text-muted-foreground">{summary.timestamp.toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Tips */}
          <Card>
            <CardHeader>
              <CardTitle className="font-[family-name:var(--font-work-sans)]">Pro Tips</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-3 bg-primary/10 rounded-lg border border-primary/20">
                <p className="text-sm font-[family-name:var(--font-open-sans)]">
                  <strong>Best Results:</strong> Use content with at least 200 words for more accurate summaries.
                </p>
              </div>
              <div className="p-3 bg-secondary/10 rounded-lg border border-secondary/20">
                <p className="text-sm font-[family-name:var(--font-open-sans)]">
                  <strong>Multilingual:</strong> Switch languages to get summaries in your preferred language.
                </p>
              </div>
              <div className="p-3 bg-accent/10 rounded-lg border border-accent/20">
                <p className="text-sm font-[family-name:var(--font-open-sans)]">
                  <strong>Study Tip:</strong> Use bullet points for quick review, detailed for comprehensive
                  understanding.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
