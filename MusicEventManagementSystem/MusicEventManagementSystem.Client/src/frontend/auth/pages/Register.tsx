import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../../shared/services/apiService';
import type { RegisterDto } from '../../shared/services/apiService';
import { UserPlus, Mail, Lock, User, Building, Music, Sparkles, CheckCircle } from 'lucide-react';

const Register = () => {
  const [formData, setFormData] = useState<RegisterDto>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    department: 4,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [passwordStrength, setPasswordStrength] = useState(0);
  const navigate = useNavigate();

  // The app is a marketing tool now, so everyone joins the marketing team
  const departments = [
    { value: 4, label: 'Marketing', color: 'purple', gradient: 'from-purple-400 to-violet-500' },
  ];

  const getDepartmentData = (dept: number) => {
    return departments.find(d => d.value === dept) || departments[0];
  };

  const currentDept = getDepartmentData(formData.department);

  // Password strength calculation
  useEffect(() => {
    const password = formData.password;
    let strength = 0;
    
    if (password.length >= 6) strength += 25;
    if (password.length >= 10) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/[0-9]/.test(password)) strength += 25;
    
    setPasswordStrength(strength);
  }, [formData.password]);

  const getPasswordStrengthColor = () => {
    if (passwordStrength < 25) return 'red';
    if (passwordStrength < 50) return 'orange';
    if (passwordStrength < 75) return 'yellow';
    return 'green';
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: name === 'department' ? parseInt(value) : value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters.');
      setLoading(false);
      return;
    }

    try {
      const response = await authAPI.register(formData);
      
      if (response.success) {
        navigate('/login', { 
          state: { message: 'Account created successfully! Please sign in.' }
        });
      } else {
        setError(response.message || 'Registration failed.');
      }
    } catch (err: any) {
      if (err.response?.status === 409) {
        setError('Email already exists.');
      } else {
        setError(err.response?.data?.message || 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Dynamic background based on selected department */}
      <div className={`absolute inset-0 bg-gradient-to-br from-${currentDept.color}-900/20 via-neutral-950 to-${currentDept.color}-950/10 transition-all duration-700`}></div>
      
      {/* Animated particles */}
      <div className="absolute inset-0">
        {[...Array(15)].map((_, i) => (
          <div
            key={i}
            className={`absolute w-1 h-1 bg-${currentDept.color}-400/20 rounded-full animate-pulse`}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 2}s`,
            }}
          ></div>
        ))}
      </div>
      
      <div className="bg-neutral-900/90 backdrop-blur-md border border-neutral-800/50 rounded-3xl p-8 w-full max-w-md shadow-2xl relative z-10 transform transition-all duration-300 hover:scale-[1.01]">
        {/* Header with dynamic department info */}
        <div className="text-center mb-4">
          <div className="flex justify-center mb-4">
            <div className={`p-4 rounded-2xl bg-gradient-to-br ${currentDept.gradient} shadow-lg relative transition-all duration-700`}>
              <div className="relative">
                <Music className="w-8 h-8 text-white" />
                <Sparkles className="absolute -bottom-1 -left-1 w-4 h-4 text-white animate-pulse" />
              </div>
            </div>
          </div>
          
          <div className="text-3xl font-black text-white mb-2 tracking-tight">
            Join <span className={`text-${currentDept.color}-400 transition-colors duration-700`}>MEMS</span>!
          </div>
          
          <div className={`w-60 h-1 bg-gradient-to-r ${currentDept.gradient} rounded-full mx-auto mb-3 transition-all duration-700`}></div>
          
          <p className="text-neutral-400 text-sm">
            Create your account for{' '}
            <span className={`text-${currentDept.color}-400 font-medium transition-colors duration-700`}>
              {currentDept.label}
            </span>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="relative group">
              <User className={`absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-300 w-4 h-4 group-focus-within:text-${currentDept.color}-600`} />
              <input
                type="text"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
                required
                className={`w-full pl-10 pr-3 py-3 bg-neutral-800/80 border border-neutral-700 rounded-xl text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-${currentDept.color}-400 focus:border-transparent transition-all duration-300 text-sm focus:bg-neutral-800`}
                placeholder="First name"
              />
            </div>
            <div className="relative group">
              <User className={`absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-100 w-4 h-4`} />
              <input
                type="text"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
                required
                className={`w-full pl-10 pr-3 py-3 bg-neutral-800/80 border border-neutral-700 rounded-xl text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-${currentDept.color}-400 focus:border-transparent transition-all duration-300 text-sm focus:bg-neutral-800`}
                placeholder="Last name"
              />
            </div>
          </div>

          <div className="relative group">
            <Mail className={`absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-100 w-4 h-4`} />
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className={`w-full pl-10 pr-3 py-3 bg-neutral-800/80 border border-neutral-700 rounded-xl text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-${currentDept.color}-400 focus:border-transparent transition-all duration-300 text-sm focus:bg-neutral-800`}
              placeholder="Email address"
            />
          </div>

          <div className="relative group">
            <Building className={`absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-100 w-4 h-4`} />
            <select
              name="department"
              value={formData.department}
              onChange={handleChange}
              required
              className={`w-full pl-10 pr-3 py-3 bg-neutral-800/80 border border-neutral-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-${currentDept.color}-400 focus:border-transparent transition-all duration-300 text-sm appearance-none cursor-pointer focus:bg-neutral-800`}
            >
              {departments.map((dept) => (
                <option key={dept.value} value={dept.value} className="bg-neutral-800">
                  {dept.label}
                </option>
              ))}
            </select>
          </div>

          <div className="relative group">
            <Lock className={`absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-100 w-4 h-4`} />
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              className={`w-full pl-10 pr-3 py-3 bg-neutral-800/80 border border-neutral-700 rounded-xl text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-${currentDept.color}-400 focus:border-transparent transition-all duration-300 text-sm focus:bg-neutral-800`}
              placeholder="Password (6+ characters)"
            />
            {formData.password && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                <div className={`w-2 h-2 rounded-full bg-${getPasswordStrengthColor()}-400`}></div>
              </div>
            )}
          </div>

          <div className="relative group">
            <Lock className={`absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-100 w-4 h-4`} />
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              className={`w-full pl-10 pr-3 py-3 bg-neutral-800/80 border border-neutral-700 rounded-xl text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-${currentDept.color}-400 focus:border-transparent transition-all duration-300 text-sm focus:bg-neutral-800`}
              placeholder="Confirm password"
            />
            {formData.confirmPassword && formData.password === formData.confirmPassword && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                <CheckCircle className="w-4 h-4 text-green-400" />
              </div>
            )}
          </div>

          {error && (
            <div className="text-red-400 text-sm text-center bg-red-950/50 backdrop-blur-sm border border-red-900/50 py-2 px-3 rounded-xl animate-shake">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || passwordStrength < 25}
            className={`w-full bg-gradient-to-r ${currentDept.gradient} hover:shadow-lg hover:shadow-${currentDept.color}-500/25 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 mt-6 transform hover:scale-[1.02] active:scale-[0.98]`}
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
            ) : (
              <>
                <UserPlus size={18} />
                Create Account
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-neutral-500 text-sm">
            Already have an account?{' '}
            <Link 
              to="/login" 
              className={`text-${currentDept.color}-400 hover:text-${currentDept.color}-300 font-medium transition-all duration-300 hover:underline`}
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>

      <style>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }
        .animate-shake {
          animation: shake 0.5s ease-in-out;
        }
      `}</style>
    </div>
  );
};

export default Register;