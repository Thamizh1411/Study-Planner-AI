import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { usePlannerStore } from '../store/plannerStore';
import { Sparkles, Mail, Lock, LogIn, Chrome } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, loginGoogleMock, loading, error, setError } = usePlannerStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    const success = await login(email, password);
    if (success) {
      navigate('/dashboard');
    }
  };

  const handleMockGoogleLogin = async () => {
    // Easily logs in with simulated credentials
    const success = await loginGoogleMock('Test Scholar', 'scholar@demo.com');
    if (success) {
      navigate('/dashboard');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative p-6">
      {/* Background radial gradients */}
      <div className="absolute top-1/2 left-1/2 translate-x-[-50%] translate-y-[-50%] w-[500px] h-[500px] bg-blue-500/5 blur-[120px] rounded-full pointer-events-none" />

      <div className="w-full max-w-md glass-panel rounded-3xl p-8 shadow-2xl relative border border-dark-800">
        {/* Header Title */}
        <div className="text-center mb-8">
          <div className="inline-flex p-3 bg-gradient-to-tr from-blue-500 to-indigo-600 rounded-2xl shadow-lg shadow-blue-500/10 text-white mb-4">
            <Sparkles size={24} />
          </div>
          <h2 className="text-3xl font-extrabold text-white">Welcome Back</h2>
          <p className="text-dark-400 text-sm mt-2">Sign in to sync your multi-agent study schedule</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-xl font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-widest text-dark-300 mb-2">Email Address</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 translate-y-[-50%] text-dark-400">
                <Mail size={18} />
              </span>
              <input 
                type="email"
                placeholder="your.email@edu.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full glass-input pl-12"
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-xs font-semibold uppercase tracking-widest text-dark-300">Password</label>
              <a href="#" className="text-xs text-blue-400 hover:text-blue-300 transition-colors">Forgot Password?</a>
            </div>
            <div className="relative">
              <span className="absolute left-4 top-1/2 translate-y-[-50%] text-dark-400">
                <Lock size={18} />
              </span>
              <input 
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full glass-input pl-12"
              />
            </div>
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="w-full btn-primary py-3.5 mt-2 font-bold"
          >
            {loading ? 'Signing in...' : 'Sign In'} <LogIn size={18} />
          </button>
        </form>

        {/* Divider */}
        <div className="relative flex py-5 items-center">
          <div className="flex-grow border-t border-dark-800"></div>
          <span className="flex-shrink mx-4 text-dark-400 text-xs uppercase tracking-widest">Or</span>
          <div className="flex-grow border-t border-dark-800"></div>
        </div>

        {/* One Click Mock Google Login for Evaluators */}
        <button 
          onClick={handleMockGoogleLogin}
          className="w-full btn-secondary py-3.5 flex items-center justify-center gap-3 font-semibold mb-6 border border-dark-850 hover:bg-dark-800"
        >
          <Chrome size={18} className="text-blue-400" />
          <span>One-Click Developer Sign In</span>
        </button>

        {/* Footer links */}
        <p className="text-center text-dark-300 text-sm">
          Don't have an account?{' '}
          <Link to="/signup" className="text-blue-400 hover:text-blue-300 font-semibold underline decoration-wavy decoration-blue-500/30">
            Sign up now
          </Link>
        </p>
      </div>
    </div>
  );
}
