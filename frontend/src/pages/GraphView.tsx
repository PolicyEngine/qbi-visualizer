import { useEffect, useState, useCallback } from 'react'
import axios from 'axios'
import ReactFlow, {
  Node,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  MarkerType,
  Handle,
  Position,
} from 'reactflow'
import 'reactflow/dist/style.css'

interface VariableData {
  name: string
  class_name: string
  label: string
  entity: string
  definition_period: string
  value_type: string
  unit: string
  documentation: string
  reference: string[]
  has_formula: boolean
  is_input: boolean
  formula_source: string
  formula_github_url: string
  github_url: string
  dependencies: string[]
  parameters: string[]
}

interface GraphData {
  nodes: Array<{
    id: string
    label: string
    type: 'input' | 'intermediate' | 'output' | 'operation' | 'parameter'
    entity: string
  }>
  edges: Array<{
    source: string
    target: string
    type: string
  }>
}

// Custom node component
const VariableNode = ({ data, selected }: { data: any; selected: boolean }) => {
  const colors = {
    input: { bg: 'bg-blue-500', border: 'border-blue-600', ring: 'ring-blue-300' },
    intermediate: { bg: 'bg-amber-500', border: 'border-amber-600', ring: 'ring-amber-300' },
    output: { bg: 'bg-emerald-500', border: 'border-emerald-600', ring: 'ring-emerald-300' },
  }
  const color = colors[data.nodeType as keyof typeof colors] || colors.intermediate

  return (
    <div
      className={`px-4 py-3 rounded-lg shadow-md border-2 ${color.bg} ${color.border} text-white min-w-[200px] ${
        selected ? `ring-4 ${color.ring}` : ''
      }`}
    >
      <Handle type="target" position={Position.Left} className="!bg-slate-400" />
      <div className="font-semibold text-sm leading-tight">{data.label}</div>
      <div className="text-xs opacity-80 mt-1">{data.entity}</div>
      <Handle type="source" position={Position.Right} className="!bg-slate-400" />
    </div>
  )
}

const nodeTypes = {
  variable: VariableNode,
}

