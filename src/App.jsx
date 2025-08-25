// src/App.jsx
import { useEffect, useState } from 'react'
import { api } from './lib/api'
import { socket } from './lib/socket'

export default function App() {
  const [logs, setLogs] = useState<string[]>([])

  useEffect(() => {
    socket.on('server_message', (m) => setLogs(l => [...l, `server: ${JSON.stringify(m)}`]))
    socket.on('progress', (m) => setLogs(l => [...l, `progress: ${m.step}`]))
    return () => {
      socket.off('server_message'); socket.off('progress');
    }
  }, [])

  const start = async () => {
    const { data } = await api.post('/generate', { idea: 'SaaS Starter' })
    setLogs(l => [...l, `generate: ${JSON.stringify(data)}`])
    socket.emit('start_generation', { idea: data.projectName })
  }

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold">AI App Builder Pro</h1>
      <button className="mt-4 px-4 py-2 border rounded" onClick={start}>Generate</button>
      <pre className="mt-6 bg-black/5 p-4 rounded whitespace-pre-wrap">{logs.join('\n')}</pre>
    </main>
  )
}
