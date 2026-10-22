import { User, Cat, Image, Film, Lock } from 'lucide-react'
import { useStore } from '../../store/useStore.js'

const typeLabels = {
  character: '角色',
  scene: '场景',
  storyboard: '分镜',
  element: '元素',
}

const iconMap = { character: User, scene: Image, storyboard: Film, element: Image }

const mockAssets = [
  {
    name: '角色 · 林小雨',
    type: 'character',
    versions: [
      { num: 'V1', state: 'vt-abandoned', status: '已废弃', meta: 'seed:9847 · 20步 · 1024×1024', time: '2026-08-22 18:30' },
      { num: 'V2', state: 'vt-archived', status: '已归档', meta: 'seed:28391 · 25步 · 1024×1024', time: '2026-08-22 19:15' },
      { num: 'V3', state: 'vt-locked', status: '已锁定', meta: 'seed:51200 · 30步 · 1024×1024', time: '2026-08-22 20:00' },
    ],
  },
  {
    name: '场景 · 竹林晨雾',
    type: 'scene',
    versions: [
      { num: 'V1', state: 'vt-archived', status: '已归档', meta: 'seed:7100 · 22步 · 1024×1024', time: '2026-08-22 18:00' },
      { num: 'V2', state: 'vt-locked', status: '已锁定', meta: 'seed:33445 · 28步 · 1024×1024', time: '2026-08-22 19:30' },
    ],
  },
]

function k13ThumbUrl(version) {
  if (!version.file_path) return null
  const idx = version.file_path.indexOf('k13_locked')
  if (idx === -1) return null
  const rel = version.file_path.slice(idx + 'k13_locked'.length).replaceAll('\\', '/')
  return '/k13-assets' + rel
}

export default function VersionTree() {
  const apiData = useStore((s) => s.apiData)
  const apiOnline = useStore((s) => s.apiOnline)
  const versions = apiData.versions?.versions

  let assets = mockAssets
  if (apiOnline && versions && versions.length > 0) {
    const groups = {}
    for (const v of versions) {
      const key = `${v.asset_type}/${v.asset_name}`
      if (!groups[key]) {
        groups[key] = {
          name: `${typeLabels[v.asset_type] || v.asset_type} · ${v.asset_name}`,
          type: v.asset_type,
          versions: [],
        }
      }
      const params = v.params || {}
      // 锁定时 params_json 结构为 {prompt, seed, params:{steps,cfg,...}, cost}
      const inner = params.params || {}
      const steps = inner.steps ?? params.steps
      const cfg = inner.cfg ?? params.cfg
      groups[key].versions.push({
        num: v.uuid,
        state: 'vt-locked',
        status: '已锁定',
        meta: `seed:${params.seed ?? '—'} · ${steps ?? '—'}步${cfg ? ` · cfg:${cfg}` : ''}`,
        time: v.locked_at,
        branch: v.branch,
        thumbUrl: k13ThumbUrl(v),
      })
    }
    assets = Object.values(groups)
  }

  const totalVersions = assets.reduce((acc, a) => acc + a.versions.length, 0)

  return (
    <div className="alt-view">
      <div className="alt-view-header">
        <h2 className="alt-view-title">版本树</h2>
        <span className="alt-view-sub">
          K13 版本管理系统 · {apiOnline ? `实时数据 · ${assets.length} 资产 · ${totalVersions} 锁定版本` : '离线演示数据'}
        </span>
      </div>
      <div className="version-tree-container">
        {assets.map((asset, ai) => {
          const Icon = iconMap[asset.type] || Image
          return (
            <div className="vt-asset-group" key={ai}>
              <div className="vt-asset-header">
                <span className="vt-asset-icon">
                  <Icon size={16} strokeWidth={2} />
                </span>
                <span className="vt-asset-name">{asset.name}</span>
                <span className="dot dot-green" title="已有锁定版本" />
              </div>
              <div className="vt-versions">
                {asset.versions.map((v, vi) => (
                  <div key={vi} style={{ display: 'flex', alignItems: 'center' }}>
                    <div className={`vt-version ${v.state}`}>
                      <div className="vt-v-num">{v.num}</div>
                      <div className="vt-v-info">
                        <div className="vt-v-status">
                          {v.state === 'vt-locked' && <Lock size={12} strokeWidth={2} style={{ color: 'var(--accent-gold)' }} />}
                          {v.status}
                          {v.branch && v.branch !== 'main' && (
                            <span className="mono" style={{ fontSize: '0.6rem', opacity: 0.6 }}> @{v.branch}</span>
                          )}
                        </div>
                        <div className="vt-v-meta mono">{v.meta}</div>
                        <div className="vt-v-time">{v.time}</div>
                      </div>
                      {v.thumbUrl ? (
                        <img
                          className="vt-v-thumb"
                          src={v.thumbUrl}
                          alt={v.num}
                          loading="lazy"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none'
                            e.currentTarget.nextElementSibling.style.display = 'flex'
                          }}
                        />
                      ) : null}
                      <div
                        className="vt-v-thumb"
                        style={{
                          background: 'linear-gradient(135deg,#3a3520,#1a1810)',
                          display: v.thumbUrl ? 'none' : 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                        title="资产待生成"
                      >
                        {!v.thumbUrl && <span className="mono" style={{ fontSize: '0.55rem', color: 'var(--fg-mute)' }}>PNG</span>}
                      </div>
                    </div>
                    {vi < asset.versions.length - 1 && <div className="vt-branch-line" />}
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
