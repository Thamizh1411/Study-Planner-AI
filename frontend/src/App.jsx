import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import { usePlannerStore } from './store/plannerStore';
import { 
  LayoutDashboard, 
  CalendarDays, 
  BookOpen, 
  GraduationCap, 
  BarChart3, 
  LogOut, 
  Flame,
  Award,
  Sparkles,
  BookMarked
} from 'lucide-react';

import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Planner from './pages/Planner';
import Notes from './pages/Notes';
import Quiz from './pages/Quiz';
import Analytics from './pages/Analytics';

// Navigation Link Component with Active States
function SidebarLink({ to, icon: Icon, children }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <Link
      to={to}
      className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
        isActive 
          ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/20 font-medium' 
          : 'text-dark-300 hover:text-dark-50 hover:bg-dark-800/50'
      }`}
    >
      <Icon size={20} className={isActive ? 'animate-pulse' : ''} />
      <span>{children}</span>
    </Link>
  );
}

// Protected Layout with Premium Glass Sidebar and Animations
function SidebarLayout() {
  const { user, logout, active_streak, analysis } = usePlannerStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="flex min-h-screen bg-dark-950">
      {/* Sidebar Panel */}
      <aside className="w-64 glass-panel border-r border-dark-800/80 p-6 flex flex-col justify-between fixed top-0 bottom-0 left-0 z-20">
        <div>
          {/* Logo Header */}
          <div className="flex items-center gap-3 mb-8 px-2">
            <div className="p-2.5 bg-gradient-to-tr from-blue-500 to-indigo-600 rounded-xl shadow-lg shadow-blue-500/20 text-white">
              <Sparkles size={20} />
            </div>
            <span className="font-extrabold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-dark-50 to-dark-200">
              StudyPlanner <span className="text-blue-400">AI</span>
            </span>
          </div>

          {/* User Status Profile */}
          <div className="mb-6 p-4 rounded-xl bg-dark-950/40 border border-dark-800/60 flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-purple-500 to-indigo-500 flex items-center justify-center text-white font-bold text-lg shadow-md">
              {user?.name ? user.name[0].toUpperCase() : 'U'}
            </div>
            <div className="overflow-hidden">
              <h4 className="font-semibold text-sm text-dark-50 truncate">{user?.name || 'Student'}</h4>
              <span className="text-xs text-dark-400 truncate block">{user?.email || 'email@edu.com'}</span>
            </div>
          </div>

          {/* Gamified Streaks & Badges */}
          <div className="flex items-center justify-between mb-8 p-3.5 bg-gradient-to-br from-orange-500/10 to-amber-500/10 border border-orange-500/20 rounded-xl">
            <div className="flex items-center gap-2">
              <Flame className="text-orange-500 animate-bounce" size={20} />
              <div>
                <div className="text-[10px] text-orange-400 uppercase tracking-widest font-semibold">Streak</div>
                <div className="text-sm font-bold text-orange-200">{active_streak || 0} Days Study</div>
              </div>
            </div>
            {analysis?.productivity_badge && (
              <div className="p-1 bg-amber-500/20 rounded text-amber-300 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 border border-amber-500/30">
                <Award size={10} />
                <span>{analysis.productivity_badge.split(' ')[0]}</span>
              </div>
            )}
          </div>

          {/* Navigation Links */}
          <nav className="flex flex-col gap-1">
            <SidebarLink to="/dashboard" icon={LayoutDashboard}>Dashboard</SidebarLink>
            <SidebarLink to="/planner" icon={CalendarDays}>Study Planner</SidebarLink>
            <SidebarLink to="/notes" icon={BookOpen}>AI Notes & Spaced Cards</SidebarLink>
            <SidebarLink to="/quiz" icon={GraduationCap}>Practice Quizzes</SidebarLink>
            <SidebarLink to="/analytics" icon={BarChart3}>Analytics Report</SidebarLink>
          </nav>
        </div>

        {/* Footer actions */}
        <div>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 text-red-400 hover:text-red-300 rounded-xl hover:bg-red-500/10 transition-all duration-200 font-medium cursor-pointer"
          >
            <LogOut size={20} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Container Area */}
      <main className="flex-1 ml-64 min-h-screen relative p-8">
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/planner" element={<Planner />} />
          <Route path="/notes" element={<Notes />} />
          <Route path="/quiz" element={<Quiz />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </main>
    </div>
  );
}

// Authentication Guard Middleware
function AuthRoute({ children }) {
  const { isAuthenticated } = usePlannerStore();
  return isAuthenticated ? children : <Login />;
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        {/* Protected Dashboard pages layout wrapper */}
        <Route 
          path="/*" 
          element={
            <AuthRoute>
              <SidebarLayout />
            </AuthRoute>
          } 
        />
      </Routes>
    </Router>
  );
}
