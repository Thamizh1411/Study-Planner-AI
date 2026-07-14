import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { usePlannerStore } from '../store/plannerStore';
import { Sparkles, User, Mail, Lock, UserPlus } from 'lucide-react';

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { signup, loading, error, setError } = usePlannerStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    const success = await signup(name, email, password);
    if (success) {
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative p-6">
      {/* Background radial gradient */}
      <div className="absolute top-1/2 left-1/2 translate-x-[-50%] translate-y-[-50%] w-[500px] h-[500px] bg-purple-500/5 blur-[120px] rounded-full pointer-events-none" />

      <div className="w-full max-w-md glass-panel rounded-3xl p-8 shadow-2xl relative border border-dark-800">
        {/* Header Title */}
        <div className="text-center mb-8">
          <div className="inline-flex p-3 bg-gradient-to-tr from-purple-500 to-indigo-600 rounded-2xl shadow-lg shadow-purple-500/10 text-white mb-4">
            <Sparkles size={24} />
          </div>
          <h2 className="text-3xl font-extrabold text-white">Create Account</h2>
          <p className="text-dark-400 text-sm mt-2">Get your custom multi-agent study schedule today</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-xl font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-widest text-dark-300 mb-2">FullName</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 translate-y-[-50%] text-dark-400">
                <User size={18} />
              </span>
              <input 
                type="text"
                placeholder="Alex Mercer"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full glass-input pl-12"
              />
            </div>
          </div>

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
            <label className="block text-xs font-semibold uppercase tracking-widest text-dark-300 mb-2">Password</label>
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
            className="w-full btn-primary py-3.5 mt-2 font-bold bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 shadow-purple-500/10 hover:shadow-purple-500/25"
          >
            {loading ? 'Registering...' : 'Register Account'} <UserPlus size={18} />
          </button>
        </form>

        {/* Footer links */}
        <p className="text-center text-dark-300 text-sm mt-8">
          Already registered?{' '}
          <Link to="/login" className="text-purple-400 hover:text-purple-300 font-semibold underline decoration-wavy decoration-purple-500/30">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
