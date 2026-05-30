import { useEffect, useMemo, useRef, useState } from 'react'

const API = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

/* ── Category config ── */
const CAT_META = {
  kahve:        { name: 'Kahveler',        icon: '☕' },
  sicak_icecek: { name: 'Sıcak İçecekler', icon: '🍵' },
  soguk_icecek: { name: 'Soğuk İçecekler', icon: '🧊' },
  kahvalti:     { name: 'Kahvaltı',        icon: '🍳' },
  atistirmalik: { name: 'Atıştırmalıklar', icon: '🥨' },
  salata:       { name: 'Salatalar',       icon: '🥗' },
  ana_yemek:    { name: 'Ana Yemekler',    icon: '🍖' },
  tatli:        { name: 'Tatlılar',        icon: '🍰' },
  pizza:        { name: 'Pizzalar',        icon: '🍕' },
  wrap:         { name: 'Dürümler',        icon: '🌯' },
  corba:        { name: 'Çorbalar',        icon: '🥣' },
  cocuk_menu:   { name: 'Çocuk Menüsü',   icon: '🧸' },
  vegan:        { name: 'Vegan',           icon: '🌱' },
  burger:       { name: 'Burgerler',       icon: '🍔' },
  makarna:      { name: 'Makarnalar',      icon: '🍝' },
}

const ALLERGENS = {
  sut: 'Süt', gluten: 'Gluten', yumurta: 'Yumurta', balik: 'Balık',
  susam: 'Susam', soya: 'Soya', kuruyemis: 'Kuruyemiş', fistik: 'Fıstık',
  hindistan_cevizi: 'H. Cevizi', cikolata: 'Çikolata', mantar: 'Mantar',
}

const QUICK = [
  'Tatlılarda neyiniz var?',
  'Glutensiz seçenekler neler?',
  '150₺ altında ne önerirsin?',
  'Çalışma saatleriniz?',
]

function img(kategori) {
  const c = kategori?.toLowerCase() || ''
  if (['kahve','sicak_icecek','soguk_icecek'].includes(c)) return '/images/espresso.png'
  if (['burger','ana_yemek','wrap','pizza','cocuk_menu'].includes(c)) return '/images/burger.png'
  if (['salata','vegan','atistirmalik','corba','kahvalti'].includes(c)) return '/images/salad.png'
  if (['tatli','makarna'].includes(c)) return '/images/dessert.png'
  return '/images/burger.png'
}

const price = n => new Intl.NumberFormat('tr-TR').format(n)

/* ═════════════════════════════════════
   App Component
   ═════════════════════════════════════ */
