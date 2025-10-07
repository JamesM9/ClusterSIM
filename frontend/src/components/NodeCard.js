import React, { useState } from 'react';
import { Server, Cpu, HardDrive, Memory, Play, Square, Wifi, WifiOff } from 'lucide-react';

const NodeCard = ({ node, onStartInstance, onStopInstance, instances }) => {
  const [showStartForm, setShowStartForm] = useState(false);
  const [instanceForm, setInstanceForm] = useState({
    name: '',
    model: 'iris',
    vehicle_type: 'copter'
  });

  const nodeInstances = instances.filter(instance => instance.node_id === node.id);
  const runningInstances = nodeInstances.filter(instance => instance.status === 'running');

  const handleStartInstance = (e) => {
    e.preventDefault();
    const instanceData = {
      name: instanceForm.name || `sim-${Date.now()}`,
      model: instanceForm.model,
      vehicle_type: instanceForm.vehicle_type
    };
    onStartInstance(node.id, instanceData);
    setShowStartForm(false);
    setInstanceForm({ name: '', model: 'iris', vehicle_type: 'copter' });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'online': return 'text-green-600';
      case 'offline': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status) => {
    return status === 'online' ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Server className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">{node.name}</h3>
        </div>
        <div className={`flex items-center space-x-1 ${getStatusColor(node.status)}`}>
          {getStatusIcon(node.status)}
          <span className="text-sm font-medium capitalize">{node.status}</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-gray-500" />
          <span className="text-sm text-gray-600">{node.cpu_cores} cores</span>
        </div>
        <div className="flex items-center space-x-2">
          <Memory className="w-4 h-4 text-gray-500" />
          <span className="text-sm text-gray-600">{node.memory_gb}GB RAM</span>
        </div>
        <div className="flex items-center space-x-2">
          <HardDrive className="w-4 h-4 text-gray-500" />
          <span className="text-sm text-gray-600">{node.disk_gb}GB disk</span>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">Address: {node.address}</p>
        <p className="text-sm text-gray-600">
          Running instances: {runningInstances.length}
        </p>
      </div>

      <div className="space-y-2 mb-4">
        {runningInstances.map(instance => (
          <div key={instance.id} className="flex items-center justify-between bg-gray-50 p-2 rounded">
            <div>
              <span className="text-sm font-medium">{instance.name}</span>
              <span className="text-xs text-gray-500 ml-2">
                {instance.vehicle_type} ({instance.model})
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-500">Port: {instance.mav_udp}</span>
              <button
                onClick={() => onStopInstance(node.id, { instance_id: instance.id })}
                className="p-1 text-red-600 hover:text-red-800"
                title="Stop instance"
              >
                <Square className="w-3 h-3" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {!showStartForm ? (
        <button
          onClick={() => setShowStartForm(true)}
          disabled={node.status !== 'online'}
          className="w-full flex items-center justify-center space-x-2 py-2 px-4 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          <Play className="w-4 h-4" />
          <span>Start Instance</span>
        </button>
      ) : (
        <form onSubmit={handleStartInstance} className="space-y-3">
          <div>
            <input
              type="text"
              placeholder="Instance name (optional)"
              value={instanceForm.name}
              onChange={(e) => setInstanceForm({...instanceForm, name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <select
              value={instanceForm.model}
              onChange={(e) => setInstanceForm({...instanceForm, model: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              <option value="iris">Iris</option>
              <option value="x500">X500</option>
              <option value="solo">Solo</option>
            </select>
            <select
              value={instanceForm.vehicle_type}
              onChange={(e) => setInstanceForm({...instanceForm, vehicle_type: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              <option value="copter">Copter</option>
              <option value="plane">Plane</option>
              <option value="rover">Rover</option>
            </select>
          </div>
          <div className="flex space-x-2">
            <button
              type="submit"
              className="flex-1 py-2 px-4 bg-primary-600 text-white rounded-md hover:bg-primary-700 text-sm"
            >
              Start
            </button>
            <button
              type="button"
              onClick={() => setShowStartForm(false)}
              className="flex-1 py-2 px-4 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 text-sm"
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default NodeCard;
