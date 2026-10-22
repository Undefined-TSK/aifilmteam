import { useEffect, useRef } from 'react'
import { Lock, Trash2, Plus, Copy, Eye, RotateCcw } from 'lucide-react'
import { useStore } from '../store/useStore.js'

export default function ContextMenu({ menu, onClose }) {
  const ref = useRef(null)
  const nodes = useStore((s) => s.nodes)
  const deleteSelected = useStore((s) => s.deleteSelected)
  const addNode = useStore((s) => s.addNode)
  const toggleVersionLock = useStore((s) => s.toggleVersionLock)
  const switchView = useStore((s) => s.switchView)
  const resetGraph = useStore((s) => s.resetGraph)

  useEffect(() => {
    const close = (e) => {
      if (ref.current && !ref.current.contains(e.target)) onClose()
    }
    document.addEventListener('mousedown', close)
    document.addEventListener('scroll', onClose, true)
    return () => {
      document.removeEventListener('mousedown', close)
      document.removeEventListener('scroll', onClose, true)
    }
  }, [onClose])

  if (!menu) return null

  const node = menu.kind === 'node' ? nodes.find((n) => n.id === menu.nodeId) : null
  const lastVersionIdx = node ? node.data.versions.length - 1 : -1
  const lastVersionLocked = node?.data.versions[lastVersionIdx]?.locked

  const style = {
    left: Math.min(menu.x, window.innerWidth - 180),
    top: Math.min(menu.y, window.innerHeight - 220),
  }

  const run = (fn) => () => {
    fn()
    onClose()
  }

  return (
    <div className="context-menu" ref={ref} style={style}>
      {menu.kind === 'node' && (
        <>
          <div className="context-menu-title">{node?.data.title}</div>
          {lastVersionIdx >= 0 && (
            <button className="context-menu-item" onClick={run(() => toggleVersionLock(menu.nodeId, lastVersionIdx))}>
              <Lock size={13} strokeWidth={2} />
              {lastVersionLocked ? '解锁最新版本' : '锁定最新版本'}
            </button>
          )}
          <button className="context-menu-item" onClick={run(() => switchView('versions'))}>
            <Eye size={13} strokeWidth={2} />
            查看版本树
          </button>
          <div className="context-menu-sep" />
          <button className="context-menu-item danger" onClick={run(deleteSelected)}>
            <Trash2 size={13} strokeWidth={2} />
            删除节点
          </button>
        </>
      )}

      {menu.kind === 'pane' && (
        <>
          <div className="context-menu-title">添加节点</div>
          <button className="context-menu-item" onClick={run(() => addNode('element', menu.flowPos))}>
            <Plus size={13} strokeWidth={2} />
            元素节点（角色/场景）
          </button>
          <button className="context-menu-item" onClick={run(() => addNode('task', menu.flowPos))}>
            <Plus size={13} strokeWidth={2} />
            任务节点
          </button>
          <button className="context-menu-item" onClick={run(() => addNode('review', menu.flowPos))}>
            <Plus size={13} strokeWidth={2} />
            审查节点
          </button>
          <button className="context-menu-item" onClick={run(() => addNode('decision', menu.flowPos))}>
            <Plus size={13} strokeWidth={2} />
            决策节点
          </button>
          <div className="context-menu-sep" />
          <button className="context-menu-item danger" onClick={run(resetGraph)}>
            <RotateCcw size={13} strokeWidth={2} />
            恢复初始布局
          </button>
          <div className="context-menu-hint">双击空白处 = 快速添加任务</div>
        </>
      )}
    </div>
  )
}
