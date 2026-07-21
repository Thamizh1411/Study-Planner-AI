import React, { useState } from 'react';
import { Bot, Send, Sparkles, User } from 'lucide-react';
import { api } from '../store/plannerStore';

const INITIAL_MESSAGE = {
  role: 'assistant',
  content: 'Hello! Tell me the topic and ask any study question. I can explain concepts, formulas, and mistakes step by step.',
};

export default function Tutor() {
  const [topicTitle, setTopicTitle] = useState('');
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const trimmedQuestion = question.trim();
    const trimmedTopic = topicTitle.trim();

    if (!trimmedTopic || !trimmedQuestion || isLoading) {
      return;
    }

    const conversation = [...messages, { role: 'user', content: trimmedQuestion }];
    setMessages(conversation);
    setQuestion('');
    setIsLoading(true);

    try {
      const response = await api.post('/ai/chat-tutor', {
        topic_title: trimmedTopic,
        question: trimmedQuestion,
        chat_history: conversation.slice(-5),
      });
      setMessages((currentMessages) => [
        ...currentMessages,
        { role: 'assistant', content: response.data.answer },
      ]);
    } catch (error) {
      const detail = error.response?.data?.detail || 'The tutor could not respond. Please try again.';
      setMessages((currentMessages) => [
        ...currentMessages,
        { role: 'assistant', content: detail },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-10">
      <header>
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <Sparkles size={24} />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-white">AI Study Tutor</h1>
            <p className="text-sm text-dark-300 mt-1">Ask for a clear explanation, worked example, or revision help.</p>
          </div>
        </div>
      </header>

      <section className="glass-card p-5">
        <label htmlFor="tutor-topic" className="text-xs font-bold uppercase tracking-wider text-dark-300">
          Current topic
        </label>
        <input
          id="tutor-topic"
          value={topicTitle}
          onChange={(event) => setTopicTitle(event.target.value)}
          placeholder="For example: Limits and Continuity"
          className="glass-input mt-2 w-full"
        />
      </section>

      <section className="glass-card overflow-hidden">
        <div className="min-h-[360px] max-h-[55vh] overflow-y-auto p-5 space-y-4">
          {messages.map((message, index) => {
            const isStudent = message.role === 'user';
            return (
              <div key={`${message.role}-${index}`} className={`flex gap-3 ${isStudent ? 'justify-end' : ''}`}>
                {!isStudent && <Bot size={20} className="mt-1 text-blue-400 shrink-0" />}
                <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                  isStudent
                    ? 'bg-blue-600 text-white'
                    : 'bg-dark-900 border border-dark-800 text-dark-100'
                }`}>
                  {message.content}
                </div>
                {isStudent && <User size={20} className="mt-1 text-dark-300 shrink-0" />}
              </div>
            );
          })}
          {isLoading && <p className="text-sm text-blue-300 animate-pulse">Tutor is thinking...</p>}
        </div>

        <form onSubmit={handleSubmit} className="border-t border-dark-800 p-4 flex gap-3">
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask a question about the selected topic..."
            className="glass-input flex-1"
          />
          <button type="submit" disabled={isLoading} className="btn-primary px-4 disabled:opacity-50">
            <Send size={18} />
          </button>
        </form>
      </section>
    </div>
  );
}
