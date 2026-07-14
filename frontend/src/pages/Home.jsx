import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Sparkles, 
  BrainCircuit, 
  Search, 
  ListTodo, 
  HelpCircle, 
  LineChart, 
  HeartHandshake, 
  ArrowRight,
  Shield,
  Zap,
  Globe
} from 'lucide-react';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.15 }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: { y: 0, opacity: 1, transition: { type: "spring", stiffness: 100 } }
};

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Dynamic Background Accents */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-500/10 blur-[150px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-purple-500/10 blur-[150px] rounded-full pointer-events-none" />

      {/* Navigation Header */}
      <header className="max-w-7xl mx-auto px-6 py-6 flex justify-between items-center relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-blue-500 to-indigo-600 rounded-xl shadow-lg shadow-blue-500/20 text-white">
            <Sparkles size={20} />
          </div>
          <span className="font-extrabold text-xl tracking-tight text-white">
            StudyPlanner <span className="text-blue-400">AI</span>
          </span>
        </div>
        <div className="flex items-center gap-6">
          <Link to="/login" className="text-dark-300 hover:text-white font-medium transition-colors">
            Log In
          </Link>
          <Link to="/signup" className="bg-white text-dark-950 hover:bg-dark-50 font-bold px-5 py-2.5 rounded-xl shadow-md transition-all duration-150 active:scale-95">
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-6 pt-20 pb-16 text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold tracking-wider uppercase mb-6 shadow-sm shadow-blue-500/5">
            <Zap size={12} className="animate-pulse" /> Multi-Agent AI Study Planner
          </span>
        </motion.div>

        <motion.h1 
          className="text-5xl md:text-7xl font-extrabold text-white leading-tight mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.8 }}
        >
          Ace Your Exams with the Power of <span className="gradient-text">AI Agents</span>
        </motion.h1>

        <motion.p 
          className="text-lg md:text-xl text-dark-300 max-w-2xl mx-auto mb-10 leading-relaxed"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.8 }}
        >
          Transform subjects, topics, and deadlines into a dynamic study calendar. Six specialized AI agents build custom notes, flashcards, and quizzes that rebalance in real-time as you learn.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6, type: "spring", stiffness: 120 }}
          className="flex flex-col sm:flex-row justify-center gap-4 max-w-md mx-auto"
        >
          <Link to="/signup" className="btn-primary py-4 text-base px-8 font-bold">
            Start Planning Free <ArrowRight size={18} />
          </Link>
        </motion.div>
      </section>

      {/* Agent Workflow Display */}
      <section className="max-w-7xl mx-auto px-6 py-20 relative z-10">
        <h2 className="text-3xl md:text-4xl font-extrabold text-center text-white mb-4">
          Meet Your AI Study Team
        </h2>
        <p className="text-dark-400 text-center max-w-lg mx-auto mb-16">
          Six cooperative AI workers collaborate in a LangGraph state machine to compile your personalized learning roadmap.
        </p>

        <motion.div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          {/* Researcher */}
          <motion.div variants={itemVariants} className="glass-card glass-panel-hover flex gap-4">
            <div className="p-3.5 bg-blue-500/10 text-blue-400 rounded-xl h-fit border border-blue-500/20">
              <Search size={22} />
            </div>
            <div>
              <h3 className="font-bold text-lg text-white mb-2">Worker 1: Researcher</h3>
              <p className="text-dark-300 text-sm leading-relaxed">
                Searches concepts, equations, step-by-step examples, and verified web links for every study topic.
              </p>
            </div>
          </motion.div>

          {/* Summarizer */}
          <motion.div variants={itemVariants} className="glass-card glass-panel-hover flex gap-4">
            <div className="p-3.5 bg-indigo-500/10 text-indigo-400 rounded-xl h-fit border border-indigo-500/20">
              <BrainCircuit size={22} />
            </div>
            <div>
              <h3 className="font-bold text-lg text-white mb-2">Worker 2: Summarizer</h3>
              <p className="text-dark-300 text-sm leading-relaxed">
                Transforms heavy content into clear markdown summaries, defining formulas and compiling mnemonic shortcuts.
              </p>
            </div>
          </motion.div>

          {/* Quiz Generator */}
          <motion.div variants={itemVariants} className="glass-card glass-panel-hover flex gap-4">
            <div className="p-3.5 bg-purple-500/10 text-purple-400 rounded-xl h-fit border border-purple-500/20">
              <HelpCircle size={22} />
            </div>
            <div>
              <h3 className="font-bold text-lg text-white mb-2">Worker 3: Quiz Maker</h3>
              <p className="text-dark-300 text-sm leading-relaxed">
                Generates interactive coding prompts, multiple-choice, and short-answer quizzes with adaptive difficulty.
              </p>
            </div>
          </motion.div>

          {/* Scheduler */}
          <motion.div variants={itemVariants} className="glass-card glass-panel-hover flex gap-4">
            <div className="p-3.5 bg-teal-500/10 text-teal-400 rounded-xl h-fit border border-teal-500/20">
              <ListTodo size={22} />
            </div>
            <div>
              <h3 className="font-bold text-lg text-white mb-2">Worker 4: Scheduler</h3>
              <p className="text-dark-300 text-sm leading-relaxed">
                Allocates hours day-by-day. Harder or weaker subjects automatically get priority weight.
              </p>
            </div>
          </motion.div>

          {/* Performance Analyzer */}
          <motion.div variants={itemVariants} className="glass-card glass-panel-hover flex gap-4">
            <div className="p-3.5 bg-rose-500/10 text-rose-400 rounded-xl h-fit border border-rose-500/20">
              <LineChart size={22} />
            </div>
            <div>
              <h3 className="font-bold text-lg text-white mb-2">Worker 5: Stats Analyzer</h3>
              <p className="text-dark-300 text-sm leading-relaxed">
                Aggregates quiz results and consistency metrics to provide granular scores, learning metrics, and reports.
              </p>
            </div>
          </motion.div>

          {/* Motivation Agent */}
          <motion.div variants={itemVariants} className="glass-card glass-panel-hover flex gap-4">
            <div className="p-3.5 bg-amber-500/10 text-amber-400 rounded-xl h-fit border border-amber-500/20">
              <HeartHandshake size={22} />
            </div>
            <div>
              <h3 className="font-bold text-lg text-white mb-2">Worker 6: Motivator</h3>
              <p className="text-dark-300 text-sm leading-relaxed">
                Pushes daily quotes, customized stress relief notes, and suggests break routines based on your workload.
              </p>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* Pricing Cards */}
      <section className="max-w-6xl mx-auto px-6 py-20 relative z-10 border-t border-dark-900">
        <h2 className="text-3xl md:text-4xl font-extrabold text-center text-white mb-4">
          Flexible Pricing For Every Student
        </h2>
        <p className="text-dark-400 text-center max-w-sm mx-auto mb-16">
          Supercharge your study performance. Upgrade anytime. Cancel with a click.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Free plan */}
          <div className="glass-card flex flex-col justify-between p-8">
            <div>
              <span className="text-xs uppercase tracking-widest text-dark-400 font-semibold">Starter</span>
              <h3 className="text-2xl font-bold text-white mt-1 mb-4">Free Plan</h3>
              <div className="text-4xl font-extrabold text-white mb-6">$0<span className="text-sm font-medium text-dark-400">/ forever</span></div>
              <ul className="space-y-3.5 text-dark-300 text-sm mb-8">
                <li className="flex items-center gap-2.5"><Shield size={16} className="text-blue-500" /> Standard AI Study Planner</li>
                <li className="flex items-center gap-2.5"><Shield size={16} className="text-blue-500" /> Basic markdown study notes</li>
                <li className="flex items-center gap-2.5"><Shield size={16} className="text-blue-500" /> Max 2 active subjects</li>
                <li className="flex items-center gap-2.5"><Shield size={16} className="text-blue-500" /> Standard quiz generation</li>
              </ul>
            </div>
            <Link to="/signup" className="btn-secondary w-full py-3.5">
              Sign Up Free
            </Link>
          </div>

          {/* Premium Monthly */}
          <div className="glass-card border-brand-500/40 relative flex flex-col justify-between p-8 bg-gradient-to-b from-dark-900/80 to-dark-950/80 shadow-brand-500/5">
            <div className="absolute top-0 right-6 translate-y-[-50%] bg-gradient-to-r from-blue-500 to-indigo-600 px-3.5 py-1 text-white text-[10px] uppercase font-bold tracking-widest rounded-full shadow-lg border border-blue-400/20">
              Most Popular
            </div>
            <div>
              <span className="text-xs uppercase tracking-widest text-blue-400 font-semibold">Scholar Pro</span>
              <h3 className="text-2xl font-bold text-white mt-1 mb-4">Monthly Premium</h3>
              <div className="text-4xl font-extrabold text-white mb-6">$9.99<span className="text-sm font-medium text-dark-400">/ month</span></div>
              <ul className="space-y-3.5 text-dark-200 text-sm mb-8">
                <li className="flex items-center gap-2.5"><Zap size={16} className="text-blue-400" /> Multi-Agent AI (all 6 workers)</li>
                <li className="flex items-center gap-2.5"><Zap size={16} className="text-blue-400" /> Unlimited Subjects & Topic lists</li>
                <li className="flex items-center gap-2.5"><Zap size={16} className="text-blue-400" /> Spaced repetition cards (SM-2)</li>
                <li className="flex items-center gap-2.5"><Zap size={16} className="text-blue-400" /> PDF Intelligence RAG & OCR Upload</li>
                <li className="flex items-center gap-2.5"><Zap size={16} className="text-blue-400" /> Google Calendar sync simulation</li>
              </ul>
            </div>
            <Link to="/signup" className="btn-primary w-full py-3.5 font-bold">
              Upgrade Now
            </Link>
          </div>

          {/* Premium Yearly */}
          <div className="glass-card flex flex-col justify-between p-8">
            <div>
              <span className="text-xs uppercase tracking-widest text-purple-400 font-semibold">Mastery Pack</span>
              <h3 className="text-2xl font-bold text-white mt-1 mb-4">Yearly Premium</h3>
              <div className="text-4xl font-extrabold text-white mb-6">$79.99<span className="text-sm font-medium text-dark-400">/ year</span></div>
              <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded inline-block mb-6 border border-emerald-500/20">Save 33% compared to monthly</span>
              <ul className="space-y-3.5 text-dark-300 text-sm mb-8">
                <li className="flex items-center gap-2.5"><Globe size={16} className="text-purple-400" /> Everything in Scholar Pro</li>
                <li className="flex items-center gap-2.5"><Globe size={16} className="text-purple-400" /> Dedicated AI voice tutor simulation</li>
                <li className="flex items-center gap-2.5"><Globe size={16} className="text-purple-400" /> Priority processing cached prompts</li>
                <li className="flex items-center gap-2.5"><Globe size={16} className="text-purple-400" /> Export PDF notes & calendars</li>
              </ul>
            </div>
            <Link to="/signup" className="btn-secondary w-full py-3.5">
              Get Yearly Pro
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-dark-900 py-10 text-center relative z-10 text-dark-400 text-sm">
        <p>© {new Date().getFullYear()} Study Planner AI SaaS. Created with LangGraph & React. All rights reserved.</p>
      </footer>
    </div>
  );
}
