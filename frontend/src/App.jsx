import { useEffect, useMemo, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

const quickPrompts = [
  'Menüde neler var?',
  'Sıcak içecekler neler?',
  'Ana yemekler neler?',
  'Fıstık alerjim var, tatlı önerir misin?',
  '100 liranın altında ne var?',
]

function App() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'ResQAI hazır. Menü, fiyat ve alerjen sorularını sorabilirsin.',
      intent: 'system',
    },
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [health, setHealth] = useState('checking')

  useEffect(() => {
    let cancelled = false

    async function checkHealth() {
      try {
        const response = await fetch(`${API_BASE_URL}/health`)
        if (!response.ok) {
          throw new Error('API yanıt vermedi')
        }
        if (!cancelled) {
          setHealth('connected')
        }
      } catch {
        if (!cancelled) {
          setHealth('offline')
        }
      }
    }

    checkHealth()
    return () => {
      cancelled = true
    }
  }, [])

  const canSend = useMemo(() => message.trim().length > 0 && !loading, [message, loading])

  async function sendMessage(text) {
    const outgoing = text.trim()
    if (!outgoing || loading) return

    setError('')
    setLoading(true)
    setMessage('')
    setMessages((current) => [...current, { role: 'user', text: outgoing }])

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: outgoing }),
      })

      if (!response.ok) {
        const payload = await response.json().catch(() => null)
        throw new Error(payload?.detail ?? 'Mesaj gönderilemedi')
      }

      const data = await response.json()
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          text: data.reply,
          intent: data.intent,
        },
      ])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Beklenmeyen bir hata oluştu')
    } finally {
      setLoading(false)
    }
  }

  function handleSubmit(event) {
    event.preventDefault()
    sendMessage(message)
  }

  return (
    <div className="app-shell">
      <div className="background-glow background-glow-left" />
      <div className="background-glow background-glow-right" />

      <main className="layout">
        <section className="hero-card">
          <div className="hero-copy">
            <p className="eyebrow">ResQAI Bistro & Coffee</p>
            <h1>Restaurant asistanı, hızlı menü ve alerjen desteği.</h1>
            <p className="lead">
              Intent classification + rule-based filtreleme ile çalışan lokal chatbot.
              Menü, fiyat ve güvenli önerileri tek ekranda test edebilirsin.
            </p>

            <div className="status-row">
              <span className={`status-pill status-${health}`}>
                {health === 'connected' ? 'API bağlı' : health === 'offline' ? 'API kapalı' : 'API kontrol ediliyor'}
              </span>
              <span className="status-note">{API_BASE_URL}</span>
            </div>
          </div>

          <div className="prompt-panel">
            <p className="panel-title">Hızlı denemeler</p>
            <div className="prompt-grid">
              {quickPrompts.map((prompt) => (
                <button key={prompt} type="button" className="prompt-chip" onClick={() => sendMessage(prompt)}>
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        </section>

        <section className="chat-card">
          <div className="chat-header">
            <div>
              <p className="eyebrow">Canlı Chat</p>
              <h2>Model ile konuş</h2>
            </div>
            <span className={`live-badge ${loading ? 'typing' : ''}`}>{loading ? 'Yanıt hazırlanıyor' : 'Hazır'}</span>
          </div>

          <div className="message-list" role="log" aria-live="polite">
            {messages.map((entry, index) => (
              <article key={`${entry.role}-${index}-${entry.text.slice(0, 18)}`} className={`message message-${entry.role}`}>
                <div className="message-meta">
                  <span>{entry.role === 'user' ? 'Sen' : 'ResQAI'}</span>
                  {entry.intent ? <span className="intent-tag">{entry.intent}</span> : null}
                </div>
                <p>{entry.text}</p>
              </article>
            ))}
          </div>

          {error ? <div className="error-banner">{error}</div> : null}

          <form className="composer" onSubmit={handleSubmit}>
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Örn: Pizza ve wrap var mı? / 100 liranın altında ne var? / Fıstık alerjim var"
              rows={3}
            />
            <div className="composer-footer">
              <span className="helper-text">Enter ile gönderebilirsin</span>
              <button type="submit" disabled={!canSend}>
                Gönder
              </button>
            </div>
          </form>
        </section>
      </main>
    </div>
  )
}

export default App
