import React, { useState, useEffect } from 'react';
import { Server, LogOut, RefreshCw } from 'lucide-react';
import { nodeAPI, instanceAPI } from './services/api';
import Login from './components/Login';
import NodeCard from './components/NodeCard';
import InstanceList from './components/InstanceList';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [nodes, setNodes] = useState([]);
  const [instances, setInstances] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Check for existing auth token on mount
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      setIsAuthenticated(true);
      fetchData();
    }
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    
    try {
      const [nodesResponse, instancesResponse] = await Promise.all([
        nodeAPI.list(),
        instanceAPI.list()
      ]);
      
      setNodes(nodesResponse.data);
      setInstances(instancesResponse.data);
    } catch (err) {
      setError('Failed to fetch data: ' + (err.response?.data?.detail || err.message));
      if (err.response?.status === 401) {
        handleLogout();
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (token) => {
    setIsAuthenticated(true);
    fetchData();
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setIsAuthenticated(false);
    setNodes([]);
    setInstances([]);
  };

  const handleStartInstance = async (nodeId, instanceData) => {
    try {
      await nodeAPI.startInstance(nodeId, instanceData);
      await fetchData(); // Refresh data
    } catch (err) {
      setError('Failed to start instance: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleStopInstance = async (nodeId, instanceData) => {
    try {
      await nodeAPI.stopInstance(nodeId, instanceData);
      await fetchData(); // Refresh data
    } catch (err) {
      setError('Failed to stop instance: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Server className="w-8 h-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">PX4 Cloud Simulator</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={fetchData}
                disabled={loading}
                className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-900 disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-900"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Server className="w-8 h-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Nodes</p>
                <p className="text-2xl font-semibold text-gray-900">{nodes.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <Server className="w-4 h-4 text-green-600" />
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Online Nodes</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {nodes.filter(n => n.status === 'online').length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <Server className="w-4 h-4 text-blue-600" />
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Instances</p>
                <p className="text-2xl font-semibold text-gray-900">{instances.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                  <Server className="w-4 h-4 text-green-600" />
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Running Instances</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {instances.filter(i => i.status === 'running').length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Instances Section */}
        <div className="mb-8">
          <InstanceList 
            instances={instances} 
            nodes={nodes}
            onStopInstance={handleStopInstance}
          />
        </div>

        {/* Nodes Section */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Available Nodes</h2>
          {nodes.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <Server className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No nodes available</h3>
              <p className="text-gray-600">Make sure your agents are running and registered with the controller.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {nodes.map(node => (
                <NodeCard
                  key={node.id}
                  node={node}
                  instances={instances}
                  onStartInstance={handleStartInstance}
                  onStopInstance={handleStopInstance}
                />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
