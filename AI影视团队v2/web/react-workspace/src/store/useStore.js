import { create } from 'zustand'
import { applyNodeChanges, applyEdgeChanges } from '@xyflow/react'
import { fetchAPI, checkAPIHealth, postAPI, deleteAPI } from '../api/client.js'
import { initialNodes, initialEdges } from '../data/nodes.js'

let nextId = 100
let saveTimer = null

const SAVE_DEBOUNCE_MS = 800

function cleanNodes(nodes) {
  return nodes.map((n) => {
    const { selected, dragging, measured, ...rest } = n
    return rest
  })
}

function cleanEdges(edges) {
  return edges.map((e) => {
    const { selected, ...rest } = e
    return rest
  })
}

export const useStore = create((set, get) => ({
  // ===== Node Graph =====
  nodes: initialNodes,
  edges: initialEdges,
  selectedNodeId: 'elem-linxy',

  connectEdge: (params) => {
    const { edges } = get()
    if (edges.some((e) => e.source === params.source && e.target === params.target)) return
    const id = `e-${params.source}-${params.target}`
    set({ edges: [...edges, { id, ...params, type: 'default', className: 'edge-solid' }] })
    get().scheduleSave()
  },

  deleteSelected: () => {
    const { nodes, edges, selectedNodeId } = get()
    const selectedEdges = edges.filter((e) => e.selected)
    const selectedNodes = nodes.filter((n) => n.selected || n.id === selectedNodeId)
    const removedIds = new Set(selectedNodes.map((n) => n.id))
    set({
      nodes: nodes.filter((n) => !removedIds.has(n.id)),
      edges: edges.filter(
        (e) => !selectedEdges.includes(e) && !removedIds.has(e.source) && !removedIds.has(e.target)
      ),
      selectedNodeId: removedIds.has(selectedNodeId) ? null : selectedNodeId,
    })
    get().scheduleSave()
  },

  selectNode: (id) => {
    set((state) => ({
      selectedNodeId: id,
      // 切换节点时清空生成/锁定状态，避免 A 节点的成功消息残留在 B 节点面板
      genState: 'idle',
      genError: null,
      lockState: 'idle',
      lockError: null,
      nodes: state.nodes.map((n) => ({ ...n, selected: n.id === id })),
    }))
  },

  updateNodeParam: (nodeId, paramIndex, newValue) => {
    set((state) => ({
      nodes: state.nodes.map((n) => {
        if (n.id !== nodeId) return n
        const params = n.data.params.map((p, i) =>
          i === paramIndex ? { ...p, v: newValue } : p
        )
        return { ...n, data: { ...n.data, params } }
      }),
    }))
    get().scheduleSave()
  },

  addNode: (nodeType, position) => {
    const presets = {
      task: { title: '新任务', icon: 'edit', params: [{ k: 'Agent', v: '待分配' }, { k: '交付', v: '—' }] },
      element: { title: '新元素', icon: 'image', params: [{ k: '描述', v: '—' }] },
      review: { title: '新审查', icon: 'shield', params: [{ k: '类型', v: '自动审查' }] },
      decision: { title: '新决策', icon: 'flag', params: [{ k: '类型', v: '确认' }] },
    }
    const preset = presets[nodeType] || presets.task
    // 时间戳前缀避免与已加载画布中的历史ID冲突（nextId每次页面加载会重置）
    const id = `node-${Date.now().toString(36)}-${nextId++}`
    const node = {
      id,
      type: 'cineast',
      position,
      data: {
        nodeType,
        title: preset.title,
        icon: preset.icon,
        status: 'gray',
        params: preset.params,
        versions: [],
        tag: '',
      },
    }
    set((state) => ({ nodes: [...state.nodes, node], selectedNodeId: id }))
    get().scheduleSave()
    return id
  },

  renameNode: (nodeId, title) => {
    set((state) => ({
      nodes: state.nodes.map((n) =>
        n.id === nodeId ? { ...n, data: { ...n.data, title } } : n
      ),
    }))
    get().scheduleSave()
  },

  toggleVersionLock: (nodeId, versionIndex) => {
    set((state) => ({
      nodes: state.nodes.map((n) => {
        if (n.id !== nodeId) return n
        const versions = n.data.versions.map((v, i) =>
          i === versionIndex ? { ...v, locked: !v.locked } : v
        )
        return { ...n, data: { ...n.data, versions } }
      }),
    }))
    get().scheduleSave()
  },

  // ===== AI 渲染：调用 ComfyUI 生成并联动预算 =====
  generate: async (nodeId, opts = {}) => {
    const node = get().nodes.find((n) => n.id === nodeId)
    if (!node) return
    const assetType = node.data.assetType
    const assetName = node.data.assetName || node.data.title
    const prompt = (opts.prompt != null ? opts.prompt : node.data.prompt) || ''
    if (!assetType || !prompt) {
      set({ genState: 'error', genError: '该节点未配置生成参数（assetType / prompt）' })
      return
    }
    set({ genState: 'rendering', genError: null, genResult: null, lockState: 'idle', lockError: null })
    const payload = { asset_type: assetType, asset_name: assetName, prompt }
    // 分镜是电影画幅，未显式指定尺寸时用 16:9（SDXL 原生支持的分辨率桶）
    if (assetType === 'storyboard') {
      payload.width = Number(opts.width) || 1344
      payload.height = Number(opts.height) || 768
    }
    if (opts.negative) payload.negative = opts.negative
    if (opts.seed !== '' && opts.seed != null) payload.seed = Number(opts.seed)
    if (opts.steps) payload.steps = Number(opts.steps)
    if (opts.cfg) payload.cfg = Number(opts.cfg)
    if (opts.width) payload.width = Number(opts.width)
    if (opts.height) payload.height = Number(opts.height)
    if (opts.cost) payload.cost = Number(opts.cost)
    const result = await postAPI('/generate', payload, 180000)
    if (!result || result.error || result.status !== 'generated') {
      const msg =
        result?.status === 'budget_blocked'
          ? '预算不足，无法生成'
          : result?.error || '生成失败（请确认 ComfyUI 服务在 8188 端口运行）'
      set({ genState: 'error', genError: msg })
      return
    }
    set((state) => ({
      genState: 'done',
      genResult: result,
      lockState: 'idle',
      lockError: null,
      nodes: state.nodes.map((n) => {
        if (n.id !== nodeId) return n
        const versionEntry = {
          ver: result.version,
          locked: false,
          web_path: result.web_path,
          image_path: result.image_path,
          seed: result.seed,
        }
        const versions = [...n.data.versions, versionEntry]
        return {
          ...n,
          data: {
            ...n.data,
            preview: {
              web_path: result.web_path,
              image_path: result.image_path,
              version: result.version,
              seed: result.seed,
              params: result.params,
              cost: result.cost,
              saved_at: result.saved_at,
            },
            versions,
            status: n.data.status === 'gray' ? 'blue' : n.data.status,
          },
        }
      }),
    }))
    get().scheduleSave()
    const budget = await fetchAPI('/budget/status')
    if (budget) set((state) => ({ apiData: { ...state.apiData, budget } }))
  },

  // ===== 锁定：将当前预览版本冻结进 K13 版本树 =====
  lockVersion: async (nodeId) => {
    const node = get().nodes.find((n) => n.id === nodeId)
    if (!node || !node.data.preview) return
    const assetType = node.data.assetType
    const assetName = node.data.assetName || node.data.title
    const file_path = node.data.preview.image_path
    const params = {
      prompt: node.data.prompt,
      seed: node.data.preview.seed,
      params: node.data.preview.params,
      cost: node.data.preview.cost,
    }
    set({ lockState: 'locking', lockError: null })
    const result = await postAPI('/lock', {
      asset_type: assetType,
      asset_name: assetName,
      file_path,
      params_json: JSON.stringify(params),
    })
    if (!result || result.error || result.status !== 'locked') {
      set({ lockState: 'error', lockError: result?.error || '锁定失败' })
      return
    }
    set((state) => ({
      lockState: 'done',
      nodes: state.nodes.map((n) => {
        if (n.id !== nodeId) return n
        const versions = n.data.versions.map((v) =>
          v.ver === n.data.preview.version ? { ...v, locked: true } : v
        )
        return { ...n, data: { ...n.data, versions, status: 'green' } }
      }),
    }))
    get().scheduleSave()
    const versions = await fetchAPI('/versions')
    if (versions) set((state) => ({ apiData: { ...state.apiData, versions } }))
  },

  handleNodesChange: (changes) => {
    set((state) => ({ nodes: applyNodeChanges(changes, state.nodes) }))
    // dimensions 是 React Flow 的渲染期尺寸测量，不代表用户改动；
    // 计入触发条件会造成"打开页面即回写"，覆盖磁盘上的手工编辑。
    if (changes.some((c) => ['position', 'remove', 'add'].includes(c.type))) {
      get().scheduleSave()
    }
  },

  handleEdgesChange: (changes) => {
    set((state) => ({ edges: applyEdgeChanges(changes, state.edges) }))
    if (changes.some((c) => ['remove', 'add'].includes(c.type))) {
      get().scheduleSave()
    }
  },

  resetGraph: async () => {
    get().cancelPendingSave()
    const res = await deleteAPI('/graph')
    const restored = !!(res && res.restored)
    set({ nodes: initialNodes, edges: initialEdges, selectedNodeId: 'elem-linxy' })
    set({
      graphSync: restored
        ? { status: 'saved', savedAt: null, restored: true }
        : { status: 'error', savedAt: null, restored: false,
            message: (res && res.message) || '存档未能移出，磁盘上仍是旧画布' },
    })
    return restored
  },

  // ===== 画布持久化 =====
  graphSync: { status: 'idle', savedAt: null },

  // 取消尚未落地的防抖保存。重置画布前必须调用，否则重置前最后一次改动
  // 会在重置之后才 POST 出去，把刚移走的存档又写回来。
  cancelPendingSave: () => {
    clearTimeout(saveTimer)
    saveTimer = null
  },

  scheduleSave: () => {
    const { apiOnline } = get()
    if (!apiOnline) {
      set({ graphSync: { status: 'offline', savedAt: get().graphSync.savedAt } })
      return
    }
    set({ graphSync: { status: 'dirty', savedAt: get().graphSync.savedAt } })
    clearTimeout(saveTimer)
    saveTimer = setTimeout(() => get().saveGraph(), SAVE_DEBOUNCE_MS)
  },

  saveGraph: async () => {
    const { apiOnline, nodes, edges } = get()
    if (!apiOnline) return
    set({ graphSync: { status: 'saving', savedAt: get().graphSync.savedAt } })
    const result = await postAPI('/graph', {
      nodes: cleanNodes(nodes),
      edges: cleanEdges(edges),
    })
    if (result && result.status === 'saved') {
      set({ graphSync: { status: 'saved', savedAt: result.saved_at } })
    } else {
      set({ graphSync: { status: 'error', savedAt: get().graphSync.savedAt } })
    }
  },

  loadGraph: async () => {
    const graph = await fetchAPI('/graph')
    // 存档存在但解析失败：明确报状态，不静默换成默认图。
    if (graph && graph.corrupt) {
      set({ graphSync: { status: 'error', savedAt: null, message: graph.message || 'graph.json 损坏' } })
      return
    }
    if (graph && graph.exists && Array.isArray(graph.nodes) && graph.nodes.length > 0) {
      const nodes = graph.nodes.map((n) => ({
        ...n,
        type: n.type || 'cineast',
        selected: false,
        dragging: false,
      }))
      set({
        nodes,
        edges: graph.edges || [],
        graphSync: { status: 'saved', savedAt: graph.saved_at },
      })
    }
  },

  // ===== Context Menu =====
  contextMenu: null,
  openContextMenu: (menu) => set({ contextMenu: menu }),
  closeContextMenu: () => set({ contextMenu: null }),

  // ===== View Switching =====
  activeView: 'graph',
  switchView: (viewName) => set({ activeView: viewName }),

  // ===== API State =====
  apiOnline: false,
  graphLoaded: false,
  apiData: {
    budget: null,
    versions: null,
    handoffs: null,
    assets: null,
    project: null,
  },

  // ===== AI 渲染（生成闭环）状态 =====
  genState: 'idle', // idle | rendering | done | error
  genError: null,
  genResult: null,
  lockState: 'idle', // idle | locking | done | error
  lockError: null,
  checkAPI: async () => {
    const online = await checkAPIHealth()
    const wasOnline = get().apiOnline
    set({ apiOnline: online })
    if (online) {
      if (!get().graphLoaded) {
        set({ graphLoaded: true })
        await get().loadGraph()
      }
      const [budget, versions, handoffs, assets, project] = await Promise.all([
        fetchAPI('/budget/status'),
        fetchAPI('/versions'),
        fetchAPI('/handoffs'),
        fetchAPI('/assets/status'),
        fetchAPI('/project'),
      ])
      set({
        apiData: { budget, versions, handoffs, assets, project },
      })
    } else if (wasOnline) {
      set({ graphSync: { status: 'offline', savedAt: get().graphSync.savedAt } })
    }
  },

  // ===== Selected Agent (left sidebar) =====
  selectedAgent: 'producer',
  selectAgent: (agentId) => set({ selectedAgent: agentId }),

  // ===== Chat =====
  chatText: '',
  setChatText: (text) => set({ chatText: text }),
  sendInstruction: () => {
    const { chatText } = get()
    const text = chatText.trim()
    if (!text) return
    // 指令入口：在画布右侧空白处生成一个任务节点承载指令原文
    const { nodes, addNode } = get()
    const maxX = nodes.reduce((m, n) => Math.max(m, n.position.x), 400)
    const id = addNode('task', { x: maxX + 250, y: 180 })
    set((state) => ({
      nodes: state.nodes.map((n) =>
        n.id === id
          ? { ...n, data: { ...n.data, title: `指令 · ${text.slice(0, 12)}`, params: [...n.data.params, { k: '原文', v: text }] } }
          : n
      ),
      chatText: '',
    }))
    get().scheduleSave()
  },
}))
