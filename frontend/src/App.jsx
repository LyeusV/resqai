import { useEffect, useMemo, useRef, useState } from 'react'

const API = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

/* ── Data Maps ── */
const CAT = {
  kahve:        'Kahveler',
  sicak_icecek: 'Sıcak İçecekler',
  soguk_icecek: 'Soğuk İçecekler',
  kahvalti:     'Kahvaltı',
  atistirmalik: 'Atıştırmalıklar',
  salata:       'Salatalar',
  ana_yemek:    'Ana Yemekler',
  tatli:        'Tatlılar',
  pizza:        'Pizzalar',
  wrap:         'Dürümler',
  corba:        'Çorbalar',
  cocuk_menu:   'Çocuk Menüsü',
  vegan:        'Vegan',
  burger:       'Burgerler',
  makarna:      'Makarnalar',
}

const ALLERGENS = {
  sut:              'Süt',
  gluten:           'Gluten',
  yumurta:          'Yumurta',
  balik:            'Balık',
  susam:            'Susam',
  soya:             'Soya',
  kuruyemis:        'Kuruyemiş',
  fistik:           'Fıstık',
  hindistan_cevizi: 'H. Cevizi',
  cikolata:         'Çikolata',
}

const SUGGESTIONS = [
  'Tatlılarda neyiniz var?',
  'Glutensiz seçenekler neler?',
  '150₺ altında ne önerirsin?',
  'Çalışma saatleriniz?',
]

/* image by category */
function catImage(kategori) {
  const c = kategori?.toLowerCase() || ''
  if (['kahve','sicak_icecek','soguk_icecek'].includes(c)) return '/images/espresso.png'
  if (['burger','ana_yemek','wrap','pizza','cocuk_menu'].includes(c)) return '/images/burger.png'
  if (['salata','vegan','atistirmalik','corba','kahvalti'].includes(c)) return '/images/salad.png'
  if (['tatli','makarna'].includes(c)) return '/images/dessert.png'
  return '/images/burger.png'
}

const fmt = n => new Intl.NumberFormat('tr-TR').format(n)

/* ═══════════════════════════════════════
   App
   ═══════════════════════════════════════ */
