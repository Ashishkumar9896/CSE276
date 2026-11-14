// src/components/ChatWidget.tsx
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { chatApi, feedbackApi } from '../services/api';
import type { ChatMessage, SuggestedAction, ChatResponse } from '../types';

interface ChatWidgetProps {
  onOpenEnquiry?: () => void;
  onOpenDemo?: () => void;
  onOpenComplaint?: () => void;
}

const WELCOME_MESSAGE: ChatMessage = {
  id: 'welcome',
  sender: 'bot',
  body: "Hello and welcome to Future Vision Classes! 🎓\n\nI am your 24/7 AI academic advisor. I can assist you with course curriculums (IIT-JEE, NEET, Foundation), batch timings, fee structures, demo class bookings, and support.\n\nHow can I help you today?",
  created_at: new Date().toISOString(),
  suggestedActions: [
    { label: '📚 Courses', message: 'What courses do you offer?' },
    { label: '💰 Fee Structure', message: 'What are the fees?' },
    { label: '🎯 Book Demo', message: 'I want to book a demo class' },
    { label: '⏰ Batch Timings', message: 'What are the class timings?' },
  ],
};

const renderFormattedText = (text: string) => {
  // Parse **bold** markdown tags cleanly
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
};

export const ChatWidget: React.FC<ChatWidgetProps> = ({ onOpenEnquiry, onOpenDemo, onOpenComplaint }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [feedbackGiven, setFeedbackGiven] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      inputRef.current?.focus();
    }
  }, [isOpen, messages, scrollToBottom]);

  const resetChat = () => {
    setMessages([WELCOME_MESSAGE]);
    setSessionToken(null);
    setFeedbackGiven(new Set());
    setError(null);
  };

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;
    setError(null);

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'customer',
      body: text.trim(),
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: text.trim(),
        session_token: sessionToken || undefined,
      }) as ChatResponse;

      if (!sessionToken && response.session_token) {
        setSessionToken(response.session_token);
      }

      const botMessage: ChatMessage = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        body: response.reply,
        intent: response.intent,
        created_at: new Date().toISOString(),
        suggestedActions: response.suggested_actions,
      };

      setMessages(prev => [...prev, botMessage]);

      // Automatically trigger corresponding modals on action intents
      if (response.intent === 'enquiry') {
        setTimeout(() => onOpenEnquiry?.(), 1400);
      } else if (response.intent === 'demo_request') {
        setTimeout(() => onOpenDemo?.(), 1400);
      } else if (response.intent === 'complaint') {
        setTimeout(() => onOpenComplaint?.(), 1400);
      }
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Unable to connect to support. Please verify backend is running.';
      setError(errorMsg);
      setMessages(prev => [...prev, {
        id: `error-${Date.now()}`,
        sender: 'bot',
        body: `⚠️ ${errorMsg}`,
        created_at: new Date().toISOString(),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const handleSuggestedAction = (action: SuggestedAction) => {
    sendMessage(action.message);
  };

  const giveFeedback = async (messageId: string, rating: 'helpful' | 'not_helpful') => {
    if (feedbackGiven.has(messageId)) return;
    try {
      await feedbackApi.submit({
        session_token: sessionToken || undefined,
        rating,
      });
      setFeedbackGiven(prev => new Set([...prev, messageId]));
    } catch {
      // Silent failure for feedback
    }
  };

  const formatTime = (isoString: string) => {
    return new Date(isoString).toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="chat-widget" role="complementary" aria-label="Customer support chat">
      {/* Toggle button */}
      <button
        className="chat-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-label="Open Future Vision Classes support chat"
      >
        <span className="chat-toggle__icon" aria-hidden="true">
          {isOpen ? '✕' : '💬'}
        </span>
        {!isOpen && <span className="chat-toggle__badge">AI</span>}
      </button>

      {/* Chat window */}
      {isOpen && (
        <div
          className="chat-window"
          role="dialog"
          aria-modal="true"
          aria-label="Future Vision Classes Support Chat"
        >
          {/* Header */}
          <div className="chat-header">
            <div className="chat-header__avatar" aria-hidden="true">🎓</div>
            <div className="chat-header__info">
              <div className="chat-header__name">Future Vision Classes</div>
              <div className="chat-header__status">AI Academic Advisor • Online</div>
            </div>
            <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
              <button
                className="chat-header__close"
                onClick={resetChat}
                title="Reset conversation"
                style={{ fontSize: '0.85rem' }}
              >
                🔄
              </button>
              <button
                className="chat-header__close"
                onClick={() => setIsOpen(false)}
                aria-label="Close chat"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Messages */}
          <div
            className="chat-messages"
            role="log"
            aria-live="polite"
            aria-relevant="additions"
          >
            {messages.map((msg) => (
              <div key={msg.id}>
                <div className={`message message--${msg.sender}`}>
                  {msg.sender === 'bot' && (
                    <div className="message__avatar" aria-hidden="true">🤖</div>
                  )}
                  <div>
                    <div className="message__bubble">{renderFormattedText(msg.body)}</div>
                    <div className="message__time">{formatTime(msg.created_at)}</div>
                  </div>
                </div>

                {/* Suggested actions under bot messages */}
                {msg.sender === 'bot' && msg.suggestedActions && msg.suggestedActions.length > 0 && (
                  <div className="suggested-actions" role="group" aria-label="Quick replies">
                    {msg.suggestedActions.map((action) => (
                      <button
                        key={action.label}
                        className="suggested-action"
                        onClick={() => handleSuggestedAction(action)}
                        disabled={isLoading}
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                )}

                {/* Feedback buttons for bot messages */}
                {msg.sender === 'bot' && msg.id !== 'welcome' && !msg.id.startsWith('error') && (
                  <div className="feedback-row">
                    <span className="feedback-label">Helpful?</span>
                    <button
                      className={`feedback-btn ${feedbackGiven.has(msg.id) ? 'active-helpful' : ''}`}
                      onClick={() => giveFeedback(msg.id, 'helpful')}
                      aria-label="Mark as helpful"
                      disabled={feedbackGiven.has(msg.id)}
                    >
                      👍
                    </button>
                    <button
                      className={`feedback-btn ${feedbackGiven.has(msg.id) ? 'active-unhelpful' : ''}`}
                      onClick={() => giveFeedback(msg.id, 'not_helpful')}
                      aria-label="Mark as not helpful"
                      disabled={feedbackGiven.has(msg.id)}
                    >
                      👎
                    </button>
                  </div>
                )}
              </div>
            ))}

            {/* Typing indicator */}
            {isLoading && (
              <div className="message message--bot">
                <div className="message__avatar" aria-hidden="true">🤖</div>
                <div className="typing-indicator" aria-label="Bot is typing">
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div className="chat-input-area">
            <div className="chat-input-row">
              <textarea
                ref={inputRef}
                id="chat-input"
                className="chat-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about courses, fees, demo classes, batch timings…"
                aria-label="Chat message input"
                maxLength={2000}
                rows={1}
                disabled={isLoading}
              />
              <button
                className="chat-send-btn"
                onClick={() => sendMessage(input)}
                disabled={isLoading || !input.trim()}
                aria-label="Send message"
              >
                ➤
              </button>
            </div>
            <p className="chat-disclaimer">
              ⚡ Instant AI assistance • Verified coaching information
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
