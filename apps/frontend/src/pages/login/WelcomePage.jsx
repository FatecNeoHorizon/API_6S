import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { initiateOAuthLogin, exchangeCodeForToken } from '@/api/auth'
import { saveClientSession } from '@/api/consent'
import zeusWelcomeImage from '@/assets/zeus_welcome_image.jpg'

export function WelcomePage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  async function handleLogin() {
    if (loading) return
    setLoading(true)

    const url = await initiateOAuthLogin()

    const w = 480, h = 640
    const left = Math.round(screen.width / 2 - w / 2)
    const top  = Math.round(screen.height / 2 - h / 2)
    const popup = window.open(url, 'keycloak-login', `width=${w},height=${h},left=${left},top=${top},scrollbars=yes`)

    if (!popup) {
      window.location.href = url
      return
    }

    function handleMessage(event) {
      if (event.origin !== window.location.origin) return
      if (event.data?.type !== 'oauth_code') return

      window.removeEventListener('message', handleMessage)
      clearInterval(pollClosed)

      const { code, state } = event.data
      const storedState   = sessionStorage.getItem('pkce_state')
      const codeVerifier  = sessionStorage.getItem('pkce_verifier')
      sessionStorage.removeItem('pkce_state')
      sessionStorage.removeItem('pkce_verifier')

      if (!storedState || state !== storedState || !codeVerifier) {
        setLoading(false)
        return
      }

      exchangeCodeForToken({
        code,
        code_verifier: codeVerifier,
        redirect_uri: `${window.location.origin}/auth/callback`,
      })
        .then(res => {
          saveClientSession(res.access_token, { refreshToken: res.refresh_token })
          if (res.kc_id_token) sessionStorage.setItem('kc_id_token', res.kc_id_token)
          navigate(res.pending_consent ? '/consent' : '/dashboard')
        })
        .catch(() => setLoading(false))
    }

    window.addEventListener('message', handleMessage)

    const pollClosed = setInterval(() => {
      if (popup.closed) {
        clearInterval(pollClosed)
        window.removeEventListener('message', handleMessage)
        setLoading(false)
      }
    }, 500)
  }

  return (
    <main className="min-h-screen bg-background grid grid-cols-1 lg:grid-cols-[1fr_1.618fr]">

      {/* Left panel */}
      <section className="flex flex-col justify-center items-center px-10 py-16 relative z-10 text-center">
        <div className="hidden lg:block absolute right-0 top-8 bottom-8 w-px bg-gradient-to-b from-transparent via-border to-transparent" />

        {/* Logo */}
        <div
          className="p-[2px] rounded-2xl mb-10 shadow-[0_8px_40px_rgba(59,130,246,0.20)]"
          style={{ background: 'linear-gradient(135deg, rgba(59,130,246,0.7) 0%, rgba(148,187,255,0.15) 50%, rgba(59,130,246,0.7) 100%)' }}
        >
          <div className="bg-sidebar rounded-2xl w-48 h-48 flex items-center justify-center overflow-hidden">
            <img src="/zeus-logo.png" alt="Zeus" className="w-full h-full object-contain scale-[1.5]" />
          </div>
        </div>

        {/* Subtitle */}
        <h1 className="text-lg font-semibold leading-snug text-foreground mb-10">
          Análise do setor<br />
          <span className="text-primary">elétrico</span> brasileiro.
        </h1>

        <button
          onClick={handleLogin}
          disabled={loading}
          className="
            inline-flex items-center gap-2.5
            bg-primary hover:bg-primary/90 disabled:opacity-60 disabled:cursor-wait
            text-primary-foreground font-semibold text-sm
            rounded-lg px-7 py-3.5
            transition-all duration-200
            focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring
          "
        >
          {loading ? 'Aguardando login...' : 'Entrar no sistema'}
          {!loading && <span aria-hidden className="text-lg">→</span>}
        </button>

        <span className="mt-10 text-[11px] text-muted-foreground/50 tracking-widest uppercase">
          Powered by NeoHorizon
        </span>
      </section>

      {/* Right panel — decorativo */}
      <section className="relative hidden lg:block overflow-hidden bg-sidebar">
        <style>{`
          @keyframes kenBurns {
            from { transform: scale(1); }
            to   { transform: scale(1.08); }
          }
          @keyframes dashTravel {
            from { stroke-dashoffset: 400; }
            to   { stroke-dashoffset: 0; }
          }
          @keyframes breathe {
            0%, 100% { opacity: 0.12; }
            50%       { opacity: 0.28; }
          }
          @keyframes dotGlow {
            0%, 100% { opacity: 0.4; r: 2; }
            50%       { opacity: 1;   r: 3.5; }
          }
          @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50%       { transform: translateY(-7px); }
          }
        `}</style>

        <img
          src={zeusWelcomeImage}
          alt=""
          className="absolute inset-0 w-full h-full object-cover opacity-30"
          style={{
            animation: 'kenBurns 16s ease-in-out infinite alternate',
            maskImage: 'radial-gradient(ellipse 85% 85% at 50% 50%, black 40%, transparent 100%)',
            WebkitMaskImage: 'radial-gradient(ellipse 85% 85% at 50% 50%, black 40%, transparent 100%)',
          }}
        />
        <GridOverlay />
        <BrazilMapDecor />
        <DataCards />
      </section>
    </main>
  )
}

