import { useState, useEffect } from 'react'
import { Pencil, Lock, Unlock, Sparkles, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react'
import { useStore } from '../store/useStore.js'
import { statusColors } from '../data/nodes.js'

const assetTypeLabels = { character: '角色', scene: '场景', storyboard: '分镜' }

export default function RightSidebar() {
  const nodes = useStore((s) => s.nodes)
  const selectedNodeId = useStore((s) => s.selectedNodeId)
  const updateNodeParam = useStore((s) => s.updateNodeParam)
  const renameNode = useStore((s) => s.renameNode)
  const toggleVersionLock = useStore((s) => s.toggleVersionLock)
  const generate = useStore((s) => s.generate)
  const lockVersion = useStore((s) => s.lockVersion)
  const genState = useStore((s) => s.genState)
  const genError = useStore((s) => s.genError)
  const lockState = useStore((s) => s.lockState)
  const lockError = useStore((s) => s.lockError)
  const apiData = useStore((s) => s.apiData)

  const node = nodes.find((n) => n.id === selectedNodeId)
  const [editingTitle, setEditingTitle] = useState(false)
  const [titleDraft, setTitleDraft] = useState('')

  // 生成表单草稿
  const [promptDraft, setPromptDraft] = useState('')
  const [seedDraft, setSeedDraft] = useState('')
  const [stepsDraft, setStepsDraft] = useState('25')

  // 切换选中节点时，重置生成表单
  useEffect(() => {
    if (node) {
      setPromptDraft(node.data.prompt || '')
      setSeedDraft('')
      setStepsDraft('25')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedNodeId])

  const handoffs = apiData.handoffs?.handoffs?.slice(0, 4) || []

  const startTitleEdit = () => {
    setTitleDraft(node?.data.title || '')
    setEditingTitle(true)
  }

  const commitTitle = () => {
    if (titleDraft.trim() && node) {
      renameNode(node.id, titleDraft.trim())
    }
    setEditingTitle(false)
  }

  const isGenNode = node && node.data.assetType
  const preview = node?.data.preview
  const alreadyLocked = preview && node.data.versions.some((v) => v.ver === preview.version && v.locked)

  return (
    <div className="sidebar-right">
      <div className="sidebar-section">
        <div className="sidebar-header">节点详情</div>
        {node ? (
          <div className="detail-section">
            {editingTitle ? (
              <input
                className="title-edit-input"
                value={titleDraft}
                autoFocus
                onChange={(e) => setTitleDraft(e.target.value)}
                onBlur={commitTitle}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') commitTitle()
                  if (e.key === 'Escape') setEditingTitle(false)
                }}
              />
            ) : (
              <div className="detail-title-row">
                <div className="detail-title">{node.data.title}</div>
                <button className="icon-btn" onClick={startTitleEdit} title="重命名">
                  <Pencil size={12} strokeWidth={2} />
                </button>
              </div>
            )}
            <div className="detail-row">
              <span className="key">类型</span>
              <span className="val">{node.data.nodeType}</span>
            </div>
            <div className="detail-row">
              <span className="key">状态</span>
              <span className="val" style={{ color: statusColors[node.data.status] }}>
                {node.data.status === 'green' ? '已完成' :
                 node.data.status === 'yellow' ? '审查中' :
                 node.data.status === 'red' ? '已退回' :
                 node.data.status === 'blue' ? '进行中' : '未开始'}
              </span>
            </div>

            {node.data.params.map((p, i) => (
              <div className="detail-row" key={i}>
                <span className="key">{p.k}</span>
                <input
                  className="param-edit-input"
                  value={p.v}
                  onChange={(e) => updateNodeParam(node.id, i, e.target.value)}
                />
              </div>
            ))}

            {node.data.versions.length > 0 && (
              <div className="detail-tag-list">
                {node.data.versions.map((v, i) => (
                  <span
                    key={i}
                    className={`detail-tag${v.locked ? ' locked' : ''}`}
                    style={{ cursor: 'pointer' }}
                    onClick={() => toggleVersionLock(node.id, i)}
                    title={v.locked ? '点击解锁' : '点击锁定'}
                  >
                    {v.ver}
                    {v.locked && <Lock size={10} strokeWidth={2.5} style={{ display: 'inline', marginLeft: 3, verticalAlign: '-1px' }} />}
                    {!v.locked && <Unlock size={10} strokeWidth={2.5} style={{ display: 'inline', marginLeft: 3, verticalAlign: '-1px', opacity: 0.5 }} />}
                  </span>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="empty-state">
            <span className="text">未选中节点</span>
          </div>
        )}
      </div>

      {isGenNode && (
        <div className="sidebar-section">
          <div className="sidebar-header">
            <Sparkles size={13} strokeWidth={2.2} style={{ verticalAlign: '-2px', marginRight: 5 }} />
            AI 渲染 · {assetTypeLabels[node.data.assetType] || node.data.assetType}
          </div>
          <div className="detail-section gen-panel">
            <textarea
              className="gen-prompt"
              value={promptDraft}
              placeholder="输入英文提示词（SDXL 对英文更敏感）"
              rows={3}
              onChange={(e) => setPromptDraft(e.target.value)}
            />
            <div className="gen-row">
              <label className="gen-label">种子</label>
              <input
                className="gen-input"
                value={seedDraft}
                placeholder="随机"
                onChange={(e) => setSeedDraft(e.target.value)}
              />
              <label className="gen-label">步数</label>
              <input
                className="gen-input gen-input-sm"
                value={stepsDraft}
                onChange={(e) => setStepsDraft(e.target.value)}
              />
            </div>
            <button
              className="gen-btn"
              disabled={genState === 'rendering' || !promptDraft.trim()}
              onClick={() =>
                generate(node.id, {
                  prompt: promptDraft,
                  seed: seedDraft,
                  steps: stepsDraft,
                })
              }
            >
              {genState === 'rendering' ? (
                <>
                  <Loader2 size={13} className="spin" /> 渲染中…
                </>
              ) : (
                <>
                  <Sparkles size={13} /> 渲染 (ComfyUI)
                </>
              )}
            </button>

            {genState === 'error' && (
              <div className="gen-msg gen-err">
                <AlertCircle size={12} /> {genError}
              </div>
            )}

            {preview && (
              <div className={`gen-preview${genState === 'rendering' ? ' rendering' : ''}`}>
                <img src={preview.web_path} alt="preview" className="gen-preview-img" />
                {genState === 'rendering' && (
                  <div className="gen-preview-overlay">新版本渲染中，当前为上一版预览</div>
                )}
                <div className="gen-preview-meta">
                  <span>版本 {preview.version}</span>
                  <span>种子 {preview.seed}</span>
                  <span>耗时 ¥{preview.cost}</span>
                </div>
                <button
                  className="gen-btn gen-lock-btn"
                  disabled={genState === 'rendering' || lockState === 'locking' || alreadyLocked}
                  onClick={() => lockVersion(node.id)}
                >
                  {lockState === 'locking' ? (
                    <>
                      <Loader2 size={13} className="spin" /> 锁定中…
                    </>
                  ) : alreadyLocked ? (
                    <>
                      <CheckCircle2 size={13} /> 已锁定
                    </>
                  ) : (
                    <>
                      <Lock size={13} /> 锁定此版本
                    </>
                  )}
                </button>
                {lockState === 'error' && (
                  <div className="gen-msg gen-err">
                    <AlertCircle size={12} /> {lockError}
                  </div>
                )}
                {lockState === 'done' && (
                  <div className="gen-msg gen-ok">
                    <CheckCircle2 size={12} /> 已冻结进 K13 版本树
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      <div className="sidebar-section">
        <div className="sidebar-header">最近交接</div>
        <div className="detail-section">
          {handoffs.length > 0 ? (
            handoffs.map((h, i) => (
              <div className="timeline-entry" key={i}>
                <span className="time">{(h.created_at || '').slice(5, 16)}</span>
                <span className="msg">
                  <span className="agent">{h.from_agent}</span>
                  {' → '}
                  {h.to_agent}
                </span>
              </div>
            ))
          ) : (
            <>
              <div className="timeline-entry">
                <span className="time">20:00</span>
                <span className="msg">
                  <span className="agent">制片人</span> 创建交接任务
                </span>
              </div>
              <div className="timeline-entry">
                <span className="time">20:15</span>
                <span className="msg">
                  <span className="agent">角色设计师</span> 完成林小雨 V3
                </span>
              </div>
              <div className="timeline-entry">
                <span className="time">20:30</span>
                <span className="msg">
                  <span className="agent">场景设计师</span> 完成雨夜巷 V2
                </span>
              </div>
              <div className="timeline-entry">
                <span className="time">21:00</span>
                <span className="msg">
                  <span className="agent">制片人</span> 退回路人角色设计
                </span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
