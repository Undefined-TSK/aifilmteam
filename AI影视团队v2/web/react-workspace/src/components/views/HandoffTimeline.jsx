import { Check, X, Clock } from 'lucide-react'
import { useStore } from '../../store/useStore.js'

const mockHandoffs = [
  { id: 'handoff-001', from: '制片人', to: '角色设计师', status: 'completed', desc: '生成林小雨概念图 · V3已锁定', time: '2026-08-22 18:30 → 20:00' },
  { id: 'handoff-002', from: '制片人', to: '角色设计师', status: 'completed', desc: '生成小白猫概念图 · V1已锁定', time: '2026-08-22 19:00' },
  { id: 'handoff-003', from: '制片人', to: '场景设计师', status: 'completed', desc: '生成竹林晨雾场景 · V2已锁定', time: '2026-08-22 18:00 → 19:30' },
  { id: 'handoff-004', from: '制片人', to: '角色设计师', status: 'rejected', desc: '退回原因：角色描述过于模糊（"路人"），需补充外貌特征', time: '2026-08-22 21:00' },
  { id: 'handoff-005', from: '制片人', to: '分镜师', status: 'inprogress', desc: '第3镜生成中 · V2 进行中', time: '2026-08-22 20:30 → 进行中' },
]

export default function HandoffTimeline() {
  const apiData = useStore((s) => s.apiData)
  const apiHandoffs = apiData.handoffs?.handoffs

  const handoffs = apiHandoffs && apiHandoffs.length > 0
    ? apiHandoffs.map((h) => ({
        id: h.handoff_id || 'unknown',
        from: h.from_agent || '未知',
        to: h.to_agent || '未知',
        status: h.status === 'completed' ? 'completed' : h.status === 'rejected' ? 'rejected' : 'inprogress',
        desc: h.description || h.task || '',
        time: h.created_at || '',
      }))
    : mockHandoffs

  const completed = handoffs.filter((h) => h.status === 'completed').length
  const inprogress = handoffs.filter((h) => h.status === 'inprogress').length
  const rejected = handoffs.filter((h) => h.status === 'rejected').length

  return (
    <div className="alt-view">
      <div className="alt-view-header">
        <h2 className="alt-view-title">交接记录</h2>
        <span className="alt-view-sub">Agent 接力时间线 · 全程可追溯</span>
      </div>
      <div className="handoff-timeline">
        {handoffs.map((h, i) => (
          <div key={i} className={`ht-item ht-${h.status}`}>
            <div className={`ht-dot${h.status === 'rejected' ? ' ht-dot-red' : h.status === 'inprogress' ? ' ht-dot-blue' : ''}`} />
            <div className="ht-card">
              <div className="ht-card-header">
                <span className="ht-from">{h.from}</span>
                <span className="ht-arrow">→</span>
                <span className="ht-to">{h.to}</span>
                <span className={`ht-status${h.status === 'rejected' ? ' ht-status-rejected' : h.status === 'inprogress' ? ' ht-status-progress' : ''}`}>
                  {h.status === 'completed' && <Check size={12} strokeWidth={2.5} />}
                  {h.status === 'rejected' && <X size={12} strokeWidth={2.5} />}
                  {h.status === 'inprogress' && <Clock size={12} strokeWidth={2} />}
                  {h.status === 'completed' ? '已完成' : h.status === 'rejected' ? '已退回' : '进行中'}
                </span>
              </div>
              <div className="ht-card-body">
                <div className="ht-uuid mono">{h.id}</div>
                <div className="ht-desc">{h.desc}</div>
                <div className="ht-time">{h.time}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="ht-stats">
        <div className="ht-stat-card">
          <div className="ht-stat-val">{handoffs.length}</div>
          <div className="ht-stat-label">总交接数</div>
        </div>
        <div className="ht-stat-card">
          <div className="ht-stat-val" style={{ color: 'var(--accent-green)' }}>{completed}</div>
          <div className="ht-stat-label">已完成</div>
        </div>
        <div className="ht-stat-card">
          <div className="ht-stat-val" style={{ color: 'var(--accent-blue)' }}>{inprogress}</div>
          <div className="ht-stat-label">进行中</div>
        </div>
        <div className="ht-stat-card">
          <div className="ht-stat-val" style={{ color: 'var(--accent-rose)' }}>{rejected}</div>
          <div className="ht-stat-label">已退回</div>
        </div>
      </div>
    </div>
  )
}
