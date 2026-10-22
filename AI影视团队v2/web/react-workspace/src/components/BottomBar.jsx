import { useState } from 'react'
import { Send, Circle } from 'lucide-react'
import { useStore } from '../store/useStore.js'

export default function BottomBar() {
  const apiOnline = useStore((s) => s.apiOnline)
  const graphSync = useStore((s) => s.graphSync)
  const chatText = useStore((s) => s.chatText)
  const setChatText = useStore((s) => s.setChatText)
  const sendInstruction = useStore((s) => s.sendInstruction)
  const [status, setStatus] = useState('normal')

  const handleSend = () => {
    if (!chatText.trim()) return
    setStatus('processing')
    sendInstruction()
    setTimeout(() => setStatus('normal'), 3000)
  }

  const graphLabel = {
    idle: null,
    dirty: '画布待保存…',
    saving: '画布保存中…',
    saved: graphSync.savedAt ? `画布已保存 ${graphSync.savedAt.slice(11)}` : '画布已保存',
    offline: '画布未同步（离线）',
    error: '画布保存失败',
  }[graphSync.status]

  const graphDot = {
    dirty: 'yellow',
    saving: 'blue',
    saved: 'green',
    offline: 'gray',
    error: 'red',
  }[graphSync.status]

  return (
    <div className="bottombar">
      <div className="bottombar-prompt" style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--bg)', border: '1px solid var(--line)', borderRadius: 'var(--radius)', padding: '4px 8px 4px 12px' }}>
        <input
          className="bottombar-input"
          type="text"
          placeholder="输入指令…（如：生成林小雨 V4，尝试赛博朋克风格）"
          value={chatText}
          onChange={(e) => setChatText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button className="bottombar-send" onClick={handleSend}>
          <Send size={14} strokeWidth={2} />
          发送
        </button>
      </div>
      <div className="bottombar-status">
        {status === 'processing' ? (
          <>
            <span className="dot dot-blue" />
            <span>正在处理指令…</span>
          </>
        ) : (
          <>
            <span className={`dot dot-${apiOnline ? 'green' : 'gray'}`} />
            <span>{apiOnline ? '系统正常' : '离线模式'}</span>
            <span style={{ opacity: 0.5 }}>·</span>
            <span>{apiOnline ? 'ComfyUI 已连接' : 'API 未连接'}</span>
            {graphLabel && (
              <>
                <span style={{ opacity: 0.5 }}>·</span>
                <span className={`dot dot-${graphDot}`} />
                <span>{graphLabel}</span>
              </>
            )}
          </>
        )}
      </div>
    </div>
  )
}