export default function App() {
  const [menu, setMenu]             = useState([])
  const [activeCat, setActiveCat]   = useState('')
  const [excluded, setExcluded]     = useState([])
  const [filterOpen, setFilterOpen] = useState(false)
  const [dark, setDark]             = useState(() => localStorage.getItem('resqai-theme') === 'dark')
  const [expandedCard, setExpandedCard] = useState(null)

  /* chat */
  const [chatOpen, setChatOpen]     = useState(false)
  const [msg, setMsg]               = useState('')
  const [history, setHistory]       = useState([
    { from: 'ai', text: 'Merhaba! 👋 Menü, fiyatlar, alerjenler veya öneriler hakkında yardımcı olabilirim. Nasıl yardımcı olayım?' },
  ])
  const [sending, setSending]       = useState(false)
  const [chatErr, setChatErr]       = useState('')
  const [sid]                       = useState(() => 'S' + Math.random().toString(36).slice(2, 8))
  const chatEndRef                  = useRef(null)
  const catScrollRef                = useRef(null)

  /* theme */
  useEffect(() => { localStorage.setItem('resqai-theme', dark ? 'dark' : 'light') }, [dark])

  /* load menu */
  useEffect(() => {
    fetch(`${API}/menu`)
      .then(r => r.json())
      .then(d => {
        const items = d.menu || []
        setMenu(items)
        if (items.length) setActiveCat(Array.from(new Set(items.map(i => i.kategori)))[0])
      })
      .catch(() => {})
  }, [])

  /* auto-scroll chat */
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [history, sending])

  /* derived */
  const cats = useMemo(() => Array.from(new Set(menu.map(i => i.kategori))), [menu])

  const items = useMemo(() =>
    menu.filter(i => {
      if (i.kategori !== activeCat) return false
      if (excluded.length && (i.alerjenler || []).some(a => excluded.includes(a))) return false
      return true
    }),
  [menu, activeCat, excluded])

  const catInfo = k => CAT_META[k] || { name: k, icon: '🍴' }

  /* send chat */
  async function send(text) {
    const t = (text ?? msg).trim()
    if (!t || sending) return
    setChatErr('')
    setSending(true)
    setMsg('')
    setHistory(h => [...h, { from: 'user', text: t }])
    try {
      const r = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: t, session_id: sid }),
      })
      if (!r.ok) throw new Error((await r.json().catch(() => null))?.detail ?? 'Hata')
      const d = await r.json()
      setHistory(h => [...h, { from: 'ai', text: d.reply, intent: d.intent }])
    } catch (e) {
      setChatErr(e.message)
    } finally {
      setSending(false)
    }
  }

  const toggleAllergen = a => setExcluded(p => p.includes(a) ? p.filter(x => x !== a) : [...p, a])

  /* ── JSX ── */
  return (
    <div className={`app ${dark ? 'dark' : 'light'}`}>

      {/* ═══ HEADER ═══ */}
      <header className="header">
        <div className="header-inner">
          <div className="brand">
            <div className="brand-icon">R</div>
            <div className="brand-text">
              <h1>ResQAI</h1>
              <span>Bistro & Coffee</span>
            </div>
          </div>
          <div className="header-actions">
            <div className="table-badge">
              <span className="table-label">MASA</span>
              <span className="table-num">14</span>
            </div>
            <button
              className="theme-btn"
              onClick={() => setDark(d => !d)}
              aria-label="Tema değiştir"
            >
              <span className={`theme-icon ${dark ? 'sun' : 'moon'}`}>
                {dark ? '☀️' : '🌙'}
              </span>
            </button>
          </div>
        </div>
      </header>

      {/* ═══ CATEGORIES ═══ */}
      <nav className="categories" ref={catScrollRef}>
        <div className="categories-track">
          {cats.map(c => {
            const info = catInfo(c)
            return (
              <button
                key={c}
                className={`cat-pill ${activeCat === c ? 'active' : ''}`}
                onClick={() => { setActiveCat(c); setExpandedCard(null) }}
              >
                <span className="cat-emoji">{info.icon}</span>
                <span className="cat-name">{info.name}</span>
              </button>
            )
          })}
        </div>
      </nav>

      {/* ═══ CONTENT ═══ */}
      <main className="content">

        {/* ─── Filter ─── */}
        <div className="filter-section">
          <button className="filter-toggle" onClick={() => setFilterOpen(f => !f)}>
            <div className="filter-left">
              <svg className="filter-svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
              </svg>
              <span>Alerjen Filtresi</span>
              {excluded.length > 0 && <span className="filter-count">{excluded.length}</span>}
            </div>
            <svg className={`filter-chev ${filterOpen ? 'open' : ''}`} width="16" height="16" viewBox="0 0 16 16">
              <path d="M4 6l4 4 4-4" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          {filterOpen && (
            <div className="filter-panel">
              <p className="filter-hint">İstemediğiniz alerjenleri seçerek menüden gizleyin:</p>
              <div className="filter-chips">
                {Object.entries(ALLERGENS).map(([k, v]) => (
                  <button
                    key={k}
                    className={`allergen-chip ${excluded.includes(k) ? 'excluded' : ''}`}
                    onClick={() => toggleAllergen(k)}
                  >
                    <span>{v}</span>
                    <span className="chip-x">{excluded.includes(k) ? '✕' : '+'}</span>
                  </button>
                ))}
              </div>
              {excluded.length > 0 && (
                <button className="filter-clear" onClick={() => setExcluded([])}>
                  Tümünü Temizle
                </button>
              )}
            </div>
          )}
        </div>

        {/* ─── Section Header ─── */}
        <div className="section-header">
          <div className="section-left">
            <span className="section-emoji">{catInfo(activeCat).icon}</span>
            <h2>{catInfo(activeCat).name}</h2>
          </div>
          <span className="section-count">{items.length} ürün</span>
        </div>

        {/* ─── Menu Grid ─── */}
        {items.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🍽️</div>
            <h3>Ürün Bulunamadı</h3>
            <p>Seçili alerjen filtrelerine uygun ürün yok.</p>
            {excluded.length > 0 && (
              <button className="empty-reset" onClick={() => setExcluded([])}>
                Filtreleri Temizle
              </button>
            )}
          </div>
        ) : (
          <div className="menu-grid">
            {items.map((item, idx) => {
              const isExpanded = expandedCard === item.id
              return (
                <article
                  key={item.id}
                  className={`menu-card ${isExpanded ? 'expanded' : ''}`}
                  style={{ animationDelay: `${idx * 50}ms` }}
                  onClick={() => setExpandedCard(isExpanded ? null : item.id)}
                >
                  {/* Image */}
                  <div className="card-visual">
                    <img src={img(item.kategori)} alt={item.isim} loading="lazy" />
                    <div className="card-overlay" />
                    <div className="card-price-tag">{price(item.fiyat)}₺</div>
                  </div>

                  {/* Info */}
                  <div className="card-info">
                    <h3 className="card-title">{item.isim}</h3>

                    <p className="card-ingredients">
                      {item.icerik?.join(', ')}
                    </p>

                    {/* Allergens */}
                    <div className="card-allergens">
                      {item.alerjenler?.length > 0 ? (
                        item.alerjenler.map(a => (
                          <span key={a} className={`allergen-tag ${excluded.includes(a) ? 'danger' : ''}`}>
                            {ALLERGENS[a] || a}
                          </span>
                        ))
                      ) : (
                        <span className="no-allergen">✓ Alerjen yok</span>
                      )}
                    </div>
                  </div>
                </article>
              )
            })}
          </div>
        )}
      </main>

      {/* ═══ AI FAB ═══ */}
      <button
        className={`ai-fab ${chatOpen ? 'open' : ''}`}
        onClick={() => setChatOpen(o => !o)}
        aria-label="AI Asistan"
      >
        <span className="fab-icon">{chatOpen ? '✕' : '✦'}</span>
        {!chatOpen && <span className="fab-label">AI Asistan</span>}
        <span className="fab-pulse" />
      </button>

      {/* ═══ CHAT PANEL ═══ */}
      {chatOpen && <div className="chat-overlay" onClick={() => setChatOpen(false)} />}
      <aside className={`chat-panel ${chatOpen ? 'visible' : ''}`}>
        {/* Head */}
        <div className="chat-header">
          <div className="chat-brand">
            <div className="chat-logo">✦</div>
            <div>
              <div className="chat-name">ResQAI Asistan</div>
              <div className="chat-status">Çevrimiçi</div>
            </div>
          </div>
          <button className="chat-close" onClick={() => setChatOpen(false)}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        {/* Messages */}
        <div className="chat-messages">
          {history.map((m, i) => (
            <div key={i} className={`msg ${m.from}`}>
              {m.from === 'ai' && <div className="msg-avatar">✦</div>}
              <div className="msg-bubble">
                <p>{m.text}</p>
              </div>
            </div>
          ))}
          {sending && (
            <div className="msg ai">
              <div className="msg-avatar">✦</div>
              <div className="msg-bubble">
                <div className="typing"><span/><span/><span/></div>
              </div>
            </div>
          )}
          {chatErr && <div className="msg-error">{chatErr}</div>}
          <div ref={chatEndRef} />
        </div>

        {/* Quick suggestions */}
        <div className="chat-suggestions">
          {QUICK.map(q => (
            <button key={q} className="quick-btn" onClick={() => send(q)} disabled={sending}>{q}</button>
          ))}
        </div>

        {/* Input */}
        <form className="chat-input" onSubmit={e => { e.preventDefault(); send() }}>
          <input
            value={msg}
            onChange={e => setMsg(e.target.value)}
            placeholder="Mesajınızı yazın…"
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }}}
          />
          <button type="submit" className="send-btn" disabled={!msg.trim() || sending}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </form>
      </aside>

    </div>
  )
}
