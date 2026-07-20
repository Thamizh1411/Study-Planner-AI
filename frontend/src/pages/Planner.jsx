import React, { useEffect, useState } from 'react';
import { usePlannerStore } from '../store/plannerStore';
import { Calendar, Sparkles, Check, Play, AlertTriangle } from 'lucide-react';

export default function Planner() {
  const { exam, schedule, weak_topics, fetchDashboard, generateAIPlan, loading } = usePlannerStore();
  const [selectedDay, setSelectedDay] = useState('');

  useEffect(() => {
    fetchDashboard();
  }, []);

  useEffect(() => {
    const dates = Object.keys(schedule);
    if (dates.length > 0 && !selectedDay) {
      setSelectedDay(dates[0]);
    }
  }, [schedule]);

  const handleRebalance = async () => {
    if (!exam) return;
    await generateAIPlan(exam.id);
  };

  const dates = Object.keys(schedule).sort();

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-16">
      {/* Top title bar */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Study Timetable</h1>
          <p className="text-dark-300 text-sm mt-1">AI Optimized calendar and spacing revision plan.</p>
        </div>

        {exam && (
          <button
            onClick={handleRebalance}
            disabled={loading}
            className="btn-primary py-3 text-xs font-bold shadow-md cursor-pointer"
          >
            <Sparkles size={16} /> {loading ? 'Rebalancing...' : 'Trigger AI Rebalance'}
          </button>
        )}
      </div>

      {!exam ? (
        <div className="glass-card text-center py-16 px-6 max-w-xl mx-auto">
          <Calendar size={32} className="text-dark-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-white mb-2">No Active Study Timetable</h3>
          <p className="text-dark-300 text-sm">Please create an exam plan on the dashboard first to view schedules.</p>
        </div>
      ) : Object.keys(schedule).length === 0 ? (
        <div className="glass-card text-center py-16 px-6 max-w-xl mx-auto">
          <Sparkles size={32} className="text-blue-400 mx-auto mb-4 animate-pulse" />
          <h3 className="text-lg font-bold text-white mb-2">Plan Pending AI Generation</h3>
          <p className="text-dark-300 text-sm mb-6">Let the multi-agent system evaluate your subjects and build the calendar.</p>
          <button 
            onClick={handleRebalance}
            disabled={loading}
            className="btn-primary mx-auto font-bold cursor-pointer"
          >
            <Sparkles size={18} /> {loading ? 'Compiling Agents...' : 'Compile Multi-Agent Plan'}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Dates List */}
          <div className="lg:col-span-1 space-y-4">
            <div className="glass-card p-4">
              <h3 className="font-bold text-xs text-dark-300 uppercase tracking-widest mb-4">Timetable Calendar</h3>
              <div className="flex flex-col gap-2 max-h-[50vh] overflow-y-auto pr-1">
                {dates.map((dateStr) => {
                  const items = schedule[dateStr] || [];
                  const studyHours = items.reduce((acc, curr) => acc + curr.hours, 0);
                  const isSelected = selectedDay === dateStr;
                  
                  return (
                    <button
                      key={dateStr}
                      onClick={() => setSelectedDay(dateStr)}
                      className={`w-full text-left p-3.5 rounded-xl border transition-all duration-150 cursor-pointer ${
                        isSelected 
                          ? 'bg-blue-600/10 border-blue-500 text-blue-300 shadow-md' 
                          : 'bg-dark-950/40 border-dark-800/80 hover:bg-dark-900/60 hover:border-dark-700 text-dark-200'
                      }`}
                    >
                      <div className="text-xs font-bold">
                        {new Date(dateStr).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}
                      </div>
                      <div className="text-[10px] text-dark-400 mt-1 flex justify-between">
                        <span>{items.length} sessions</span>
                        <span className="font-bold text-dark-300">{studyHours.toFixed(1)} hrs</span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Weak Areas Side Alert */}
            {weak_topics.length > 0 && (
              <div className="glass-card p-4 border-red-500/20 bg-red-500/5">
                <div className="flex items-center gap-2 text-red-400 font-bold text-xs uppercase tracking-wider mb-2">
                  <AlertTriangle size={16} />
                  <span>Weak Areas Alert</span>
                </div>
                <p className="text-[11px] text-red-300/80 leading-relaxed mb-3">
                  Quizzes show low score trends in the following topics. AI has allocated extra review blocks to them.
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {weak_topics.map((t, idx) => (
                    <span key={idx} className="text-[10px] font-semibold text-red-200 bg-red-950/50 border border-red-800/40 px-2 py-0.5 rounded">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Day Schedule Detail Display */}
          <div className="lg:col-span-3 space-y-6">
            <div className="glass-card p-6 relative">
              <div className="absolute top-0 right-0 w-[150px] h-[150px] bg-indigo-500/5 blur-[50px] pointer-events-none rounded-full" />
              
              <div className="flex justify-between items-center mb-6 pb-4 border-b border-dark-800">
                <div>
                  <h2 className="text-xl font-extrabold text-white">
                    {selectedDay ? new Date(selectedDay).toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }) : 'Select a date'}
                  </h2>
                  <p className="text-dark-400 text-xs mt-1">Study blocks allocated for spacing and retention</p>
                </div>
                
                <span className="text-xs font-semibold text-dark-300 bg-dark-950 border border-dark-800 px-3 py-1.5 rounded-xl">
                  Total Planned: {((schedule[selectedDay] || []).reduce((acc, c) => acc + c.hours, 0)).toFixed(1)} Hours
                </span>
              </div>

              {/* Study blocks */}
              <div className="space-y-4">
                {(schedule[selectedDay] || []).length === 0 ? (
                  <p className="text-center py-10 text-dark-400 text-sm">No study sessions allocated for this date.</p>
                ) : (
                  (schedule[selectedDay] || []).map((item, idx) => (
                    <div 
                      key={idx}
                      className={`p-5 rounded-2xl border flex items-center justify-between transition-all duration-200 ${
                        item.completed 
                          ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-300'
                          : 'bg-dark-950/20 border-dark-800/80 hover:border-dark-750 hover:bg-dark-950/40'
                      }`}
                    >
                      <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-xl border ${
                          item.type === 'study'
                            ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                            : item.type === 'final_revision'
                            ? 'bg-purple-500/10 text-purple-400 border-purple-500/20'
                            : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                        }`}>
                          {item.type === 'study' ? (
                            <Play size={16} />
                          ) : (
                            <Sparkles size={16} />
                          )}
                        </div>
                        <div>
                          <h4 className="font-bold text-sm text-dark-50">{item.topic_title}</h4>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-dark-400 font-semibold">{item.subject_name}</span>
                            <span className="text-dark-500 text-[10px]">•</span>
                            <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded ${
                              item.type === 'study'
                                ? 'text-blue-400 bg-blue-500/10 border border-blue-500/15'
                                : item.type === 'final_revision'
                                ? 'text-purple-400 bg-purple-500/10 border border-purple-500/15'
                                : 'text-amber-400 bg-amber-500/10 border border-amber-500/15'
                            }`}>
                              {item.type.replace('_', ' ')}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        <span className="font-extrabold text-sm text-dark-100 bg-dark-950 px-3 py-1.5 rounded-xl border border-dark-850">{item.hours} hours</span>
                        {item.completed ? (
                          <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-full border border-emerald-500/30">
                            <Check size={14} />
                          </div>
                        ) : (
                          <span className="text-xs text-dark-400 font-medium">Scheduled</span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