export default function App() {
  const [menu, setMenu]             = useState([])
  const [cat, setCat]               = useState('')
  const [excluded, setExcluded]     = useState([])
  const [filterOpen, setFilterOpen] = useState(false)
  const [dark, setDark]             = useState(() => localStorage.getItem('theme') === 'dark')

  /* chat */
  const [chatOpen, setChatOpen]     = useState(false)
  const [msg, setMsg]               = useState('')
  const [history, setHistory]       = useState([
    { from: 'ai', text: 'Merhaba! Menü, fiyatlar veya alerjenler hakkında yardımcı olabilirim.' },
  ])
  const [sending, setSending]       = useState(false)
  const [err, setErr]               = useState('')
  const [sid]                       = useState(() => 'S' + Math.random().toString(36).slice(2, 8))
  const chatEnd                     = useRef(null)

  /* theme persist */
  useEffect(() => { localStorage.setItem('theme', dark ? 'dark' : 'light') }, [dark])

  /* load menu */
  useEffect(() => {
    fetch(`${API}/menu`)
      .then(r => r.json())
      .then(d => {
        const items = d.menu || []
        setMenu(items)
        if (items.length) setCat(Array.from(new Set(items.map(i => i.kategori)))[0])
      })
      .catch(() => {})
  }, [])

  /* auto-scroll chat */
  useEffect(() => { chatEnd.current?.scrollIntoView({ behavior: 'smooth' }) }, [history, sending])

  /* derived */
  const cats = useMemo(() => Array.from(new Set(menu.map(i => i.kategori))), [menu])

  const items = useMemo(() =>
    menu.filter(i => {
      if (i.kategori !== cat) return false
      if (excluded.length) {
        const a = i.alerjenler || []
        if (excluded.some(e => a.includes(e))) return false
      }
      return true
    }),
  [menu, cat, excluded])

  /* chat */
  async function send(text) {
    const t = (text ?? msg).trim()
    if (!t || sending) return
    setErr('')
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
      setErr(e.message)
    } finally {
      setSending(false)
    }
  }

  const toggle = a => setExcluded(p => p.includes(a) ? p.filter(x => x !== a) : [...p, a])

  /* ── RENDER ── */
  return (
    <div className={`root ${dark ? 'dark' : 'light'}`}>

      {/* ═══ TOP BAR ═══ */}
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <h1 className="logo">ResQAI <span>Bistro & Coffee</span></h1>
          </div>
          <div className="topbar-right">
            <span className="table-chip">Masa 14</span>
            <button className="icon-btn" onClick={() => setDark(d => !d)} aria-label="Tema">
              {dark ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
      </header>

      {/* ═══ CATEGORY TABS ═══ */}
      <nav className="cattabs">
        <div className="cattabs-scroll">
          {cats.map(c => (
            <button key={c} className={`cattab ${cat === c ? 'on' : ''}`} onClick={() => setCat(c)}>
              {CAT[c] || c}
            </button>
          ))}
        </div>
      </nav>

      {/* ═══ MAIN ═══ */}
      <main className="main">

        {/* allergen filter */}
        <div className="filter-bar">
          <button className="filter-trigger" onClick={() => setFilterOpen(f => !f)}>
            <span className="ft-left">
              <span className="ft-icon">⚠️</span>
              <span>Alerjen Filtresi</span>
              {excluded.length > 0 && <span className="fbadge">{excluded.length}</span>}
            </span>
            <svg className={`chev ${filterOpen ? 'up' : ''}`} width="14" height="14" viewBox="0 0 14 14">
              <path d="M3.5 5.25L7 8.75L10.5 5.25" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          {filterOpen && (
            <div className="filter-body">
              <div className="filter-chips">
                {Object.entries(ALLERGENS).map(([k, v]) => (
                  <button key={k} className={`fchip ${excluded.includes(k) ? 'on' : ''}`} onClick={() => toggle(k)}>{v}</button>
                ))}
              </div>
              {excluded.length > 0 && (
                <button className="clear-link" onClick={() => setExcluded([])}>Filtreleri temizle</button>
              )}
            </div>
          )}
        </div>

        {/* section title */}
        <div className="section-head">
          <h2 className="section-title">{CAT[cat] || cat}</h2>
          <span className="item-count">{items.length} ürün</span>
        </div>

        {/* menu grid */}
        {items.length === 0 ? (
          <div className="empty">
            <p>Seçili filtrelere uygun ürün bulunamadı.</p>
            {excluded.length > 0 && (
              <button className="empty-btn" onClick={() => setExcluded([])}>Filtreleri Temizle</button>
            )}
          </div>
        ) : (
          <div className="grid">
            {items.map((item, idx) => (
              <article key={item.id} className="card" style={{ animationDelay: `${idx * 40}ms` }}>
                <div className="card-img">
                  <img src={catImage(item.kategori)} alt={item.isim} loading="lazy" />
                  <span className="card-cat">{CAT[item.kategori] || item.kategori}</span>
                </div>
                <div className="card-body">
                  <div className="card-top">
                    <h3 className="card-name">{item.isim}</h3>
                    <span className="card-price">{fmt(item.fiyat)}₺</span>
                  </div>
                  <p className="card-desc">{item.icerik?.join(', ')}</p>
                  <div className="card-foot">
                    {item.alerjenler?.length > 0 ? (
                      <div className="card-tags">
                        {item.alerjenler.map(a => (
                          <span key={a} className={`tag ${excluded.includes(a) ? 'warn' : ''}`}>
                            {ALLERGENS[a] || a}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="safe">✓ Alerjen içermez</span>
                    )}
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>

      {/* ═══ FAB ═══ */}
      <button className="fab" onClick={() => setChatOpen(o => !o)} aria-label="AI Asistan">
        {chatOpen ? '✕' : '✦'}
      </button>

      {/* ═══ CHAT ═══ */}
      {chatOpen && <div className="overlay" onClick={() => setChatOpen(false)} />}
      <div className={`chat ${chatOpen ? 'open' : ''}`}>
        <div className="chat-head">
          <div className="chat-head-left">
            <span className="chat-avatar">✦</span>
            <span className="chat-title">ResQAI Asistan</span>
          </div>
          <button className="icon-btn sm" onClick={() => setChatOpen(false)}>✕</button>
        </div>

        <div className="chat-body">
          {history.map((m, i) => (
            <div key={i} className={`bubble ${m.from}`}>
              <p>{m.text}</p>
            </div>
          ))}
          {sending && (
            <div className="bubble ai">
              <div className="dots"><span/><span/><span/></div>
            </div>
          )}
          {err && <div className="chat-err">{err}</div>}
          <div ref={chatEnd} />
        </div>

        <div className="suggestions">
          {SUGGESTIONS.map(s => (
            <button key={s} className="sug" onClick={() => send(s)} disabled={sending}>{s}</button>
          ))}
        </div>

        <form className="composer" onSubmit={e => { e.preventDefault(); send() }}>
          <input
            value={msg}
            onChange={e => setMsg(e.target.value)}
            placeholder="Bir şey sorun…"
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }}}
          />
          <button type="submit" disabled={!msg.trim() || sending}>↑</button>
        </form>
      </div>
    </div>
  )
}
