import React, { useEffect, useState } from 'react';
import { usePlannerStore } from '../store/plannerStore';
import { api } from '../store/plannerStore';
import { GraduationCap, Timer, Award, CheckCircle2, AlertCircle, RefreshCw, ChevronRight } from 'lucide-react';

export default function Quiz() {
  const { exam } = usePlannerStore();
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  
  // Quiz states
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [quizDifficulty, setQuizDifficulty] = useState('medium');
  const [quizLoading, setQuizLoading] = useState(false);
  const [answers, setAnswers] = useState({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [quizResult, setQuizResult] = useState(null);
  const [rebalancedPlan, setRebalancedPlan] = useState(null);
  
  // Countdown Timer
  const [timeLeft, setTimeLeft] = useState(300); // 5 minutes
  const [timerActive, setTimerActive] = useState(false);

  useEffect(() => {
    if (exam) {
      axiosLoadTopics();
    }
  }, [exam]);

  const axiosLoadTopics = async () => {
    try {
      const res = await api.get(`/exams/${exam.id}/details`);
      setTopics(res.data.topics || []);
      if (res.data.topics?.length > 0 && !selectedTopic) {
        setSelectedTopic(res.data.topics[0]);
      }
    } catch (err) {
      console.error('Failed to load topics', err);
    }
  };

  // Load quiz on topic selection
  useEffect(() => {
    if (selectedTopic) {
      loadTopicQuiz();
    }
  }, [selectedTopic]);

  const loadTopicQuiz = async () => {
    setQuizLoading(true);
    setQuizQuestions([]);
    setIsSubmitted(false);
    setQuizResult(null);
    setRebalancedPlan(null);
    setAnswers({});
    setTimeLeft(300);
    setTimerActive(false);
    
    try {
      const res = await api.get(`/progress/topics/${selectedTopic.id}/quiz`);
      setQuizQuestions(res.data.questions || []);
      setQuizDifficulty(res.data.difficulty || 'medium');
      setTimerActive(true);
    } catch {
      setQuizQuestions([]);
    } finally {
      setQuizLoading(false);
    }
  };

  // Countdown timer effect
  useEffect(() => {
    if (!timerActive || timeLeft <= 0) return;
    const interval = setInterval(() => {
      setTimeLeft(prev => prev - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [timerActive, timeLeft]);

  // Submit trigger
  const handleQuizSubmit = async () => {
    setTimerActive(false);
    
    // Evaluate answers
    let correctCount = 0;
    const totalQuestions = quizQuestions.length;
    
    const evaluation = quizQuestions.map((q) => {
      const studentAns = (answers[q.id] || '').trim().toLowerCase();
      const correctAns = (q.correct_answer || '').trim().toLowerCase();
      
      let isCorrect = false;
      if (q.type === 'mcq' || q.type === 'true_false') {
        isCorrect = studentAns === correctAns;
      } else {
        // Keyword overlap for fill blanks / short answers / coding
        isCorrect = correctAns.split(' ').some(word => studentAns.includes(word)) || studentAns === correctAns;
      }
      
      if (isCorrect) correctCount++;
      return {
        question_id: q.id,
        is_correct: isCorrect,
        correct_answer: q.correct_answer,
        student_answer: answers[q.id] || '(No response)'
      };
    });
    
    const scorePct = (correctCount / totalQuestions) * 100.0;
    
    try {
      const response = await api.post('/progress/quiz/submit', {
        topic_id: selectedTopic.id,
        score: scorePct
      });
      
      setQuizResult({
        score: scorePct,
        correct: correctCount,
        total: totalQuestions,
        evaluation: evaluation,
        analysis: response.data.analysis
      });
      
      if (response.data.rebalanced_schedule) {
        setRebalancedPlan(response.data.rebalanced_schedule);
      }
      
      setIsSubmitted(true);
      alert(`Quiz evaluated: ${scorePct.toFixed(1)}%. Timetable rebalanced by AI scheduler.`);
    } catch (err) {
      alert('Failed to submit quiz score: ' + (err.response?.data?.detail || err.message));
    }
  };

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-16">
      {/* Top Banner */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Practice Arena</h1>
          <p className="text-dark-300 text-sm mt-1">Interactive adaptive testing. Scheduler rebalances schedule after every attempt.</p>
        </div>
      </div>

      {!exam ? (
        <div className="glass-card text-center py-16 px-6 max-w-xl mx-auto">
          <GraduationCap size={32} className="text-dark-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-white mb-2">No Active Tests</h3>
          <p className="text-dark-300 text-sm">Create an exam schedule on the dashboard to trigger questions.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar topics navigation */}
          <div className="lg:col-span-1 glass-card p-4">
            <h3 className="font-bold text-xs text-dark-300 uppercase tracking-widest mb-4">Select Syllabus topic</h3>
            <div className="flex flex-col gap-2 max-h-[60vh] overflow-y-auto pr-1">
              {topics.map((t) => {
                const isSelected = selectedTopic?.id === t.id;
                return (
                  <button
                    key={t.id}
                    onClick={() => setSelectedTopic(t)}
                    className={`w-full text-left p-3 rounded-xl border transition-all duration-150 flex items-center justify-between cursor-pointer ${
                      isSelected 
                        ? 'bg-blue-600/10 border-blue-500 text-blue-300' 
                        : 'bg-dark-950/40 border-dark-800/80 hover:bg-dark-900/60 hover:border-dark-700 text-dark-200'
                    }`}
                  >
                    <div className="truncate pr-2">
                      <div className="text-xs font-semibold truncate">{t.title}</div>
                      <span className="text-[10px] text-dark-400 font-medium block truncate">{t.subject_name}</span>
                    </div>
                    <ChevronRight size={14} className={isSelected ? 'text-blue-400' : 'text-dark-500'} />
                  </button>
                );
              })}
            </div>
          </div>

          {/* Central Quiz Workspace */}
          <div className="lg:col-span-3 space-y-6">
            <div className="glass-card p-6 min-h-[50vh] relative overflow-hidden">
              <div className="absolute top-0 right-0 w-[150px] h-[150px] bg-purple-500/5 blur-[50px] pointer-events-none rounded-full" />
              
              {selectedTopic && (
                <div className="mb-6 flex justify-between items-center pb-4 border-b border-dark-800">
                  <div>
                    <h2 className="text-xl font-extrabold text-white">{selectedTopic.title}</h2>
                    <span className="text-xs text-dark-400 capitalize">Adaptive Level: {quizDifficulty}</span>
                  </div>

                  {timerActive && (
                    <span className="text-xs font-bold bg-dark-950 border border-dark-800 px-3.5 py-1.5 rounded-xl flex items-center gap-2 text-dark-200">
                      <Timer size={14} className="text-purple-400 animate-spin" /> {minutes}:{seconds < 10 ? '0' : ''}{seconds} Left
                    </span>
                  )}
                </div>
              )}

              {quizLoading ? (
                <div className="py-20 text-center text-dark-300 text-sm flex justify-center items-center gap-2">
                  <RefreshCw className="animate-spin text-purple-500" size={18} /> Loading test questions...
                </div>
              ) : quizQuestions.length === 0 ? (
                <div className="py-16 text-center text-dark-400 text-sm">
                  Please generate your AI Study Plan on the dashboard to populate quizzes for this topic.
                </div>
              ) : (
                <div className="space-y-8">
                  {quizQuestions.map((q, qIdx) => {
                    const evalInfo = quizResult?.evaluation.find(e => e.question_id === q.id);
                    return (
                      <div key={q.id} className="space-y-4">
                        <div className="flex gap-3">
                          <span className="h-6 w-6 rounded-lg bg-dark-950 border border-dark-850 flex items-center justify-center text-xs font-bold text-dark-300">{qIdx+1}</span>
                          <h4 className="font-bold text-sm text-dark-50">{q.question_text}</h4>
                        </div>

                        {/* MCQ Rendering */}
                        {q.type === 'mcq' && (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pl-9">
                            {q.options.map((opt, optIdx) => {
                              const isChecked = answers[q.id] === opt;
                              return (
                                <button
                                  key={optIdx}
                                  disabled={isSubmitted}
                                  onClick={() => setAnswers({ ...answers, [q.id]: opt })}
                                  className={`w-full text-left p-3.5 rounded-xl border text-xs transition-all cursor-pointer ${
                                    isChecked 
                                      ? 'bg-purple-600/10 border-purple-500 text-purple-300 font-semibold' 
                                      : 'bg-dark-950/20 border-dark-800 hover:bg-dark-950/40 text-dark-200'
                                  }`}
                                >
                                  {opt}
                                </button>
                              );
                            })}
                          </div>
                        )}

                        {/* True / False Rendering */}
                        {q.type === 'true_false' && (
                          <div className="flex gap-4 pl-9">
                            {['True', 'False'].map((val) => {
                              const isChecked = answers[q.id] === val;
                              return (
                                <button
                                  key={val}
                                  disabled={isSubmitted}
                                  onClick={() => setAnswers({ ...answers, [q.id]: val })}
                                  className={`px-6 py-2.5 rounded-xl border text-xs transition-all cursor-pointer ${
                                    isChecked 
                                      ? 'bg-purple-600/10 border-purple-500 text-purple-300 font-semibold' 
                                      : 'bg-dark-950/20 border-dark-800 hover:bg-dark-950/40 text-dark-200'
                                  }`}
                                >
                                  {val}
                                </button>
                              );
                            })}
                          </div>
                        )}

                        {/* Fill In Blank Rendering */}
                        {q.type === 'fill_blank' && (
                          <div className="pl-9 max-w-md">
                            <input
                              type="text"
                              disabled={isSubmitted}
                              placeholder="Type correct keyword..."
                              value={answers[q.id] || ''}
                              onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                              className="w-full glass-input"
                            />
                          </div>
                        )}

                        {/* Short Answer Rendering */}
                        {q.type === 'short_answer' && (
                          <div className="pl-9">
                            <textarea
                              disabled={isSubmitted}
                              placeholder="Write a concise concept description..."
                              rows="3"
                              value={answers[q.id] || ''}
                              onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                              className="w-full glass-input"
                            />
                          </div>
                        )}

                        {/* Coding Question Rendering */}
                        {q.type === 'coding' && (
                          <div className="pl-9 space-y-3">
                            <textarea
                              disabled={isSubmitted}
                              placeholder="// Write your code or solution expressions..."
                              rows="4"
                              value={answers[q.id] || ''}
                              onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                              className="w-full glass-input font-mono text-xs"
                            />
                          </div>
                        )}

                        {/* Submit Evaluation Results Details */}
                        {isSubmitted && evalInfo && (
                          <div className="pl-9">
                            {evalInfo.is_correct ? (
                              <div className="p-3.5 bg-emerald-500/5 border border-emerald-500/20 text-emerald-300 text-xs rounded-xl flex items-center gap-2">
                                <CheckCircle2 size={16} /> Question Correct!
                              </div>
                            ) : (
                              <div className="p-3.5 bg-red-500/5 border border-red-500/20 text-red-400 text-xs rounded-xl space-y-1">
                                <div className="flex items-center gap-2">
                                  <AlertCircle size={16} /> Incorrect Response.
                                </div>
                                <div className="text-[11px] text-red-300">
                                  Expected keyword/solutions: <strong className="font-bold underline">{evalInfo.correct_answer}</strong>
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}

                  {!isSubmitted ? (
                    <div className="pt-6 border-t border-dark-800 flex justify-end">
                      <button 
                        onClick={handleQuizSubmit}
                        className="btn-primary py-3.5 px-8 font-extrabold cursor-pointer"
                      >
                        Submit Answers
                      </button>
                    </div>
                  ) : (
                    /* Final Grading Summary Card */
                    <div className="p-6 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 rounded-3xl space-y-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-indigo-500/20 rounded-xl text-indigo-300">
                          <Award size={20} />
                        </div>
                        <div>
                          <h3 className="font-extrabold text-white text-base">Quiz Score: {quizResult.score.toFixed(1)}%</h3>
                          <span className="text-xs text-dark-300">Graded {quizResult.correct} out of {quizResult.total} questions correct</span>
                        </div>
                      </div>

                      {rebalancedPlan && (
                        <div className="p-4 bg-emerald-500/5 border border-emerald-500/25 rounded-2xl">
                          <p className="text-xs text-emerald-300 leading-relaxed font-semibold">
                            🔄 AI Scheduler Rebalance: Study calendar updated dynamically! Topics with low confidence have been assigned extra hour weights.
                          </p>
                        </div>
                      )}
                      
                      <button 
                        onClick={loadTopicQuiz}
                        className="btn-secondary text-xs font-bold cursor-pointer"
                      >
                        Retake Test
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