function GraphView() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [variables, setVariables] = useState<Record<string, VariableData>>({})
  const [selectedVariable, setSelectedVariable] = useState<VariableData | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)

      // Fetch both graph structure and variable details
      const [graphRes, varsRes] = await Promise.all([
        axios.get<GraphData>('/api/variables/graph/dependency'),
        axios.get<{ variables: VariableData[] }>('/api/variables/')
      ])

      // Create variables lookup
      const varsMap: Record<string, VariableData> = {}
      varsRes.data.variables.forEach(v => {
        varsMap[v.name] = v
      })
      setVariables(varsMap)

      // Filter to only main variable nodes
      const variableNodes = graphRes.data.nodes.filter(
        n => n.type === 'input' || n.type === 'intermediate' || n.type === 'output'
      )

      // Filter edges to variable-to-variable only
      const variableIds = new Set(variableNodes.map(n => n.id))
      const variableEdges = graphRes.data.edges.filter(
        e => variableIds.has(e.source) && variableIds.has(e.target)
      )

      // Layout and create nodes
      const { nodes: layoutNodes, edges: layoutEdges } = layoutGraph(variableNodes, variableEdges)

      setNodes(layoutNodes)
      setEdges(layoutEdges)
      setError(null)
    } catch (err) {
      setError('Failed to load graph data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const layoutGraph = (
    rawNodes: GraphData['nodes'],
    rawEdges: GraphData['edges']
  ) => {
    const nodeHeight = 70
    const nodeWidth = 220
    const verticalGap = 25
    const horizontalGap = 280

    // Build dependency map
    const dependsOn = new Map<string, Set<string>>()
    rawEdges.forEach(edge => {
      if (!dependsOn.has(edge.target)) {
        dependsOn.set(edge.target, new Set())
      }
      dependsOn.get(edge.target)!.add(edge.source)
    })

    // Calculate layers (topological sort)
    const layers = new Map<string, number>()

    const getLayer = (nodeId: string, visited = new Set<string>()): number => {
      if (layers.has(nodeId)) return layers.get(nodeId)!
      if (visited.has(nodeId)) return 0

      visited.add(nodeId)
      const deps = dependsOn.get(nodeId)

      if (!deps || deps.size === 0) {
        layers.set(nodeId, 0)
        return 0
      }

      let maxDepLayer = -1
      deps.forEach(depId => {
        maxDepLayer = Math.max(maxDepLayer, getLayer(depId, visited))
      })

      const layer = maxDepLayer + 1
      layers.set(nodeId, layer)
      return layer
    }

    rawNodes.forEach(n => getLayer(n.id))

    // Group by layer
    const nodesByLayer = new Map<number, typeof rawNodes>()
    let maxLayer = 0
    rawNodes.forEach(node => {
      const layer = layers.get(node.id) || 0
      maxLayer = Math.max(maxLayer, layer)
      if (!nodesByLayer.has(layer)) nodesByLayer.set(layer, [])
      nodesByLayer.get(layer)!.push(node)
    })

    // Sort nodes within each layer by type (inputs first)
    nodesByLayer.forEach((nodesInLayer, layer) => {
      nodesInLayer.sort((a, b) => {
        const order = { input: 0, intermediate: 1, output: 2 }
        return (order[a.type as keyof typeof order] || 1) - (order[b.type as keyof typeof order] || 1)
      })
    })

    // Position nodes
    const resultNodes: Node[] = []

    for (let layer = 0; layer <= maxLayer; layer++) {
      const nodesInLayer = nodesByLayer.get(layer) || []

      nodesInLayer.forEach((node, idx) => {
        resultNodes.push({
          id: node.id,
          type: 'variable',
          position: {
            x: 50 + layer * horizontalGap,
            y: 50 + idx * (nodeHeight + verticalGap),
          },
          data: {
            label: node.label || node.id,
            entity: node.entity,
            nodeType: node.type,
          },
        })
      })
    }

    // Create edges
    const resultEdges = rawEdges.map((edge, idx) => ({
      id: `e-${idx}`,
      source: edge.source,
      target: edge.target,
      type: 'smoothstep',
      style: { stroke: '#94a3b8', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#94a3b8' },
    }))

    return { nodes: resultNodes, edges: resultEdges }
  }

  const onNodeClick = useCallback((_: any, node: Node) => {
    const varData = variables[node.id]
    setSelectedVariable(varData || null)
  }, [variables])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-slate-50">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin mx-auto mb-3"></div>
          <div className="text-slate-500">Loading dependency graph...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-slate-50">
        <div className="bg-white border border-red-200 rounded-xl p-6 max-w-md">
          <h3 className="text-red-700 font-semibold mb-2">Error</h3>
          <p className="text-slate-600 text-sm mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm hover:bg-slate-800"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  // Count node types
  const inputCount = nodes.filter(n => n.data.nodeType === 'input').length
  const intermediateCount = nodes.filter(n => n.data.nodeType === 'intermediate').length
  const outputCount = nodes.filter(n => n.data.nodeType === 'output').length

  return (
    <div className="h-full w-full flex bg-slate-50">
      {/* Graph */}
      <div className="flex-1 relative">
        {/* Legend */}
        <div className="absolute top-4 left-4 z-10 bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <h3 className="font-semibold text-slate-900 text-sm mb-3">Variable Types</h3>
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 rounded bg-blue-500"></div>
              <span className="text-sm text-slate-600">Input ({inputCount})</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 rounded bg-amber-500"></div>
              <span className="text-sm text-slate-600">Intermediate ({intermediateCount})</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 rounded bg-emerald-500"></div>
              <span className="text-sm text-slate-600">Output ({outputCount})</span>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100">
            <p className="text-xs text-slate-400">Click a node to view details</p>
          </div>
        </div>

        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.3}
          maxZoom={1.5}
        >
          <Background color="#e2e8f0" gap={20} />
          <Controls className="!bg-white !border-slate-200 !rounded-lg !shadow-sm" />
        </ReactFlow>
      </div>

      {/* Detail Panel */}
      <div className={`w-[400px] bg-white border-l border-slate-200 overflow-y-auto transition-all ${selectedVariable ? '' : 'hidden'}`}>
        {selectedVariable && (
          <>
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-slate-200 p-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className={`inline-block px-2 py-0.5 rounded text-xs font-medium mb-2 ${
                    selectedVariable.is_input
                      ? 'bg-blue-100 text-blue-700'
                      : selectedVariable.name === 'qualified_business_income_deduction'
                        ? 'bg-emerald-100 text-emerald-700'
                        : 'bg-amber-100 text-amber-700'
                  }`}>
                    {selectedVariable.is_input ? 'Input' : selectedVariable.name === 'qualified_business_income_deduction' ? 'Output' : 'Intermediate'}
                  </div>
                  <h2 className="text-lg font-semibold text-slate-900">{selectedVariable.label}</h2>
                  <code className="text-xs text-slate-500 font-mono">{selectedVariable.name}</code>
                </div>
                <button
                  onClick={() => setSelectedVariable(null)}
                  className="text-slate-400 hover:text-slate-600 p-1"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="p-4 space-y-6">
              {/* Metadata */}
              <div>
                <h3 className="text-sm font-semibold text-slate-700 mb-3">Metadata</h3>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs text-slate-500">Entity</div>
                    <div className="font-medium text-slate-900">{selectedVariable.entity}</div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs text-slate-500">Period</div>
                    <div className="font-medium text-slate-900">{selectedVariable.definition_period}</div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs text-slate-500">Type</div>
                    <div className="font-medium text-slate-900">{selectedVariable.value_type}</div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs text-slate-500">Unit</div>
                    <div className="font-medium text-slate-900">{selectedVariable.unit || '—'}</div>
                  </div>
                </div>
              </div>

              {/* Documentation */}
              {selectedVariable.documentation && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-2">Description</h3>
                  <p className="text-sm text-slate-600">{selectedVariable.documentation}</p>
                </div>
              )}

              {/* Formula */}
              {selectedVariable.has_formula && selectedVariable.formula_source && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-semibold text-slate-700">Formula</h3>
                    {selectedVariable.formula_github_url && (
                      <a
                        href={selectedVariable.formula_github_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        View on GitHub
                      </a>
                    )}
                  </div>
                  <pre className="bg-slate-900 text-slate-100 rounded-lg p-4 text-xs overflow-x-auto font-mono leading-relaxed">
                    {selectedVariable.formula_source}
                  </pre>
                </div>
              )}

              {/* Input indicator */}
              {selectedVariable.is_input && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <div className="font-medium text-blue-900 text-sm">Input Variable</div>
                      <p className="text-sm text-blue-700 mt-1">This is a user-provided input with no computation formula.</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Dependencies */}
              {selectedVariable.dependencies && selectedVariable.dependencies.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-2">Dependencies</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedVariable.dependencies.map(dep => (
                      <button
                        key={dep}
                        onClick={() => {
                          const v = variables[dep]
                          if (v) setSelectedVariable(v)
                        }}
                        className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 rounded-lg text-xs font-mono text-slate-700 transition-colors"
                      >
                        {dep}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Parameters */}
              {selectedVariable.parameters && selectedVariable.parameters.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-2">Parameters Used</h3>
                  <div className="space-y-2">
                    {selectedVariable.parameters.map(param => (
                      <div key={param} className="px-3 py-2 bg-purple-50 border border-purple-200 rounded-lg text-xs font-mono text-purple-700">
                        {param}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* References */}
              {selectedVariable.reference && selectedVariable.reference.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-2">Legal References</h3>
                  <div className="space-y-2">
                    {selectedVariable.reference.map((ref, idx) => (
                      <a
                        key={idx}
                        href={ref}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block text-sm text-blue-600 hover:text-blue-800 truncate"
                      >
                        {ref}
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {/* GitHub link */}
              {selectedVariable.github_url && (
                <a
                  href={selectedVariable.github_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900 py-2 px-3 bg-slate-50 rounded-lg border border-slate-200 hover:border-slate-300 transition-colors"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                  </svg>
                  View Source File
                </a>
              )}
            </div>
          </>
        )}
      </div>

      {/* Empty state when nothing selected */}
      {!selectedVariable && (
        <div className="w-[400px] bg-white border-l border-slate-200 flex items-center justify-center">
          <div className="text-center p-6">
            <svg className="w-12 h-12 mx-auto mb-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
            </svg>
            <p className="text-sm text-slate-500">Select a variable to view details</p>
            <p className="text-xs text-slate-400 mt-1">Click any node in the graph</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default GraphView
