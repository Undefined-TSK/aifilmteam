import { Handle, Position } from '@xyflow/react'
import { User, Image, Edit, Shield, Flag, Film } from 'lucide-react'
import { useStore } from '../store/useStore.js'
import { statusColors } from '../data/nodes.js'

const iconMap = {
  user: User,
  image: Image,
  edit: Edit,
  shield: Shield,
  flag: Flag,
  film: Film,
}

export default function CineastNode({ id, data, selected }) {
  const Icon = iconMap[data.icon] || User
  const selectNode = useStore((s) => s.selectNode)
  const statusColor = statusColors[data.status] || 'var(--fg-mute)'

  return (
    <div
      className={`cineast-node${selected ? ' selected' : ''}`}
      data-type={data.nodeType}
      onClick={(e) => {
        e.stopPropagation()
        selectNode(id)
      }}
    >
      <Handle type="target" position={Position.Left} />

      <div className="node-head">
        <div className="node-title">
          <span className="node-icon">
            <Icon size={16} strokeWidth={2} />
          </span>
          {data.title}
        </div>
        <span className="node-status-dot" style={{ background: statusColor }} />
      </div>

      <div className="node-body">
        {data.params.map((p, i) => (
          <div className="node-param" key={i}>
            <span className="key">{p.k}</span>
            <span className="val">{p.v}</span>
          </div>
        ))}
      </div>

      {data.preview?.web_path && (
        <div className="node-preview">
          <img src={data.preview.web_path} alt="preview" className="node-preview-img" />
          <span className="node-preview-badge">{data.preview.version}</span>
        </div>
      )}

      {data.versions.length > 0 && (
        <div className="node-foot">
          <div className="node-versions">
            {data.versions.map((v, i) => (
              <span
                key={i}
                className={`node-ver${v.locked ? ' locked' : ''}`}
              >
                {v.ver}
              </span>
            ))}
          </div>
          {data.tag && <span className="node-tag">{data.tag}</span>}
        </div>
      )}

      <Handle type="source" position={Position.Right} />
    </div>
  )
}
