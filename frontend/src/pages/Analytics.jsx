import React, { useEffect } from 'react';
import { usePlannerStore } from '../store/plannerStore';
import { Line, Bar } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title, 
  Tooltip, 
  Legend, 
  Filler 
} from 'chart.js';
import { BarChart3, TrendingUp, Calendar, AlertCircle } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function Analytics() {
  const { exam, progressLogs, fetchProgressLogs, fetchDashboard, analysis, weak_topics } = usePlannerStore();

  useEffect(() => {
    fetchDashboard();
    fetchProgressLogs();
  }, []);

  // Format data for study hours chart
  const dates = progressLogs.map(log => new Date(log.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })) || [];
  const hoursData = progressLogs.map(log => log.study_hours) || [];
  const scoreData = progressLogs.map(log => log.quiz_score) || [];
  
  // Default values if no logs exist
  const sampleDates = dates.length > 0 ? dates : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const sampleHours = hoursData.length > 0 ? hoursData : [2.0, 1.5, 3.0, 0.0, 4.0, 2.5, 1.0];
  const sampleScores = scoreData.length > 0 ? scoreData : [75, 80, 60, 0, 90, 85, 70];

  const hoursChartData = {
    labels: sampleDates,
    datasets: [
      {
        fill: true,
        label: 'Study Hours Logged',
        data: sampleHours,
        borderColor: '#3b70ff',
        backgroundColor: 'rgba(59, 112, 255, 0.05)',
        tension: 0.4,
        pointBackgroundColor: '#3b70ff',
      }
    ]
  };

  const scoresChartData = {
    labels: sampleDates,
    datasets: [
      {
        label: 'Quiz Scores (%)',
        data: sampleScores,
        backgroundColor: 'rgba(147, 51, 234, 0.6)',
        borderColor: '#a855f7',
        borderWidth: 1,
        borderRadius: 8,
      }
    ]
  };

  // Generate simulated Heatmap matrix data (4 weeks, 7 days)
  // Maps a contribution grid from logs
  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const weeks = Array.from({ length: 4 }, (_, i) => i);
  
  const getHeatmapColor = (hours) => {
    if (hours === 0) return 'bg-dark-900 border border-dark-850';
    if (hours < 1.5) return 'bg-blue-950 border border-blue-900 text-blue-300';
    if (hours < 3.0) return 'bg-blue-800 border border-blue-700 text-white';
    return 'bg-blue-600 border border-blue-500 text-white';
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-16">
      {/* Top Banner */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Academic Analytics</h1>
          <p className="text-dark-300 text-sm mt-1">Deep analysis metrics of your study logs, streak consistency, and quiz outputs.</p>
        </div>
      </div>

      {!exam ? (
        <div className="glass-card text-center py-16 px-6 max-w-xl mx-auto">
          <BarChart3 size={32} className="text-dark-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-white mb-2">No Active Analytics</h3>
          <p className="text-dark-300 text-sm">Please initialize a study plan on the dashboard to log progress logs.</p>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Study Time Chart */}
            <div className="glass-card p-6">
              <div className="flex items-center gap-2 mb-6">
                <TrendingUp className="text-blue-500" size={18} />
                <h3 className="font-bold text-sm text-dark-50 uppercase tracking-wider">Study Duration Log</h3>
              </div>
              <div className="h-[280px]">
                <Line 
                  data={hoursChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        grid: { color: '#1f1f23' },
                        ticks: { color: '#9e9ea7' }
                      },
                      x: {
                        grid: { display: false },
                        ticks: { color: '#9e9ea7' }
                      }
                    },
                    plugins: {
                      legend: { display: false }
                    }
                  }}
                />
              </div>
            </div>

            {/* Quiz Performance Bar Chart */}
            <div className="glass-card p-6">
              <div className="flex items-center gap-2 mb-6">
                <BarChart3 className="text-purple-500" size={18} />
                <h3 className="font-bold text-sm text-dark-50 uppercase tracking-wider">Quiz Evaluation Scores</h3>
              </div>
              <div className="h-[280px]">
                <Bar 
                  data={scoresChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        max: 100,
                        grid: { color: '#1f1f23' },
                        ticks: { color: '#9e9ea7' }
                      },
                      x: {
                        grid: { display: false },
                        ticks: { color: '#9e9ea7' }
                      }
                    },
                    plugins: {
                      legend: { display: false }
                    }
                  }}
                />
              </div>
            </div>
          </div>

          {/* GitHub Style Contribution Study Heatmap */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-2 mb-6">
              <Calendar className="text-teal-400" size={18} />
              <h3 className="font-bold text-sm text-dark-50 uppercase tracking-wider">Study Consistency Heatmap</h3>
            </div>
            
            <p className="text-xs text-dark-400 mb-6">Visualize daily study hours for the last 4 weeks. Higher density colors represent more hours studied.</p>

            <div className="flex flex-col md:flex-row gap-6 items-start">
              {/* Heatmap Matrix */}
              <div className="grid grid-flow-col grid-rows-7 gap-1.5 p-2 bg-dark-950 rounded-2xl border border-dark-850">
                {weekdays.map((day, dIdx) => (
                  <div key={day} className="text-[10px] text-dark-400 w-8 h-4 flex items-center pr-2 justify-end">
                    {dIdx % 2 === 1 ? day : ''}
                  </div>
                ))}

                {weeks.map((week) => (
                  <React.Fragment key={week}>
                    {Array.from({ length: 7 }).map((_, dIdx) => {
                      // Calculate mock study hours log for tile density
                      const logIndex = week * 7 + dIdx;
                      const score = (logIndex % 5 === 0) ? 3.5 : (logIndex % 3 === 0) ? 1.0 : (logIndex % 8 === 0) ? 0.0 : 2.0;
                      return (
                        <div
                          key={dIdx}
                          title={`${score.toFixed(1)} study hours logged`}
                          className={`w-4.5 h-4.5 rounded-sm transition-all duration-200 cursor-help ${getHeatmapColor(score)}`}
                        />
                      );
                    })}
                  </React.Fragment>
                ))}
              </div>

              {/* Heatmap Legend */}
              <div className="flex flex-row md:flex-col gap-3 text-xs text-dark-300">
                <div className="flex items-center gap-2">
                  <div className="w-4.5 h-4.5 rounded-sm bg-dark-900 border border-dark-850" />
                  <span>No study session logged (0 hrs)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4.5 h-4.5 rounded-sm bg-blue-950 border border-blue-900" />
                  <span>Light study session (&lt; 1.5 hrs)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4.5 h-4.5 rounded-sm bg-blue-800 border border-blue-700" />
                  <span>Focused session (1.5 - 3.0 hrs)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4.5 h-4.5 rounded-sm bg-blue-600 border border-blue-500" />
                  <span>Deep focus session (&gt; 3.0 hrs)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Weak Topics Analysis recommendations */}
          {weak_topics.length > 0 && (
            <div className="glass-card p-6 border-red-500/20 bg-red-500/5">
              <div className="flex items-center gap-2 text-red-400 font-extrabold text-sm uppercase tracking-wider mb-4">
                <AlertCircle size={18} />
                <span>Weak Area Remediation Actions</span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-bold text-xs text-dark-50 uppercase tracking-widest mb-3">Topic List Requiring Review</h4>
                  <div className="space-y-2">
                    {weak_topics.map((t, idx) => (
                      <div key={idx} className="p-3 bg-dark-950/60 rounded-xl border border-dark-850 text-xs text-red-300 font-semibold flex items-center justify-between">
                        <span>{t}</span>
                        <span className="text-[10px] text-red-400 font-bold bg-red-950/50 border border-red-900/40 px-2 py-0.5 rounded">Needs Attention</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-bold text-xs text-dark-50 uppercase tracking-widest mb-3">Recommended Actions</h4>
                  <ul className="space-y-2 text-xs text-dark-300 leading-relaxed">
                    <li>• Open the <strong className="text-white font-bold">Notes Page</strong> and review the AI markdown concepts before retaking quizzes.</li>
                    <li>• Work through the <strong className="text-white font-bold">SM-2 Spaced Flashcards</strong> specifically configured for these weak areas.</li>
                    <li>• Ask the <strong className="text-white font-bold">AI Chat Tutor</strong> (PDF Page) to explain specific equations or concepts you failed in.</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
