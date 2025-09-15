"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { User, Settings, LogOut, Trophy, BookOpen, Clock, Target, ChevronDown } from "lucide-react"

interface UserProfileProps {
  user: {
    id: string
    name: string
    email: string
    avatar: string
    provider: string
  }
  onLogout: () => void
}

export default function UserProfile({ user, onLogout }: UserProfileProps) {
  const [showProfile, setShowProfile] = useState(false)

  const userStats = {
    studyStreak: 12,
    totalHours: 156,
    quizzesCompleted: 24,
    averageScore: 87,
    level: 5,
    xp: 2340,
    nextLevelXp: 3000,
  }

  const achievements = [
    { name: "Study Streak Master", description: "10+ days streak", icon: Target, earned: true },
    { name: "Quiz Champion", description: "20+ quizzes completed", icon: Trophy, earned: true },
    { name: "Night Owl", description: "Study after 10 PM", icon: Clock, earned: false },
    { name: "Early Bird", description: "Study before 7 AM", icon: BookOpen, earned: false },
  ]

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="flex items-center gap-2 h-10 px-3 hover:bg-muted/50">
            <Avatar className="w-8 h-8">
              <AvatarImage src={user.avatar || "/placeholder.svg"} alt={user.name} />
              <AvatarFallback className="bg-primary text-primary-foreground text-sm">
                {user.name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <span className="hidden md:block font-medium text-sm">{user.name.split(" ")[0]}</span>
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel className="font-normal">
            <div className="flex flex-col space-y-1">
              <p className="text-sm font-medium leading-none">{user.name}</p>
              <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => setShowProfile(true)} className="cursor-pointer">
            <User className="mr-2 h-4 w-4" />
            <span>View Profile</span>
          </DropdownMenuItem>
          <DropdownMenuItem className="cursor-pointer">
            <Settings className="mr-2 h-4 w-4" />
            <span>Settings</span>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={onLogout} className="cursor-pointer text-red-600">
            <LogOut className="mr-2 h-4 w-4" />
            <span>Log out</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <Dialog open={showProfile} onOpenChange={setShowProfile}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Profile</DialogTitle>
            <DialogDescription>Your learning progress and achievements</DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            <div className="flex items-center gap-4">
              <Avatar className="w-20 h-20">
                <AvatarImage src={user.avatar || "/placeholder.svg"} alt={user.name} />
                <AvatarFallback className="bg-primary text-primary-foreground text-xl">
                  {user.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <h3 className="text-2xl font-bold">{user.name}</h3>
                <p className="text-muted-foreground">{user.email}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="secondary">Level {userStats.level}</Badge>
                  <Badge variant="outline">
                    {userStats.xp} / {userStats.nextLevelXp} XP
                  </Badge>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Progress to Level {userStats.level + 1}</span>
                <span>{Math.round((userStats.xp / userStats.nextLevelXp) * 100)}%</span>
              </div>
              <Progress value={(userStats.xp / userStats.nextLevelXp) * 100} className="h-2" />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-primary">{userStats.studyStreak}</div>
                  <div className="text-sm text-muted-foreground">Day Streak</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-secondary">{userStats.totalHours}</div>
                  <div className="text-sm text-muted-foreground">Total Hours</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-accent">{userStats.quizzesCompleted}</div>
                  <div className="text-sm text-muted-foreground">Quizzes Done</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-chart-1">{userStats.averageScore}%</div>
                  <div className="text-sm text-muted-foreground">Avg Score</div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Trophy className="w-5 h-5 text-yellow-500" />
                  Achievements
                </CardTitle>
                <CardDescription>Your learning milestones</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {achievements.map((achievement, index) => (
                    <div
                      key={index}
                      className={`flex items-center gap-3 p-3 rounded-lg border ${
                        achievement.earned ? "bg-primary/5 border-primary/20" : "bg-muted/30 border-muted"
                      }`}
                    >
                      <achievement.icon
                        className={`w-8 h-8 ${achievement.earned ? "text-primary" : "text-muted-foreground"}`}
                      />
                      <div className="flex-1">
                        <div
                          className={`font-medium ${achievement.earned ? "text-foreground" : "text-muted-foreground"}`}
                        >
                          {achievement.name}
                        </div>
                        <div className="text-sm text-muted-foreground">{achievement.description}</div>
                      </div>
                      {achievement.earned && (
                        <Badge variant="default" className="bg-primary">
                          Earned
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
