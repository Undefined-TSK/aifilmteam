import { useEffect } from 'react'
import { ReactFlowProvider } from '@xyflow/react'
import { useStore } from './store/useStore.js'
import Topbar from './components/Topbar.jsx'
import LeftSidebar from './components/LeftSidebar.jsx'
import RightSidebar from './components/RightSidebar.jsx'
import BottomBar from './components/BottomBar.jsx'
import NodeGraph from './components/NodeGraph.jsx'
import VersionTree from './components/views/VersionTree.jsx'
import BudgetDashboard from './components/views/BudgetDashboard.jsx'
import HandoffTimeline from './components/views/HandoffTimeline.jsx'
import Storyboard from './components/views/Storyboard.jsx'

export default function App() {
  const activeView = useStore((s) => s.activeView)
  const checkAPI = useStore((s) => s.checkAPI)

  useEffect(() => {
    checkAPI()
    const timer = setInterval(() => checkAPI(), 30000)
    return () => clearInterval(timer)
  }, [checkAPI])

  return (
    <ReactFlowProvider>
      <div className="app">
        <Topbar />
        <LeftSidebar />
        <div className="canvas-area" style={{ position: 'relative', overflow: 'hidden' }}>
          {activeView === 'graph' && <NodeGraph />}
          {activeView === 'versions' && <VersionTree />}
          {activeView === 'budget' && <BudgetDashboard />}
          {activeView === 'handoffs' && <HandoffTimeline />}
          {activeView === 'storyboard' && <Storyboard />}
        </div>
        <RightSidebar />
        <BottomBar />
      </div>
    </ReactFlowProvider>
  )
}
