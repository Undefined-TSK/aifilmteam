import { Check, Clock, Minus } from 'lucide-react'
import { useStore } from '../../store/useStore.js'

function k13ThumbUrl(version) {
  if (!version.file_path) return null
  const idx = version.file_path.indexOf('k13_locked')
  if (idx === -1) return null
  const rel = version.file_path.slice(idx + 'k13_locked'.length).replaceAll('\\', '/')
  return '/k13-assets' + rel
}

const mockShots = [
  { num: 1, desc: '雨夜街道全景 · 远景', camera: '远景 · 静态', dur: '5秒', status: 'done', thumb: 'linear-gradient(135deg,#2a3530,#1a1818)' },
  { num: 2, desc: '雨夜少女中景 · 回头', camera: '中景 · 慢摇', dur: '4秒', status: 'done', thumb: 'linear-gradient(135deg,#2a303a,#1a1818)' },
  { num: 3, desc: '流浪猫特写 · 跑过', camera: '特写 · 固定', dur: '3秒', status: 'wip', thumb: 'linear-gradient(135deg,#302a3a,#1a1818)' },
  { num: 4, desc: '双人全景 · 对话', camera: '全景 · 固定', dur: '6秒', status: 'pending', thumb: '' },
  { num: 5, desc: '雨夜少女特写 · 微笑', camera: '特写 · 推镜', dur: '4秒', status: 'pending', thumb: '' },
  { num: 6, desc: '雨夜空镜 · 路灯雨丝', camera: '远景 · 固定', dur: '3秒', status: 'pending', thumb: '' },
  { num: 7, desc: '流浪猫跟拍 · 奔跑', camera: '跟随 · 手持', dur: '5秒', status: 'pending', thumb: '' },
  { num: 8, desc: '双人远景 · 远去', camera: '远景 · 固定', dur: '6秒', status: 'pending', thumb: '' },
]

export default function Storyboard() {
  const apiData = useStore((s) => s.apiData)
  const apiOnline = useStore((s) => s.apiOnline)

  const storyboardVersions = (apiData.versions?.versions || [])
    .filter((v) => v.asset_type === 'storyboard')
    .map((v) => ({ ...v, thumbUrl: k13ThumbUrl(v) }))

  const shots = mockShots.map((shot, i) => {
    if (apiOnline && storyboardVersions[i]) {
      return { ...shot, status: 'done', thumbUrl: storyboardVersions[i].thumbUrl, versionId: storyboardVersions[i].uuid }
    }
    return shot
  })

  const doneCount = shots.filter((s) => s.status === 'done').length

  return (
    <div className="alt-view">
      <div className="alt-view-header">
        <h2 className="alt-view-title">分镜板</h2>
        <span className="alt-view-sub">
          分镜序列 · {shots.length} 镜头 · {apiOnline ? `实时数据 · ${doneCount} 已完成` : '离线演示数据'}
        </span>
      </div>
      <div className="storyboard-grid">
        {shots.map((shot) => (
          <div className="sb-card" key={shot.num}>
            <div className="sb-thumb" style={{ background: shot.thumb || 'var(--bg)' }}>
              {shot.thumbUrl ? (
                <img
                  src={shot.thumbUrl}
                  alt={`第${shot.num}镜`}
                  loading="lazy"
                  onError={(e) => { e.currentTarget.style.display = 'none' }}
                />
              ) : (
                !shot.thumb && <Minus size={20} strokeWidth={2} color="var(--fg-mute)" />
              )}
              <span className={`sb-status-chip sb-chip-${shot.status}`}>
                {shot.status === 'done' && <Check size={11} strokeWidth={2.5} />}
                {shot.status === 'wip' && <Clock size={11} strokeWidth={2} />}
                {shot.status === 'pending' && <Minus size={11} strokeWidth={2.5} />}
                {shot.status === 'done' ? '已完成' : shot.status === 'wip' ? '生成中' : '待生成'}
              </span>
            </div>
            <div className="sb-info">
              <div className="sb-shot-num">
                第{shot.num}镜{shot.versionId && <span className="mono" style={{ opacity: 0.6 }}> · {shot.versionId}</span>}
              </div>
              <div className="sb-shot-title">{shot.desc}</div>
              <div className="sb-shot-meta">
                <span>{shot.camera}</span>
                <span>{shot.dur}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
