'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Loader2, Bot, User, Wrench, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { chatApi, ChatMessage, ToolCallInfo } from '@/lib/api-client';
import { useSession } from '@/lib/auth';

function ToolCallBadge({ toolCall }: { toolCall: ToolCallInfo }) {
  const [expanded, setExpanded] = useState(false);

  const friendlyNames: Record<string, string> = {
    add_task: 'Added task',
    list_tasks: 'Listed tasks',
    complete_task: 'Completed task',
    delete_task: 'Deleted task',
    update_task: 'Updated task',
  };

  const label = friendlyNames[toolCall.tool_name] || toolCall.tool_name;

  return (
    <div className="mt-1">
      <button
        onClick={() => setExpanded(!expanded)}
        className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-900/60 transition-colors"
      >
        <Wrench className="h-3 w-3" />
        {label}
        {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
      </button>
      {expanded && (
        <div className="mt-1 p-2 text-xs bg-gray-50 dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
          {Object.keys(toolCall.arguments).length > 0 && (
            <div className="mb-1">
              <span className="font-semibold text-gray-600 dark:text-gray-400">Args: </span>
              <span className="text-gray-700 dark:text-gray-300">
                {JSON.stringify(toolCall.arguments)}
              </span>
            </div>
          )}
          {toolCall.result && (
            <div>
              <span className="font-semibold text-gray-600 dark:text-gray-400">Result: </span>
              <span className="text-gray-700 dark:text-gray-300">{toolCall.result}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}
    >
      <div className={`flex gap-2 max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <div
          className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gradient-to-br from-purple-500 to-blue-500 text-white'
          }`}
        >
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </div>
        <div>
          <div
            className={`px-3 py-2 rounded-2xl text-sm leading-relaxed ${
              isUser
                ? 'bg-blue-600 text-white rounded-br-md'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-bl-md'
            }`}
          >
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>
          {message.tool_calls && message.tool_calls.length > 0 && (
            <div className="mt-1 space-y-1">
              {message.tool_calls.map((tc, i) => (
                <ToolCallBadge key={i} toolCall={tc} />
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

const SUGGESTIONS = [
  'List my tasks',
  'Add a task to buy groceries',
  'What tasks are pending?',
  'Mark task 1 as done',
];

export function ChatPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | undefined>();
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { data: sessionData } = useSession();

  const userId = sessionData?.user?.id;

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load history when panel opens
  useEffect(() => {
    if (isOpen && userId && !historyLoaded) {
      loadHistory();
    }
  }, [isOpen, userId, historyLoaded]);

  // Focus input when panel opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 200);
    }
  }, [isOpen]);

  const loadHistory = async () => {
    if (!userId) return;
    try {
      const data = await chatApi.getHistory(userId);
      if (data.messages && data.messages.length > 0) {
        setMessages(data.messages);
        setConversationId(data.conversation_id);
      }
      setHistoryLoaded(true);
    } catch (error) {
      console.error('Failed to load chat history:', error);
      setHistoryLoaded(true);
    }
  };

  const sendMessage = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText || !userId || loading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: messageText,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatApi.sendMessage(userId, messageText, conversationId);

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        tool_calls: response.tool_calls,
        created_at: response.created_at,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setConversationId(response.conversation_id);

      // Dispatch tasks-updated event if tools were called
      if (response.tool_calls && response.tool_calls.length > 0) {
        window.dispatchEvent(new CustomEvent('tasks-updated'));
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!userId) return null;

  return (
    <>
      {/* Toggle Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 text-white shadow-lg hover:shadow-xl flex items-center justify-center transition-shadow"
          >
            <MessageCircle className="h-6 w-6" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-6 right-6 z-50 w-96 h-[500px] bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-3 flex items-center justify-between flex-shrink-0">
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-white" />
                <h3 className="text-white font-semibold text-sm">AI Todo Assistant</h3>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white/80 hover:text-white transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4">
              {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center px-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/40 dark:to-purple-900/40 flex items-center justify-center mb-3">
                    <Bot className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Hi! I'm your Todo assistant.
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                    I can help you manage tasks through conversation.
                  </p>
                  <div className="space-y-2 w-full">
                    {SUGGESTIONS.map((suggestion) => (
                      <button
                        key={suggestion}
                        onClick={() => sendMessage(suggestion)}
                        className="w-full text-left px-3 py-2 text-xs rounded-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:border-blue-300 dark:hover:border-blue-600 transition-colors"
                      >
                        "{suggestion}"
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((msg, i) => (
                    <MessageBubble key={i} message={msg} />
                  ))}
                  {loading && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex items-center gap-2 text-gray-400 text-sm mb-3"
                    >
                      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                      <div className="flex items-center gap-1 px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-bl-md">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-xs">Thinking...</span>
                      </div>
                    </motion.div>
                  )}
                </>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-3 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
              <div className="flex gap-2">
                <Input
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask me to manage your tasks..."
                  disabled={loading}
                  className="flex-1 text-sm h-9 rounded-xl"
                />
                <Button
                  onClick={() => sendMessage()}
                  disabled={!input.trim() || loading}
                  size="sm"
                  className="h-9 w-9 p-0 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
