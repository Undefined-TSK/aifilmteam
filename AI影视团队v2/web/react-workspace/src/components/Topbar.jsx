import { useStore } from '../store/useStore.js'

const tabs = [
  { id: 'graph', label: '节点图' },
  { id: 'storyboard', label: '分镜板' },
  { id: 'versions', label: '版本树' },
  { id: 'budget', label: '预算' },
  { id: 'handoffs', label: '交接记录' },
]

export default function Topbar() {
  const activeView = useStore((s) => s.activeView)
  const switchView = useStore((s) => s.switchView)
  const apiOnline = useStore((s) => s.apiOnline)

  return (
    <div className="topbar">
      <div className="topbar-left">
        <div className="topbar-logo">
          <span className="topbar-logo-mark">C</span>
          CINEAST
        </div>
        <div className="topbar-breadcrumb">
          <span>项目</span>
          <span className="sep">/</span>
          <span className="current">雨夜寻猫</span>
        </div>
      </div>

      <div className="topbar-center">
        {tabs.map((t) => (
          <button
            key={t.id}
            className={`topbar-tab${activeView === t.id ? ' active' : ''}`}
            onClick={() => switchView(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="topbar-right">
        <span className={`api-badge ${apiOnline ? 'online' : 'offline'}`}>
          <span className="dot" />
          {apiOnline ? 'API已连接' : 'API离线'}
        </span>
        <button className="topbar-btn">导出</button>
        <button className="topbar-btn primary">预览生成</button>
      </div>
    </div>
  )
}
