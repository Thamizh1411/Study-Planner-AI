import React, { useEffect, useState } from 'react';
import { usePlannerStore } from '../store/plannerStore';
import { 
  Flame, 
  BookOpen, 
  GraduationCap, 
  AlertCircle,
  Calendar,
  Plus,
  Trash2,
  Sparkles,
  Brain,
  CheckCircle,
  Play
} from 'lucide-react';

export default function Dashboard() {
  const { 
    user,
    exam,
    completion_rate,
    active_streak,
    average_quiz_score,
    weak_topics,
    today_plan,
    analysis,
    motivation,
    fetchDashboard,
    createExam,
    deleteExam,
    generateAIPlan,
    logStudyHours,
    loading 
  } = usePlannerStore();

  const [showExamModal, setShowExamModal] = useState(false);
  
  // Create Exam Form state
  const [examName, setExamName] = useState('');
  const [examDate, setExamDate] = useState('');
  const examPriority = 'medium';
  const examDifficulty = 'medium';
  
  // Custom subject list builder
  const [subjects, setSubjects] = useState([{ name: '', difficulty: 'medium' }]);
  const [topics, setTopics] = useState([{ title: '', subject_name: '', status: 'pending', confidence: 'medium' }]);

  // Study Logging state
  const [logHrs, setLogHrs] = useState('');

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleAddSubject = () => {
    setSubjects([...subjects, { name: '', difficulty: 'medium' }]);
  };

  const handleAddTopic = () => {
    setTopics([...topics, { title: '', subject_name: '', status: 'pending', confidence: 'medium' }]);
  };

  const handleCreateExamSubmit = async (e) => {
    e.preventDefault();
    if (!examName || !examDate || subjects.some(s => !s.name) || topics.some(t => !t.title || !t.subject_name)) {
      alert('Please fill out all fields including all subject names and topic titles.');
      return;
    }

    const success = await createExam({
      name: examName,
      exam_date: examDate,
      priority: examPriority,
      difficulty: examDifficulty,
      subjects: subjects,
      topics: topics
    });

    if (success) {
      setShowExamModal(false);
      // Reset form
      setExamName('');
      setExamDate('');
      setSubjects([{ name: '', difficulty: 'medium' }]);
      setTopics([{ title: '', subject_name: '', status: 'pending', confidence: 'medium' }]);
    }
  };

  const handleGeneratePlan = async () => {
    if (!exam) return;
    await generateAIPlan(exam.id);
  };

  const handleLogHoursSubmit = async (e) => {
    e.preventDefault();
    const hoursVal = parseFloat(logHrs);
    if (isNaN(hoursVal) || hoursVal <= 0) {
      alert('Please enter a valid positive number of hours.');
      return;
    }
    const success = await logStudyHours(hoursVal);
    if (success) {
      setLogHrs('');
      alert('Study hours logged successfully!');
    }
  };

  const handleDelExam = async () => {
    if (window.confirm('Are you sure you want to delete this exam and reset your planner?')) {
      await deleteExam(exam.id);
    }
  };

  const daysLeft = exam ? Math.ceil((new Date(exam.exam_date) - new Date()) / (1000 * 60 * 60 * 24)) : 0;
  const hasPlanItems = Array.isArray(today_plan)
    ? today_plan.length > 0
    : Boolean(today_plan && Object.keys(today_plan).length > 0);
  const showCompileButton = Boolean(exam) && !hasPlanItems;

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-16">
      {/* Top Header Section */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Study Dashboard</h1>
          <p className="text-dark-300 text-sm mt-1">Hello, {user?.name || 'Scholar'}. Welcome back to your dashboard.</p>
        </div>

        <div className="flex items-center gap-3">
          {showCompileButton && (
            <button
              onClick={handleGeneratePlan}
              disabled={loading}
              className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-blue-400 hover:text-blue-300 transition-all border border-blue-500/20 hover:bg-blue-500/10 px-4 py-2.5 rounded-xl cursor-pointer"
            >
              <Sparkles size={14} /> {loading ? 'Compiling...' : 'Compile Multi-Agent Plan'}
            </button>
          )}

          {exam && (
            <button 
              onClick={handleDelExam}
              className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-red-400 hover:text-red-300 transition-all border border-red-500/20 hover:bg-red-500/10 px-4 py-2.5 rounded-xl cursor-pointer"
            >
              <Trash2 size={14} /> Delete Exam Plan
            </button>
          )}
        </div>
      </div>

      {/* Grid Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Study Streak */}
        <div className="glass-card flex items-center justify-between p-6">
          <div>
            <span className="text-xs text-dark-400 font-semibold uppercase tracking-wider">Active Streak</span>
            <h3 className="text-3xl font-extrabold text-white mt-1.5">{active_streak} Days</h3>
            <p className="text-xs text-dark-300 mt-2">Consistent studies</p>
          </div>
          <div className="p-4 bg-orange-500/10 text-orange-500 rounded-2xl border border-orange-500/20">
            <Flame size={24} className="animate-pulse" />
          </div>
        </div>

        {/* Topic Completion Rate */}
        <div className="glass-card flex items-center justify-between p-6">
          <div>
            <span className="text-xs text-dark-400 font-semibold uppercase tracking-wider">Topic Completion</span>
            <h3 className="text-3xl font-extrabold text-white mt-1.5">{completion_rate}%</h3>
            <p className="text-xs text-dark-300 mt-2">Syllabus progression</p>
          </div>
          <div className="p-4 bg-blue-500/10 text-blue-500 rounded-2xl border border-blue-500/20">
            <BookOpen size={24} />
          </div>
        </div>

        {/* Average Quiz Score */}
        <div className="glass-card flex items-center justify-between p-6">
          <div>
            <span className="text-xs text-dark-400 font-semibold uppercase tracking-wider">Quiz Accuracy</span>
            <h3 className="text-3xl font-extrabold text-white mt-1.5">{average_quiz_score}%</h3>
            <p className="text-xs text-dark-300 mt-2">Performance rating</p>
          </div>
          <div className="p-4 bg-purple-500/10 text-purple-500 rounded-2xl border border-purple-500/20">
            <GraduationCap size={24} />
          </div>
        </div>

        {/* Weak Topics */}
        <div className="glass-card flex items-center justify-between p-6">
          <div>
            <span className="text-xs text-dark-400 font-semibold uppercase tracking-wider">Weak Areas</span>
            <h3 className="text-3xl font-extrabold text-white mt-1.5">{weak_topics.length} Topics</h3>
            <p className="text-xs text-dark-300 mt-2">Need rebalancing review</p>
          </div>
          <div className="p-4 bg-red-500/10 text-red-500 rounded-2xl border border-red-500/20">
            <AlertCircle size={24} />
          </div>
        </div>
      </div>

      {/* Main Content Layout */}
      {!exam ? (
        /* Empty State: Create Exam */
        <div className="glass-card text-center py-16 px-6 max-w-xl mx-auto border border-dark-800">
          <div className="inline-flex p-4 bg-gradient-to-tr from-blue-500 to-indigo-600 rounded-3xl shadow-lg shadow-blue-500/10 text-white mb-6 animate-bounce">
            <Calendar size={32} />
          </div>
          <h2 className="text-2xl font-extrabold text-white mb-2">No Active Exam Plans</h2>
          <p className="text-dark-300 text-sm max-w-sm mx-auto mb-8 leading-relaxed">
            Create your exam schedule, add subjects and syllabus topics, and let the AI agents plan your daily hours.
          </p>
          <button 
            onClick={() => setShowExamModal(true)}
            className="btn-primary mx-auto py-3.5 px-6 font-bold cursor-pointer"
          >
            <Plus size={18} /> Configure Study Plan
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Today's Tasks & Hours Logging */}
          <div className="lg:col-span-2 space-y-8">
            {/* Today's Schedule Card */}
            <div className="glass-card p-6 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-[200px] h-[200px] bg-blue-500/5 blur-[50px] rounded-full pointer-events-none" />
              
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-lg font-bold text-white">Today's Schedule</h3>
                  <span className="text-xs text-dark-400">Study blocks for {new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })}</span>
                </div>
                
                {daysLeft > 0 ? (
                  <span className="text-xs font-semibold text-blue-400 bg-blue-500/10 px-3 py-1.5 rounded-xl border border-blue-500/20 flex items-center gap-1.5">
                    <Calendar size={14} /> {daysLeft} Days to Exam
                  </span>
                ) : (
                  <span className="text-xs font-semibold text-red-400 bg-red-500/10 px-3 py-1.5 rounded-xl border border-red-500/20">
                    Exam Date Reached!
                  </span>
                )}
              </div>

              {/* Verify if schedule has study plans */}
              {!hasPlanItems ? (
                <div className="py-10 text-center">
                  <p className="text-dark-300 text-sm mb-6">Your calendar is clear. Trigger AI planner compilation to build your agent study roadmap.</p>
                  <button 
                    onClick={handleGeneratePlan}
                    disabled={loading}
                    className="btn-primary mx-auto font-bold cursor-pointer"
                  >
                    <Sparkles size={18} /> {loading ? 'Compiling Agents...' : 'Compile Multi-Agent Plan'}
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {today_plan.map((item, idx) => (
                    <div 
                      key={idx} 
                      className={`p-4 rounded-xl border flex items-center justify-between transition-all duration-200 ${
                        item.completed 
                          ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-300' 
                          : 'bg-dark-950/40 border-dark-800 hover:border-dark-700'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${
                          item.type === 'study' 
                            ? 'bg-blue-500/10 text-blue-400' 
                            : 'bg-amber-500/10 text-amber-400'
                        }`}>
                          <Play size={14} className={item.completed ? 'text-emerald-400' : ''} />
                        </div>
                        <div>
                          <h4 className="font-semibold text-sm text-dark-50">{item.topic_title}</h4>
                          <span className="text-xs text-dark-400 block">{item.subject_name} • <span className="capitalize">{item.type.replace('_', ' ')}</span></span>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <span className="text-xs font-semibold bg-dark-900 px-2.5 py-1 rounded-lg border border-dark-800">{item.hours} hrs</span>
                        {item.completed ? (
                          <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded flex items-center gap-1">
                            <CheckCircle size={12} /> Done
                          </span>
                        ) : (
                          <span className="text-xs font-semibold text-dark-400">Pending</span>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  <div className="pt-4 border-t border-dark-850 flex justify-end">
                    <button 
                      onClick={handleGeneratePlan}
                      disabled={loading}
                      className="text-xs text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1.5 cursor-pointer"
                    >
                      <Sparkles size={14} /> Rebalance Plan with AI
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Log Study Hours Card */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-bold text-white mb-2">Track Daily Progress</h3>
              <p className="text-dark-400 text-xs mb-4">Input study time to build consistency streaks and recalculate learning rates.</p>
              
              <form onSubmit={handleCreateExamSubmit} className="flex gap-4 items-center">
                <div className="relative flex-1">
                  <input 
                    type="number" 
                    step="0.5"
                    placeholder="E.g., 2.5 study hours"
                    value={logHrs}
                    onChange={(e) => setLogHrs(e.target.value)}
                    className="w-full glass-input"
                  />
                </div>
                <button 
                  onClick={handleLogHoursSubmit}
                  type="button"
                  className="btn-primary py-3.5 px-6 font-bold cursor-pointer"
                >
                  Log Study Time
                </button>
              </form>
            </div>
          </div>

          {/* Right Column: Motivation & Performance Reports */}
          <div className="space-y-8">
            {/* Daily Motivation from Worker 6 */}
            <div className="glass-card p-6 bg-gradient-to-br from-indigo-500/5 to-purple-500/5 border border-indigo-500/10">
              <div className="flex items-center gap-2 mb-4">
                <Brain className="text-indigo-400 animate-pulse" size={20} />
                <h4 className="font-bold text-sm text-indigo-300 uppercase tracking-wider">AI Motivation Desk</h4>
              </div>
              <p className="text-dark-100 italic text-sm leading-relaxed mb-4">
                "{motivation?.daily_motivation || 'Consistency is the engine of academic success.'}"
              </p>
              
              {motivation?.study_tips && (
                <div className="space-y-2.5">
                  <div className="text-[10px] text-indigo-400 uppercase tracking-widest font-bold">Study Tips</div>
                  {motivation.study_tips.map((tip, idx) => (
                    <div key={idx} className="text-xs text-dark-300 leading-relaxed">• {tip}</div>
                  ))}
                </div>
              )}
            </div>

            {/* Weekly report from Worker 5 */}
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-bold text-sm text-dark-50 uppercase tracking-wider">Performance Analytics</h4>
                {analysis?.productivity_badge && (
                  <span className="text-[10px] font-bold text-amber-300 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
                    {analysis.productivity_badge}
                  </span>
                )}
              </div>
              
              {/* Productive Scores */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-3 bg-dark-950/50 border border-dark-800 rounded-xl">
                  <div className="text-[10px] text-dark-400 uppercase tracking-wider font-semibold">Productivity Score</div>
                  <div className="text-2xl font-black text-blue-400 mt-1">{analysis?.productivity_score || 80}/100</div>
                </div>
                <div className="p-3 bg-dark-950/50 border border-dark-800 rounded-xl">
                  <div className="text-[10px] text-dark-400 uppercase tracking-wider font-semibold">Learning Score</div>
                  <div className="text-2xl font-black text-purple-400 mt-1">{analysis?.learning_score || 70}/100</div>
                </div>
              </div>

              <div className="space-y-4">
                <p className="text-xs text-dark-300 leading-relaxed">
                  {analysis?.weekly_summary || 'Your personalized learning dashboard is processing metrics.'}
                </p>

                {analysis?.suggestions && (
                  <div className="space-y-2">
                    <div className="text-[10px] text-dark-400 uppercase tracking-widest font-bold">Actions Required</div>
                    {analysis.suggestions.map((sug, idx) => (
                      <div key={idx} className="text-xs text-dark-300 leading-relaxed">• {sug}</div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal Configure Study Plan */}
      {showExamModal && (
        <div className="fixed inset-0 bg-dark-950/80 backdrop-blur-sm flex items-center justify-center p-6 z-50 overflow-y-auto">
          <div className="w-full max-w-2xl bg-dark-900 border border-dark-800 rounded-3xl p-8 max-h-[85vh] overflow-y-auto shadow-2xl">
            <h2 className="text-2xl font-black text-white mb-2">Configure Study Plan</h2>
            <p className="text-dark-400 text-xs mb-6">Input exam variables, syllabus subjects, and individual topics to schedule study logs.</p>

            <form onSubmit={handleCreateExamSubmit} className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-dark-300 mb-2">Exam Subject/Title</label>
                  <input 
                    type="text"
                    required
                    placeholder="E.g., final term exams"
                    value={examName}
                    onChange={(e) => setExamName(e.target.value)}
                    className="w-full glass-input"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-dark-300 mb-2">Exam Target Date</label>
                  <input 
                    type="date"
                    required
                    value={examDate}
                    onChange={(e) => setExamDate(e.target.value)}
                    className="w-full glass-input"
                  />
                </div>
              </div>

              {/* Subjects builder */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <h4 className="text-xs font-bold text-dark-300 uppercase tracking-wider">1. Subjects List</h4>
                  <button 
                    type="button" 
                    onClick={handleAddSubject}
                    className="text-xs text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1 cursor-pointer"
                  >
                    + Add Subject
                  </button>
                </div>
                {subjects.map((sub, idx) => (
                  <div key={idx} className="grid grid-cols-3 gap-3">
                    <input 
                      type="text" 
                      placeholder="Subject Name (e.g. Calculus)"
                      value={sub.name}
                      required
                      onChange={(e) => {
                        const newSubs = [...subjects];
                        newSubs[idx].name = e.target.value;
                        setSubjects(newSubs);
                      }}
                      className="col-span-2 glass-input py-2"
                    />
                    <select
                      value={sub.difficulty}
                      onChange={(e) => {
                        const newSubs = [...subjects];
                        newSubs[idx].difficulty = e.target.value;
                        setSubjects(newSubs);
                      }}
                      className="glass-input py-2 bg-dark-950 text-xs"
                    >
                      <option value="easy">Easy</option>
                      <option value="medium">Medium</option>
                      <option value="hard">Hard</option>
                    </select>
                  </div>
                ))}
              </div>

              {/* Topics builder */}
              <div className="space-y-3 pt-3 border-t border-dark-850">
                <div className="flex justify-between items-center">
                  <h4 className="text-xs font-bold text-dark-300 uppercase tracking-wider">2. Topics / Syllabus Chapters</h4>
                  <button 
                    type="button" 
                    onClick={handleAddTopic}
                    className="text-xs text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1 cursor-pointer"
                  >
                    + Add Topic
                  </button>
                </div>
                {topics.map((top, idx) => (
                  <div key={idx} className="grid grid-cols-4 gap-3">
                    <input 
                      type="text" 
                      placeholder="Topic Name (e.g. Limits)"
                      value={top.title}
                      required
                      onChange={(e) => {
                        const newTops = [...topics];
                        newTops[idx].title = e.target.value;
                        setTopics(newTops);
                      }}
                      className="col-span-2 glass-input py-2"
                    />
                    <input 
                      type="text" 
                      placeholder="Subject Name"
                      value={top.subject_name}
                      required
                      onChange={(e) => {
                        const newTops = [...topics];
                        newTops[idx].subject_name = e.target.value;
                        setTopics(newTops);
                      }}
                      className="glass-input py-2"
                    />
                    <select
                      value={top.confidence}
                      onChange={(e) => {
                        const newTops = [...topics];
                        newTops[idx].confidence = e.target.value;
                        setTopics(newTops);
                      }}
                      className="glass-input py-2 bg-dark-950 text-xs"
                    >
                      <option value="low">Low Confidence</option>
                      <option value="medium">Medium</option>
                      <option value="high">High Confidence</option>
                    </select>
                  </div>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 pt-6 justify-end border-t border-dark-850">
                <button 
                  type="button" 
                  onClick={() => setShowExamModal(false)}
                  className="btn-secondary py-3 text-xs"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn-primary py-3 text-xs font-bold"
                >
                  Save and Initialize Plan
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
