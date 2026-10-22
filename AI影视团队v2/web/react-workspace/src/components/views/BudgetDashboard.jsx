import { useStore } from '../../store/useStore.js'

export default function BudgetDashboard() {
  const apiData = useStore((s) => s.apiData)
  const budget = apiData.budget

  // /api/budget/status 返回 total_budget/spent/remaining，旧字段 limit 仅作兼容
  const spent = budget?.spent ?? 34
  const limit = budget?.total_budget ?? budget?.limit ?? 50
  const pct = (spent / limit) * 100
  const offset = 440 - (440 * pct / 100)
  const remaining = budget?.remaining ?? Math.max(limit - spent, 0)
  const statusColor = pct > 80 ? 'var(--accent-red)' : pct > 50 ? 'var(--accent-gold)' : 'var(--accent-green)'
  const statusText = pct > 80 ? '熔断状态' : pct > 50 ? '预警状态' : '正常状态'

  const categories = budget?.categories || [
    { label: '角色概念图', spent: 15, limit: 20, color: 'var(--accent-teal)' },
    { label: '场景概念图', spent: 11, limit: 20, color: 'var(--accent-blue)' },
    { label: '分镜生成', spent: 3, limit: 10, color: 'var(--accent-purple)' },
    { label: '动画渲染', spent: 0, limit: 10, color: 'var(--accent-rose)' },
  ]

  return (
    <div className="alt-view">
      <div className="alt-view-header">
        <h2 className="alt-view-title">预算仪表盘</h2>
        <span className="alt-view-sub">预算管理 · 预警与熔断</span>
      </div>
      <div className="budget-dashboard">
        <div className="bd-hero">
          <div className="bd-hero-ring">
            <svg width="160" height="160" viewBox="0 0 160 160">
              <circle cx="80" cy="80" r="70" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="12" />
              <circle
                cx="80" cy="80" r="70" fill="none"
                stroke={statusColor}
                strokeWidth="12"
                strokeDasharray="440"
                strokeDashoffset={offset}
                strokeLinecap="round"
                transform="rotate(-90 80 80)"
              />
              <text x="80" y="75" textAnchor="middle" fill="var(--fg)" fontSize="28" fontWeight="700" fontFamily="Inter,sans-serif">{spent}</text>
              <text x="80" y="100" textAnchor="middle" fill="var(--fg-mute)" fontSize="13" fontFamily="Inter,sans-serif">/ {limit} 点</text>
            </svg>
          </div>
          <div className="bd-hero-info">
            <div className="bd-hero-status" style={{ color: statusColor }}>{statusText}</div>
            <div className="bd-hero-desc">已使用 {Math.round(pct)}% 预算，超过 80% 将触发熔断</div>
            <div className="bd-hero-stats">
              <div className="bd-stat">
                <div className="bd-stat-val">{remaining}</div>
                <div className="bd-stat-label">剩余点数</div>
              </div>
              <div className="bd-stat">
                <div className="bd-stat-val">{Math.floor(remaining / (spent / 7 || 1))}</div>
                <div className="bd-stat-label">可生成次数</div>
              </div>
              <div className="bd-stat">
                <div className="bd-stat-val">{(spent / 7).toFixed(1)}</div>
                <div className="bd-stat-label">单均消耗</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bd-section">
          <div className="bd-section-title">分类消耗</div>
          {categories.map((cat, i) => (
            <div className="bd-cat-row" key={i}>
              <span className="bd-cat-label">{cat.label}</span>
              <div className="bd-cat-bar">
                <div
                  className="bd-cat-fill"
                  style={{
                    width: `${(cat.spent / cat.limit) * 100}%`,
                    background: cat.color,
                  }}
                />
              </div>
              <span className="bd-cat-val mono">{cat.spent} / {cat.limit}</span>
            </div>
          ))}
        </div>

        <div className="bd-section">
          <div className="bd-section-title">熔断规则</div>
          <div className="bd-rule">
            <span className="dot dot-green" style={{ width: 6, height: 6 }} />
            <span>使用率 &lt; 50%：正常工作</span>
          </div>
          <div className="bd-rule">
            <span style={{ width: 6, height: 6, borderRadius: '50%', display: 'inline-block', background: 'var(--accent-gold)' }} />
            <span>使用率 50%-80%：预警提示</span>
          </div>
          <div className="bd-rule">
            <span className="dot dot-red" style={{ width: 6, height: 6 }} />
            <span>使用率 &gt; 80%：自动熔断，停止生成</span>
          </div>
        </div>
      </div>
    </div>
  )
}
