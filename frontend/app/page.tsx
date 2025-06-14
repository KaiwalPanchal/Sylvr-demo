"use client";

import type React from "react";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Send, Mic, MicOff } from "lucide-react";

interface Message {
  id: number;
  text: string;
  isUser: boolean;
}

export default function ChatBot() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: "Hello! How can I help you today?", isUser: false },
  ]);
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket("ws://localhost:8000/chat");
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("Connected to WebSocket");
      // Add a system message to show connection status
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          text: "Connected to chat server",
          isUser: false,
        },
      ]);
    };

    ws.onmessage = (event) => {
      console.log("Received message:", event.data); // Debug log
      try {
        const data = JSON.parse(event.data);
        // Handle both response formats
        const responseText =
          data.response || data.summary || JSON.stringify(data);
        const botMessage: Message = {
          id: Date.now(),
          text: responseText,
          isUser: false,
        };
        setMessages((prev) => [...prev, botMessage]);
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          text: "Error connecting to chat server. Please try refreshing the page.",
          isUser: false,
        },
      ]);
    };

    ws.onclose = () => {
      console.log("Disconnected from WebSocket");
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          text: "Disconnected from chat server. Please refresh the page to reconnect.",
          isUser: false,
        },
      ]);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Check for supported MIME types
      const mimeTypes = [
        "audio/webm",
        "audio/webm;codecs=opus",
        "audio/ogg;codecs=opus",
        "audio/mp4",
        "audio/mpeg",
      ];

      let selectedMimeType = "";
      for (const mimeType of mimeTypes) {
        if (MediaRecorder.isTypeSupported(mimeType)) {
          selectedMimeType = mimeType;
          break;
        }
      }

      if (!selectedMimeType) {
        throw new Error("No supported audio MIME types found");
      }

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: selectedMimeType,
        audioBitsPerSecond: 128000,
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: selectedMimeType,
        });

        const formData = new FormData();
        formData.append(
          "file",
          audioBlob,
          "recording." + selectedMimeType.split("/")[1].split(";")[0]
        );
        formData.append("originalFormat", selectedMimeType);

        try {
          const response = await fetch("http://localhost:8000/transcribe", {
            method: "POST",
            body: formData,
          });

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const data = await response.json();
          if (data.transcribed_text) {
            setInput(data.transcribed_text);
            // Optionally show a success message
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now(),
                text: "Audio transcribed successfully!",
                isUser: false,
              },
            ]);
          }
        } catch (error) {
          console.error("Error transcribing audio:", error);
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now(),
              text: "Error transcribing audio. Please try again.",
              isUser: false,
            },
          ]);
        }

        // Clean up the media stream
        stream.getTracks().forEach((track) => track.stop());
      };

      // Start recording with a 1-second timeslice to get more frequent data
      mediaRecorder.start(1000);
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          text: "Error accessing microphone. Please check your permissions.",
          isUser: false,
        },
      ]);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendMessage = () => {
    if (!input.trim() || !wsRef.current) return;

    const userMessage: Message = {
      id: Date.now(),
      text: input,
      isUser: true,
    };

    setMessages((prev) => [...prev, userMessage]);

    // Ensure WebSocket is connected before sending
    if (wsRef.current.readyState === WebSocket.OPEN) {
      console.log("Sending message:", input); // Debug log
      wsRef.current.send(JSON.stringify({ message: input }));
    } else {
      console.error("WebSocket is not connected");
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          text: "Error: Not connected to chat server. Please refresh the page.",
          isUser: false,
        },
      ]);
    }
    setInput("");
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-4">
      <div className="w-full h-screen flex flex-col">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.isUser ? "justify-end" : "justify-start"
              }`}
            >
              <Card
                className={`max-w-[80%] p-4 ${
                  message.isUser
                    ? "bg-blue-600 text-white"
                    : "bg-gray-800 text-white"
                }`}
              >
                <p>{message.text}</p>
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
            className="flex-1"
          />
          <Button
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onMouseLeave={stopRecording}
            onTouchStart={startRecording}
            onTouchEnd={stopRecording}
            className={`${
              isRecording
                ? "bg-red-500 hover:bg-red-600"
                : "bg-blue-500 hover:bg-blue-600"
            }`}
          >
            {isRecording ? <MicOff /> : <Mic />}
          </Button>
          <Button
            onClick={sendMessage}
            className="bg-blue-500 hover:bg-blue-600"
          >
            <Send />
          </Button>
        </div>
      </div>
    </div>
  );
}
