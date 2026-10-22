import { useCallback, useState } from 'react'
import {
  ReactFlow,
  Background,
  BackgroundVariant,
  useReactFlow,
} from '@xyflow/react'
import { useStore } from '../store/useStore.js'
import CineastNode from './CineastNode.jsx'
import ContextMenu from './ContextMenu.jsx'

const nodeTypes = { cineast: CineastNode }

function ZoomControls() {
  const { zoomIn, zoomOut, zoomTo, getZoom } = useReactFlow()
  const [zoomLevel, setZoomLevel] = useState(Math.round(getZoom() * 100))

  const updateLevel = (fn) => {
    fn({ duration: 200 })
    setTimeout(() => setZoomLevel(Math.round(getZoom() * 100)), 250)
  }

  return (
    <div className="canvas-overlay zoom-controls" style={{ position: 'absolute' }}>
      <button className="zoom-btn" onClick={() => updateLevel(zoomIn)}>+</button>
      <div className="zoom-level">{zoomLevel}%</div>
      <button className="zoom-btn" onClick={() => updateLevel(zoomOut)}>-</button>
      <button className="zoom-btn" onClick={() => { zoomTo(1, { duration: 200 }); setTimeout(() => setZoomLevel(100), 250) }} title="重置缩放">⟲</button>
    </div>
  )
}

export default function NodeGraph() {
  const nodes = useStore((s) => s.nodes)
  const edges = useStore((s) => s.edges)
  const selectNode = useStore((s) => s.selectNode)
  const connectEdge = useStore((s) => s.connectEdge)
  const addNode = useStore((s) => s.addNode)
  const handleNodesChange = useStore((s) => s.handleNodesChange)
  const handleEdgesChange = useStore((s) => s.handleEdgesChange)
  const openContextMenu = useStore((s) => s.openContextMenu)
  const closeContextMenu = useStore((s) => s.closeContextMenu)
  const contextMenu = useStore((s) => s.contextMenu)
  const { screenToFlowPosition } = useReactFlow()

  const onNodesChange = useCallback((changes) => {
    handleNodesChange(changes)
  }, [handleNodesChange])

  const onEdgesChange = useCallback((changes) => {
    handleEdgesChange(changes)
  }, [handleEdgesChange])

  const onConnect = useCallback((params) => {
    connectEdge(params)
  }, [connectEdge])

  const onNodeClick = useCallback((_, node) => {
    selectNode(node.id)
  }, [selectNode])

  const onNodeContextMenu = useCallback((event, node) => {
    event.preventDefault()
    selectNode(node.id)
    openContextMenu({
      kind: 'node',
      nodeId: node.id,
      x: event.clientX,
      y: event.clientY,
    })
  }, [selectNode, openContextMenu])

  const onPaneContextMenu = useCallback((event) => {
    event.preventDefault()
    const pos = screenToFlowPosition({ x: event.clientX, y: event.clientY })
    openContextMenu({
      kind: 'pane',
      flowPos: pos,
      x: event.clientX,
      y: event.clientY,
    })
  }, [openContextMenu, screenToFlowPosition])

  const onDoubleClick = useCallback((event) => {
    if (event.target.closest('.react-flow__node')) return
    const pos = screenToFlowPosition({ x: event.clientX, y: event.clientY })
    addNode('task', pos)
  }, [addNode, screenToFlowPosition])

  return (
    <>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onNodeContextMenu={onNodeContextMenu}
        onPaneContextMenu={onPaneContextMenu}
        onDoubleClick={onDoubleClick}
        deleteKeyCode={['Delete']}
        zoomOnDoubleClick={false}
        fitView
        fitViewOptions={{ padding: 0.15 }}
        minZoom={0.3}
        maxZoom={2.5}
        proOptions={{ hideAttribution: true }}
        connectionLineStyle={{ stroke: 'var(--accent-gold)', strokeWidth: 2 }}
        connectionLineType="default"
        defaultEdgeOptions={{ type: 'default' }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={24}
          size={1}
          color="rgba(255,255,255,0.03)"
        />
        <div className="canvas-overlay canvas-status">
          <div className="status-badge">
            <span className="dot dot-green" />
            {nodes.filter((n) => n.data.status === 'green').length} 已通过
          </div>
          <div className="status-badge">
            <span className="dot dot-blue" />
            {nodes.filter((n) => n.data.status === 'yellow').length} 进行中
          </div>
          <div className="status-badge">
            <span className="dot dot-gray" />
            {nodes.filter((n) => n.data.status === 'gray').length} 未开始
          </div>
          <div className="status-badge" title="拖拽节点端口可创建连线；双击空白添加节点；右键打开菜单">
            <span className="dot dot-yellow" />
            {nodes.length} 节点 · {edges.length} 连线
          </div>
        </div>
        <ZoomControls />
      </ReactFlow>

      {contextMenu && (
        <ContextMenu
          menu={contextMenu}
          onClose={closeContextMenu}
        />
      )}
    </>
  )
}
