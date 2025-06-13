"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Send } from "lucide-react"

interface Message {
  id: number
  text: string
  isUser: boolean
}

export default function ChatBot() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: "Hello! How can I help you today?", isUser: false },
  ])
  const [input, setInput] = useState("")

  const sendMessage = () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now(),
      text: input,
      isUser: true,
    }

    const botMessage: Message = {
      id: Date.now() + 1,
      text: "Thanks for your message! This is a minimal chatbot response.",
      isUser: false,
    }

    setMessages((prev) => [...prev, userMessage, botMessage])
    setInput("")
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      sendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-black text-white p-4">
      <div className="w-full h-screen flex flex-col">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}>
              <Card
                className={`max-w-xs p-3 ${
                  message.isUser ? "bg-white text-black" : "bg-gray-800 text-white border-gray-700"
                }`}
              >
                {message.text}
              </Card>
            </div>
          ))}
        </div>

        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 bg-gray-800 border-gray-700 text-white placeholder-gray-400"
          />
          <Button onClick={sendMessage} size="icon" className="bg-white text-black hover:bg-gray-200">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
