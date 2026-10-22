import { useStore } from '../store/useStore.js'
import { agentList } from '../data/nodes.js'

export default function LeftSidebar() {
  const selectedAgent = useStore((s) => s.selectedAgent)
  const selectAgent = useStore((s) => s.selectAgent)
  const apiData = useStore((s) => s.apiData)

  const budget = apiData.budget
  // /api/budget/status 返回 total_budget/spent/remaining，旧字段 limit 仅作兼容
  const spent = budget?.spent ?? 12.5
  const limit = budget?.total_budget ?? budget?.limit ?? 50
  const remaining = budget?.remaining ?? Math.max(limit - spent, 0)
  const pct = Math.min((spent / limit) * 100, 100)
  const fillClass = pct > 80 ? 'danger' : pct > 60 ? 'warn' : ''

  return (
    <div className="sidebar-left">
      <div className="sidebar-section">
        <div className="sidebar-header">
          AGENT 团队
          <span className="count">{agentList.length}</span>
        </div>
        <ul className="sidebar-list">
          {agentList.map((a) => (
            <li
              key={a.id}
              className={`sidebar-item${selectedAgent === a.id ? ' active' : ''}`}
              onClick={() => selectAgent(a.id)}
            >
              <span className={`dot dot-${a.status}`} />
              <span className="label">{a.name}</span>
              <span className="meta">{a.meta}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="budget-mini">
        <div className="sidebar-header" style={{ padding: '0 0 6px' }}>
          预算
          <span className="count">¥{spent}/{limit}</span>
        </div>
        <div className="budget-bar">
          <div
            className={`budget-fill${fillClass ? ' ' + fillClass : ''}`}
            style={{ width: pct + '%' }}
          />
        </div>
        <div className="budget-text">
          <span className="spent">已用 ¥{spent}</span>
          <span>剩余 ¥{remaining.toFixed(1)}</span>
        </div>
      </div>
    </div>
  )
}