function GridOverlay() {
  return (
    <div
      className="absolute inset-0"
      style={{
        backgroundImage: `
          linear-gradient(rgba(96,165,250,0.06) 1px, transparent 1px),
          linear-gradient(90deg, rgba(96,165,250,0.06) 1px, transparent 1px)
        `,
        backgroundSize: '32px 32px',
      }}
    />
  )
}

function BrazilMapDecor() {
  const dots = [
    { cx: 250, cy: 160, r: 3 },
    { cx: 230, cy: 220, r: 2 },
    { cx: 270, cy: 250, r: 2.5 },
    { cx: 290, cy: 130, r: 2 },
  ]

  return (
    <svg className="absolute inset-0 w-full h-full" viewBox="0 0 500 400">
      <ellipse
        cx="250" cy="200" rx="120" ry="160"
        fill="none" stroke="#60a5fa" strokeWidth="0.8"
        style={{ animation: 'breathe 4s ease-in-out infinite' }}
      />
      <path
        d="M200,60 Q260,80 280,120 Q300,160 270,200 Q240,240 260,280 Q280,320 240,360"
        fill="none" stroke="#60a5fa" strokeWidth="0.6"
        strokeDasharray="400" strokeDashoffset="400"
        opacity="0.3"
        style={{ animation: 'dashTravel 5s linear infinite' }}
      />
      {dots.map((c, i) => (
        <circle
          key={i} cx={c.cx} cy={c.cy} r={c.r} fill="#60a5fa"
          style={{ animation: `dotGlow 2.4s ease-in-out infinite ${i * 0.5}s` }}
        />
      ))}
    </svg>
  )
}

function DataCards() {
  const cardBase = 'bg-sidebar-accent border border-sidebar-border rounded-xl p-4'

  const floatStyle = (delay) => ({
    animation: `float 4s ease-in-out infinite ${delay}`,
  })

  return (
    <>
      <div
        className="absolute top-7 left-6 flex items-center gap-1.5 text-[10px] text-sidebar-foreground/60 font-mono tracking-wider border border-sidebar-border rounded-md px-2.5 py-1.5 bg-sidebar/80"
        style={floatStyle('0s')}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-sidebar-primary animate-pulse" />
        dados atualizados
      </div>

      <div className={`absolute top-7 right-6 ${cardBase}`} style={floatStyle('0.6s')}>
        <p className="text-[10px] text-sidebar-foreground/60 font-mono uppercase tracking-widest mb-1">DEC médio nacional</p>
        <p className="text-2xl font-bold font-mono text-sidebar-primary">14.2h</p>
        <p className="text-[11px] text-sidebar-foreground/40 mt-1">continuidade — 2024</p>
      </div>

      <div className={`absolute top-1/2 right-9 -translate-y-1/2 ${cardBase}`} style={floatStyle('1.2s')}>
        <p className="text-[10px] text-sidebar-foreground/60 font-mono uppercase tracking-widest mb-1">FEC médio nacional</p>
        <p className="text-2xl font-bold font-mono text-sidebar-primary">10.8×</p>
        <p className="text-[11px] text-sidebar-foreground/40 mt-1">interrupções/ano</p>
      </div>

      <div className={`absolute bottom-9 left-6 ${cardBase}`} style={floatStyle('1.8s')}>
        <p className="text-[10px] text-sidebar-foreground/60 font-mono uppercase tracking-widest mb-1">distribuidoras monitoradas</p>
        <p className="text-xl font-bold font-mono text-sidebar-foreground">63</p>
        <p className="text-[11px] text-sidebar-foreground/40 mt-1">BDGD · geoespacial</p>
      </div>
    </>
  )
}
