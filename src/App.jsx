import React, { useState, useEffect, useCallback, useRef } from 'react'
import { AlertTriangle, Wifi, WifiOff, Loader, CheckCircle, XCircle } from 'lucide-react'
import './App.css'

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    })
    
    // Log to monitoring service in production
    console.error('Error Boundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
            <div className="flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mx-auto mb-4">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 text-center mb-2">
              Something went wrong
            </h2>
            <p className="text-gray-600 text-center mb-6">
              We apologize for the inconvenience. Please refresh the page or try again later.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Refresh Page
            </button>
            {process.env.NODE_ENV === 'development' && (
              <details className="mt-4">
                <summary className="text-sm text-gray-500 cursor-pointer">Error Details</summary>
                <pre className="mt-2 text-xs text-gray-600 bg-gray-100 p-2 rounded overflow-auto">
                  {this.state.error && this.state.error.toString()}
                  <br />
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Enhanced Socket Service
class SocketService {
  constructor() {
    this.socket = null
    this.listeners = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
  }

  connect() {
    if (typeof window !== 'undefined' && window.io) {
      this.socket = window.io('/', {
        autoConnect: true,
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: this.reconnectDelay,
        reconnectionDelayMax: 5000,
        maxReconnectionAttempts: this.maxReconnectAttempts,
        timeout: 20000,
        transports: ['websocket', 'polling']
      })

      this.socket.on('connect', () => {
        this.reconnectAttempts = 0
        this.emit('connection_status', { connected: true })
      })

      this.socket.on('disconnect', () => {
        this.emit('connection_status', { connected: false })
      })

      this.socket.on('connect_error', (error) => {
        console.error('Socket connection error:', error)
        this.emit('connection_error', error)
      })

      return this.socket
    }
    return null
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event).add(callback)
    
    if (this.socket) {
      this.socket.on(event, callback)
    }
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback)
    }
    
    if (this.socket) {
      this.socket.off(event, callback)
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data))
    }
    
    if (this.socket) {
      this.socket.emit(event, data)
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
    this.listeners.clear()
  }
}

// API Service
class APIService {
  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || '/api'
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body)
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || `HTTP Error: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error(`API Request failed: ${endpoint}`, error)
      throw error
    }
  }

  // Project methods
  async getProjects() {
    return this.request('/projects')
  }

  async createProject(projectData) {
    return this.request('/projects', {
      method: 'POST',
      body: projectData
    })
  }

  async getProject(id) {
    return this.request(`/projects/${id}`)
  }

  async updateProject(id, updates) {
    return this.request(`/projects/${id}`, {
      method: 'PUT',
      body: updates
    })
  }

  async deleteProject(id) {
    return this.request(`/projects/${id}`, {
      method: 'DELETE'
    })
  }

  // Generation methods
  async startGeneration(projectId, description) {
    return this.request('/generation/start', {
      method: 'POST',
      body: { project_id: projectId, description }
    })
  }

  async getGenerationStatus(projectId) {
    return this.request(`/generation/status/${projectId}`)
  }

  async cancelGeneration(projectId) {
    return this.request(`/generation/cancel/${projectId}`, {
      method: 'POST'
    })
  }
}

// Main App Component
function App() {
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState(null)
  const [projects, setProjects] = useState([])
  const [currentProject, setCurrentProject] = useState(null)
  const [generationLogs, setGenerationLogs] = useState([])
  const [loading, setLoading] = useState({
    projects: false,
    generation: false,
    creating: false
  })
  const [error, setError] = useState(null)

  const socketRef = useRef(null)
  const apiRef = useRef(new APIService())

  // Initialize socket connection
  useEffect(() => {
    socketRef.current = new SocketService()
    const socket = socketRef.current.connect()

    if (socket) {
      socketRef.current.on('connection_status', ({ connected }) => {
        setIsConnected(connected)
        if (connected) {
          setConnectionError(null)
          addLog('âœ… Connected to AI App Builder Pro')
        } else {
          addLog('âŒ Disconnected from server')
        }
      })

      socketRef.current.on('connection_error', (error) => {
        setConnectionError(error.message)
        addLog(`ðŸ”¥ Connection error: ${error.message}`)
      })

      socketRef.current.on('generation_progress', (data) => {
        addLog(`ðŸ”„ ${data.agent}: ${data.message}`)
        if (currentProject && data.project_id === currentProject.id) {
          setCurrentProject(prev => ({
            ...prev,
            progress: data.progress,
            current_agent: data.agent
          }))
        }
      })

      socketRef.current.on('generation_complete', (data) => {
        addLog(`âœ¨ Generation completed for project ${data.project_id}`)
        setLoading(prev => ({ ...prev, generation: false }))
        loadProjects() // Refresh projects
      })

      socketRef.current.on('generation_error', (data) => {
        addLog(`ðŸ’¥ Generation failed: ${data.error}`)
        setLoading(prev => ({ ...prev, generation: false }))
        setError(data.error)
      })
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect()
      }
    }
  }, [currentProject])

  // Load projects on mount
  useEffect(() => {
    loadProjects()
  }, [])

  const addLog = useCallback((message) => {
    const timestamp = new Date().toLocaleTimeString()
    setGenerationLogs(prev => [...prev.slice(-49), `[${timestamp}] ${message}`])
  }, [])

  const loadProjects = async () => {
    try {
      setLoading(prev => ({ ...prev, projects: true }))
      const response = await apiRef.current.getProjects()
      setProjects(response.projects || [])
    } catch (error) {
      setError(`Failed to load projects: ${error.message}`)
      addLog(`âŒ Failed to load projects: ${error.message}`)
    } finally {
      setLoading(prev => ({ ...prev, projects: false }))
    }
  }

  const handleCreateProject = async (formData) => {
    try {
      setLoading(prev => ({ ...prev, creating: true }))
      setError(null)
      
      const response = await apiRef.current.createProject(formData)
      const newProject = response.project
      
      setProjects(prev => [newProject, ...prev])
      setCurrentProject(newProject)
      addLog(`ðŸŽ¯ Created project: ${newProject.name}`)
      
      return newProject
    } catch (error) {
      setError(`Failed to create project: ${error.message}`)
      addLog(`âŒ Project creation failed: ${error.message}`)
      throw error
    } finally {
      setLoading(prev => ({ ...prev, creating: false }))
    }
  }

  const handleStartGeneration = async (projectId, description) => {
    try {
      setLoading(prev => ({ ...prev, generation: true }))
      setError(null)
      
      await apiRef.current.startGeneration(projectId, description)
      addLog(`ðŸš€ Starting generation for project ${projectId}`)
      
      // Join project room for real-time updates
      if (socketRef.current) {
        socketRef.current.emit('join_project', { project_id: projectId })
      }
      
    } catch (error) {
      setError(`Failed to start generation: ${error.message}`)
      addLog(`âŒ Generation start failed: ${error.message}`)
      setLoading(prev => ({ ...prev, generation: false }))
    }
  }

  const clearError = () => setError(null)
  const clearLogs = () => setGenerationLogs([])

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  AI App Builder Pro
                </h1>
                <span className="ml-3 text-sm text-gray-500">v2.0</span>
              </div>
              
              <div className="flex items-center space-x-4">
                <ConnectionStatus 
                  isConnected={isConnected} 
                  connectionError={connectionError} 
                />
                <ProjectCounter count={projects.length} />
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Error Banner */}
          {error && (
            <ErrorBanner message={error} onDismiss={clearError} />
          )}

          {/* Grid Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column - Project Management */}
            <div className="space-y-6">
              <ProjectForm 
                onSubmit={handleCreateProject}
                loading={loading.creating}
              />
              
              <ProjectList 
                projects={projects}
                loading={loading.projects}
                onSelectProject={setCurrentProject}
                onStartGeneration={handleStartGeneration}
                currentProject={currentProject}
                generationLoading={loading.generation}
              />
            </div>

            {/* Right Column - Console & Details */}
            <div className="space-y-6">
              {currentProject && (
                <ProjectDetails 
                  project={currentProject}
                  onStartGeneration={handleStartGeneration}
                  generationLoading={loading.generation}
                />
              )}
              
              <Console 
                logs={generationLogs}
                onClear={clearLogs}
                connected={isConnected}
              />
            </div>
          </div>
        </main>
      </div>
    </ErrorBoundary>
  )
}

// Connection Status Component
const ConnectionStatus = ({ isConnected, connectionError }) => (
  <div className="flex items-center space-x-2">
    {isConnected ? (
      <>
        <Wifi className="w-4 h-4 text-green-500" />
        <span className="text-sm text-gray-600">Connected</span>
      </>
    ) : (
      <>
        <WifiOff className="w-4 h-4 text-red-500" />
        <span className="text-sm text-gray-600">
          {connectionError ? 'Error' : 'Disconnected'}
        </span>
      </>
    )}
  </div>
)

// Project Counter Component
const ProjectCounter = ({ count }) => (
  <div className="flex items-center space-x-2">
    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
    <span className="text-sm text-gray-600">{count} Projects</span>
  </div>
)

// Error Banner Component
const ErrorBanner = ({ message, onDismiss }) => (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
    <div className="flex">
      <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
      <div className="ml-3 flex-1">
        <p className="text-sm text-red-800">{message}</p>
      </div>
      <button
        onClick={onDismiss}
        className="ml-3 flex-shrink-0 text-red-400 hover:text-red-600"
      >
        <span className="sr-only">Dismiss</span>
        <XCircle className="w-5 h-5" />
      </button>
    </div>
  </div>
)

// Project Form Component
const ProjectForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    framework: 'React',
    complexity: 'medium'
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.name.trim() || !formData.description.trim()) return
    
    try {
      await onSubmit(formData)
      setFormData({ name: '', description: '', framework: 'React', complexity: 'medium' })
    } catch (error) {
      // Error is handled by parent component
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Create New Project</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Project Name
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="My Awesome App"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Describe your app idea in detail..."
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Framework
            </label>
            <select
              name="framework"
              value={formData.framework}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="React">React</option>
              <option value="Next.js">Next.js</option>
              <option value="Vue">Vue</option>
              <option value="Angular">Angular</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Complexity
            </label>
            <select
              name="complexity"
              value={formData.complexity}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="simple">Simple</option>
              <option value="medium">Medium</option>
              <option value="complex">Complex</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || !formData.name.trim() || !formData.description.trim()}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              <span>Creating...</span>
            </>
          ) : (
            <span>Create Project</span>
          )}
        </button>
      </form>
    </div>
  )
}

// Project List Component
const ProjectList = ({ 
  projects, 
  loading, 
  onSelectProject, 
  onStartGeneration, 
  currentProject,
  generationLoading 
}) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          {[...Array(3)].map((_, i) => (
            <div key={i} className="mb-4 last:mb-0">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Projects ({projects.length})
      </h2>
      
      {projects.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-gray-400 text-sm">No projects yet</div>
          <div className="text-gray-400 text-xs mt-1">Create your first project above</div>
        </div>
      ) : (
        <div className="space-y-3">
          {projects.map(project => (
            <ProjectCard
              key={project.id}
              project={project}
              isSelected={currentProject?.id === project.id}
              onSelect={() => onSelectProject(project)}
              onStartGeneration={onStartGeneration}
              generationLoading={generationLoading && currentProject?.id === project.id}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// Project Card Component
const ProjectCard = ({ 
  project, 
  isSelected, 
  onSelect, 
  onStartGeneration, 
  generationLoading 
}) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100'
      case 'generating': return 'text-blue-600 bg-blue-100'
      case 'failed': return 'text-red-600 bg-red-100'
      case 'cancelled': return 'text-yellow-600 bg-yellow-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const handleGenerate = (e) => {
    e.stopPropagation()
    onStartGeneration(project.id, project.description)
  }

  return (
    <div 
      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
        isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
      }`}
      onClick={onSelect}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-medium text-gray-900 truncate">{project.name}</h3>
        <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(project.status)}`}>
          {project.status}
        </span>
      </div>
      
      <p className="text-sm text-gray-600 line-clamp-2 mb-3">{project.description}</p>
      
      <div className="flex justify-between items-center">
        <div className="text-xs text-gray-500">
          {project.framework} â€¢ {new Date(project.created_at).toLocaleDateString()}
        </div>
        
        {project.status === 'draft' && (
          <button
            onClick={handleGenerate}
            disabled={generationLoading}
            className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-1"
          >
            {generationLoading ? (
              <>
                <Loader className="w-3 h-3 animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <span>Generate</span>
            )}
          </button>
        )}
      </div>
      
      {project.status === 'generating' && (
        <div className="mt-2 bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${project.progress || 0}%` }}
          />
        </div>
      )}
    </div>
  )
}

// Project Details Component
const ProjectDetails = ({ project, onStartGeneration, generationLoading }) => (
  <div className="bg-white rounded-lg shadow-sm border p-6">
    <h2 className="text-lg font-semibold text-gray-900 mb-4">Project Details</h2>
    
    <div className="space-y-3">
      <div>
        <div className="text-sm font-medium text-gray-700">Name</div>
        <div className="text-sm text-gray-900">{project.name}</div>
      </div>
      
      <div>
        <div className="text-sm font-medium text-gray-700">Description</div>
        <div className="text-sm text-gray-900">{project.description}</div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="text-sm font-medium text-gray-700">Framework</div>
          <div className="text-sm text-gray-900">{project.framework}</div>
        </div>
        <div>
          <div className="text-sm font-medium text-gray-700">Status</div>
          <div className="text-sm text-gray-900 capitalize">{project.status}</div>
        </div>
      </div>
      
      {project.current_agent && (
        <div>
          <div className="text-sm font-medium text-gray-700">Current Agent</div>
          <div className="text-sm text-gray-900">{project.current_agent}</div>
        </div>
      )}
      
      {project.progress > 0 && (
        <div>
          <div className="text-sm font-medium text-gray-700 mb-2">Progress</div>
          <div className="bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${project.progress}%` }}
            />
          </div>
          <div className="text-xs text-gray-500 mt-1">{project.progress}%</div>
        </div>
      )}
    </div>
  </div>
)

// Console Component
const Console = ({ logs, onClear, connected }) => (
  <div className="bg-gray-900 rounded-lg p-6">
    <div className="flex justify-between items-center mb-4">
      <h2 className="text-lg font-semibold text-white">Console</h2>
      <div className="flex items-center space-x-2">
        <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
        <button
          onClick={onClear}
          className="px-3 py-1 text-xs bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
        >
          Clear
        </button>
      </div>
    </div>
    
    <div className="bg-gray-800 rounded p-4 font-mono text-sm text-gray-300 h-64 overflow-y-auto">
      {logs.length === 0 ? (
        <div className="text-gray-500 text-center py-8">
          Console output will appear here...
        </div>
      ) : (
        logs.map((log, index) => (
          <div key={index} className="mb-1 leading-relaxed">
            {log}
          </div>
        ))
      )}
    </div>
  </div>
)

export default App
