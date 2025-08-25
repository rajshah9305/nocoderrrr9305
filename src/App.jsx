import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import {
  Zap, Code, Folder, BarChart3, Settings, CheckCircle, Loader, 
  Eye, ExternalLink, Edit3, MoreVertical, TrendingUp, TrendingDown,
  Clock, Rocket, Database, Monitor, Server, Palette, Brain, Plus,
  ArrowRight, X, MessageSquare, EyeOff, RefreshCw
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:5000/api';
const socket = io('http://127.0.0.1:5000');

const AIAppBuilder = () => {
  const [activeTab, setActiveTab] = useState('builder');
  const [showSettings, setShowSettings] = useState(false);
  const [isLive, setIsLive] = useState(false);
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [generationStatus, setGenerationStatus] = useState(null);
  const [overallProgress, setOverallProgress] = useState(27);
  const [currentAgent, setCurrentAgent] = useState('Requirements Analyst');
  const [showCodeModal, setShowCodeModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectStatus, setProjectStatus] = useState('draft');
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { 
      id: 1, 
      type: 'ai', 
      content: 'Hi! I can help you build apps, explain features, or suggest improvements. What would you like to create today?',
      timestamp: new Date().toISOString()
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [projectStats, setProjectStats] = useState({
    total_projects: 0,
    deployed: 0,
    building: 0,
    total_views: 0
  });

  // API Functions
  const fetchProjects = async () => {
    try {
      const response = await fetch(`${API_BASE}/projects`);
      const data = await response.json();
      if (data.success) {
        setProjects(data.projects);
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const fetchProjectStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/projects/stats`);
      const data = await response.json();
      if (data.success) {
        setProjectStats(data.stats);
      }
    } catch (error) {
      console.error('Error fetching project stats:', error);
    }
  };

  const createProject = async (projectData) => {
    try {
      const response = await fetch(`${API_BASE}/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(projectData)
      });
      const data = await response.json();
      if (data.success) {
        setCurrentProject(data.project);
        fetchProjects();
        return data.project;
      }
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  const startGeneration = async (projectId, description) => {
    try {
      const response = await fetch(`${API_BASE}/generation/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, description })
      });
      const data = await response.json();
      if (data.success) {
        setGenerationStatus('generating');
      }
    } catch (error) {
      console.error('Error starting generation:', error);
    }
  };

  // WebSocket listeners
  useEffect(() => {
    socket.on('generation_update', (data) => {
      setOverallProgress(data.progress || 0);
      setCurrentAgent(data.current_agent || 'Requirements Analyst');
      setProjectStatus(data.status || 'draft');
    });

    return () => {
      socket.off('generation_update');
    };
  }, []);

  const getAgentStatus = (agentIndex, agentName) => {
    const agentNames = [
      'Requirements Analyst',
      'System Architect', 
      'UI/UX Designer',
      'Frontend Developer',
      'Backend Developer',
      'DevOps Engineer'
    ];
    
    if (projectStatus === 'completed') {
      return { status: 'completed', progress: 100, color: 'green' };
    }
    
    if (projectStatus === 'generating') {
      const currentIndex = agentNames.indexOf(currentAgent);
      if (agentIndex < currentIndex) {
        return { status: 'completed', progress: 100, color: 'green' };
      } else if (agentIndex === currentIndex) {
        return { status: 'active', progress: Math.min(Math.floor((overallProgress * 6) % 100), 100), color: 'blue' };
      }
    }
    
    return { status: 'pending', progress: 0, color: 'gray' };
  };

  // Load data on mount
  useEffect(() => {
    fetchProjects();
    fetchProjectStats();
  }, []);

  const agents = [
    { 
      id: 'analyst', 
      name: 'Requirements Analyst', 
      icon: Brain, 
      description: 'Analyzes requirements and creates technical specifications'
    },
    { 
      id: 'architect', 
      name: 'System Architect', 
      icon: Database, 
      description: 'Designs system architecture and database schemas'
    },
    { 
      id: 'designer', 
      name: 'UI/UX Designer', 
      icon: Palette, 
      description: 'Creates user interface designs and user experience flows'
    },
    { 
      id: 'frontend', 
      name: 'Frontend Developer', 
      icon: Monitor, 
      description: 'Builds React components and user interfaces'
    },
    { 
      id: 'backend', 
      name: 'Backend Developer', 
      icon: Server, 
      description: 'Develops APIs, databases, and server-side logic'
    },
    { 
      id: 'deployer', 
      name: 'DevOps Engineer', 
      icon: Rocket, 
      description: 'Handles deployment, CI/CD, and infrastructure'
    }
  ];

  const openInNewTab = (url) => {
    window.open(url, '_blank');
  };

  const handleNewProject = async () => {
    const projectData = {
      name: "New Project",
      description: "A new AI-generated application",
      framework: "React"
    };
    await createProject(projectData);
  };

  const viewProjectCode = async (project) => {
    try {
      const response = await fetch(`${API_BASE}/projects/${project.id}`);
      const data = await response.json();
      if (data.success) {
        setSelectedProject(data.project);
        setShowCodeModal(true);
      }
    } catch (error) {
      console.error('Error fetching project code:', error);
    }
  };

  const sendChatMessage = () => {
    if (!chatInput.trim()) return;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: chatInput,
      timestamp: new Date().toISOString()
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    
    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        type: 'ai',
        content: getAIResponse(chatInput),
        timestamp: new Date().toISOString()
      };
      setChatMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  const getAIResponse = (message) => {
    const responses = [
      "That's a great idea! I can help you build that. Would you like to start with the requirements analysis?",
      "I understand what you're looking for. Let me suggest some features that would work well for your app.",
      "Based on your description, I recommend using React for the frontend and Node.js for the backend.",
      "That sounds like an interesting project! Have you considered adding user authentication?",
      "I can help you with that. Would you like me to generate a project plan?"
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">AI App Builder Pro</h1>
                <p className="text-xs text-gray-500">Fullstack Development Platform</p>
              </div>
            </div>
            
            <nav className="flex items-center space-x-8">
              {[
                { id: 'builder', label: 'Builder', icon: Code },
                { id: 'projects', label: 'Projects', icon: Folder },
                { id: 'analytics', label: 'Analytics', icon: BarChart3 }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'text-blue-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600">Connected</span>
              </div>
              <button
                onClick={() => setChatOpen(!chatOpen)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <MessageSquare className="w-5 h-5" />
              </button>
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'builder' && (
          <div>
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Building Your App</h1>
              <p className="text-gray-600">Our AI agents are working together to create your application</p>
            </div>

            {/* Overall Progress */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Overall Progress</h3>
                <span className="text-sm text-gray-500">{overallProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-300" style={{ width: `${overallProgress}%` }}></div>
              </div>
            </div>

            {/* Agent Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {agents.map((agent, index) => {
                const agentState = getAgentStatus(index, agent.name);
                return (
                  <div 
                    key={agent.id} 
                    className={`bg-white rounded-xl shadow-sm border p-6 ${
                      agentState.status === 'active' ? 'border-blue-300 ring-2 ring-blue-100' : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-start space-x-4">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                        agentState.color === 'green' ? 'bg-green-100 text-green-600' :
                        agentState.color === 'blue' ? 'bg-blue-100 text-blue-600' :
                        'bg-gray-100 text-gray-400'
                      }`}>
                        {agentState.status === 'active' ? (
                          <Loader className="w-6 h-6 animate-spin" />
                        ) : agentState.status === 'completed' ? (
                          <CheckCircle className="w-6 h-6" />
                        ) : (
                          <agent.icon className="w-6 h-6" />
                        )}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-1">{agent.name}</h3>
                        <p className="text-sm text-gray-600 mb-3">{agent.description}</p>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm text-gray-600">Progress</span>
                          <span className="text-sm font-medium text-gray-900">{agentState.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-300 ${
                              agentState.color === 'green' ? 'bg-green-500' :
                              agentState.color === 'blue' ? 'bg-blue-500' :
                              'bg-gray-300'
                            }`}
                            style={{ width: `${agentState.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Live Preview Section */}
            <div className="mt-8 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Live Preview</h3>
                <div className="flex space-x-2">
                  <button 
                    onClick={() => currentProject && viewProjectCode(currentProject)}
                    className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors flex items-center space-x-2"
                  >
                    <Code className="w-4 h-4" />
                    <span>View Code</span>
                  </button>
                  <button 
                    onClick={() => openInNewTab('https://todoapp-example.vercel.app')}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Open in New Tab
                  </button>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-8 text-center">
                <div className="mb-4">
                  <h4 className="text-xl font-semibold text-gray-900 mb-2">TodoApp</h4>
                  <p className="text-gray-600">A modern, full-stack application</p>
                </div>
                <div className="space-y-2 text-sm text-gray-600">
                  <p><strong>Features:</strong></p>
                  <p>React frontend</p>
                  <p>Express.js backend</p>
                  <p>REST API</p>
                  <p>Modern UI</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div>
            <div className="flex justify-between items-center mb-8">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
                <p className="text-gray-600">Track your app performance and usage</p>
              </div>
              <div className="flex items-center space-x-4">
                <button className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900">
                  <TrendingUp className="w-4 h-4" />
                  <span>Static</span>
                </button>
                <button 
                  onClick={() => setIsLive(!isLive)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    isLive ? 'bg-green-600 text-white' : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {isLive ? 'Live' : 'Start Live'}
                </button>
              </div>
            </div>

            {/* Analytics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {[
                { title: 'Total Builds', value: '24', change: -12, icon: Code, color: 'blue' },
                { title: 'Deployments', value: '18', change: -8, icon: Rocket, color: 'green' },
                { title: 'API Calls', value: '1.2k', change: -24, icon: Zap, color: 'purple' },
                { title: 'Build Time', value: '3.2m', change: 15, icon: Clock, color: 'orange' }
              ].map((metric, index) => (
                <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      metric.color === 'blue' ? 'bg-blue-100 text-blue-600' :
                      metric.color === 'green' ? 'bg-green-100 text-green-600' :
                      metric.color === 'purple' ? 'bg-purple-100 text-purple-600' :
                      'bg-orange-100 text-orange-600'
                    }`}>
                      <metric.icon className="w-5 h-5" />
                    </div>
                    <div className={`flex items-center space-x-1 text-sm ${
                      metric.change > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {metric.change > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                      <span>{Math.abs(metric.change)}</span>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">{metric.title}</p>
                    <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Build Activity</h3>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  Chart visualization would go here
                </div>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  Performance chart would go here
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'projects' && (
          <div>
            <div className="flex justify-between items-center mb-8">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
                <p className="text-gray-600">Manage your generated applications</p>
              </div>
              <div className="flex items-center space-x-4">
                <button className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900">
                  <TrendingUp className="w-4 h-4" />
                  <span>Static</span>
                </button>
                <button 
                  onClick={() => setIsLive(!isLive)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    isLive ? 'bg-green-600 text-white' : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {isLive ? 'Live' : 'Start Live'}
                </button>
                <button 
                  onClick={handleNewProject}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>New Project</span>
                </button>
              </div>
            </div>

            {/* Project Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-blue-100 text-blue-600">
                    <Folder className="w-5 h-5" />
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Projects</p>
                  <p className="text-2xl font-bold text-gray-900">{projectStats.total_projects}</p>
                </div>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-green-100 text-green-600">
                    <CheckCircle className="w-5 h-5" />
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Deployed</p>
                  <p className="text-2xl font-bold text-gray-900">{projectStats.deployed}</p>
                </div>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-yellow-100 text-yellow-600">
                    <Loader className="w-5 h-5" />
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Building</p>
                  <p className="text-2xl font-bold text-gray-900">{projectStats.building}</p>
                </div>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-purple-100 text-purple-600">
                    <Eye className="w-5 h-5" />
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Views</p>
                  <p className="text-2xl font-bold text-gray-900">{projectStats.total_views}</p>
                </div>
              </div>
            </div>

            {/* Project Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {projects.length > 0 ? projects.map(project => (
                <div key={project.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      project.status === 'completed' ? 'bg-green-100 text-green-700' :
                      project.status === 'generating' ? 'bg-blue-100 text-blue-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {project.status === 'completed' ? 'deployed' : project.status}
                    </div>
                    <button className="p-1 text-gray-400 hover:text-gray-600">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </div>
                  
                  <h3 className="font-semibold text-gray-900 mb-2">{project.name}</h3>
                  <p className="text-sm text-gray-600 mb-4">{project.description}</p>
                  
                  <div className="space-y-2 mb-4 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Framework</span>
                      <span className="font-medium">{project.framework}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Progress</span>
                      <span className="font-medium">{project.progress || 0}%</span>
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors flex items-center justify-center space-x-1 ${
                      project.status === 'completed' 
                        ? 'bg-blue-600 text-white hover:bg-blue-700' 
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}>
                      <Eye className="w-4 h-4" />
                      <span>{project.status === 'completed' ? 'View Live' : 'Deploy'}</span>
                    </button>
                    <button 
                      onClick={() => viewProjectCode(project)}
                      className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                      title="View Code"
                    >
                      <Code className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                      <ExternalLink className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )) : (
                <div className="col-span-3 text-center py-12">
                  <p className="text-gray-500">No projects yet. Create your first project!</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Chat Sidebar */}
      {chatOpen && (
        <div className="fixed right-0 top-0 h-full w-80 bg-white border-l border-gray-200 flex flex-col z-40">
          <div className="p-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h3 className="font-semibold text-gray-900">AI Assistant</h3>
              <button
                onClick={() => setChatOpen(false)}
                className="p-1 text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {chatMessages.map(message => (
              <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs px-3 py-2 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  <p className="text-sm">{message.content}</p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                placeholder="Ask me anything..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              />
              <button
                onClick={sendChatMessage}
                className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Code Modal */}
      {showCodeModal && selectedProject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">Generated Code - {selectedProject.name}</h2>
                <button
                  onClick={() => setShowCodeModal(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="space-y-6">
                {/* Specifications */}
                {selectedProject.specifications && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-3">Requirements & Specifications</h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                        {typeof selectedProject.specifications === 'string' 
                          ? selectedProject.specifications 
                          : JSON.stringify(selectedProject.specifications, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Architecture */}
                {selectedProject.architecture && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-3">System Architecture</h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                        {typeof selectedProject.architecture === 'string' 
                          ? selectedProject.architecture 
                          : JSON.stringify(selectedProject.architecture, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Design */}
                {selectedProject.design && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-3">UI/UX Design</h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                        {typeof selectedProject.design === 'string' 
                          ? selectedProject.design 
                          : JSON.stringify(selectedProject.design, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Generated Code */}
                {selectedProject.generated_code && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-3">Generated Code</h3>
                    <div className="bg-gray-900 rounded-lg p-4">
                      <pre className="text-sm text-green-400 whitespace-pre-wrap overflow-x-auto">
                        {typeof selectedProject.generated_code === 'string' 
                          ? selectedProject.generated_code 
                          : JSON.stringify(selectedProject.generated_code, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Tech Stack */}
                {selectedProject.tech_stack && selectedProject.tech_stack.length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-3">Technology Stack</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedProject.tech_stack.map((tech, index) => (
                        <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Features */}
                {selectedProject.features && selectedProject.features.length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-3">Features</h3>
                    <ul className="list-disc list-inside space-y-1">
                      {selectedProject.features.map((feature, index) => (
                        <li key={index} className="text-gray-700">{feature}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* No Code Available */}
                {!selectedProject.specifications && !selectedProject.architecture && 
                 !selectedProject.design && !selectedProject.generated_code && (
                  <div className="text-center py-8">
                    <Code className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">No generated code available yet.</p>
                    <p className="text-sm text-gray-400 mt-2">Code will appear here once the AI agents complete the generation process.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAppBuilder;