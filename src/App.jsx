import { useState, useEffect } from 'react'
import { socket } from './services/socket'
import { api } from './services/api'
import Header from './components/Header'
import ProjectForm from './components/ProjectForm'
import Console from './components/Console'

function App() {
  const [logs, setLogs] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [project, setProject] = useState(null)

  useEffect(() => {
    function onConnect() {
      setIsConnected(true)
    }

    function onDisconnect() {
      setIsConnected(false)
    }

    function onServerMessage(message) {
      setLogs(prev => [...prev, `server: ${JSON.stringify(message)}`])
    }

    function onProgress(data) {
      setLogs(prev => [...prev, `progress: ${data.step}`])
    }

    socket.on('connect', onConnect)
    socket.on('disconnect', onDisconnect)
    socket.on('server_message', onServerMessage)
    socket.on('progress', onProgress)

    return () => {
      socket.off('connect', onConnect)
      socket.off('disconnect', onDisconnect)
      socket.off('server_message', onServerMessage)
      socket.off('progress', onProgress)
    }
  }, [])

  const handleProjectSubmit = async (projectData) => {
    try {
      const { data } = await api.post('/api/projects', projectData)
      setProject(data)
      setLogs(prev => [...prev, `Project created: ${data.name}`])
      socket.emit('start_generation', { projectId: data.id })
    } catch (error) {
      setLogs(prev => [...prev, `Error: ${error.message}`])
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header isConnected={isConnected} />
      <main className="container mx-auto px-4 py-8">
        <ProjectForm onSubmit={handleProjectSubmit} />
        <Console logs={logs} />
      </main>
    </div>
  )
}

export default App
