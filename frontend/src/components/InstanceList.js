import React from 'react';
import { Square, ExternalLink, Clock, Server } from 'lucide-react';

const InstanceList = ({ instances, nodes, onStopInstance }) => {
  const getNodeName = (nodeId) => {
    const node = nodes.find(n => n.id === nodeId);
    return node ? node.name : nodeId;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'bg-green-100 text-green-800';
      case 'starting': return 'bg-yellow-100 text-yellow-800';
      case 'stopping': return 'bg-orange-100 text-orange-800';
      case 'stopped': return 'bg-gray-100 text-gray-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  if (instances.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <Server className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No instances running</h3>
        <p className="text-gray-600">Start an instance on one of your nodes to see it here.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Running Instances</h2>
      </div>
      <div className="divide-y divide-gray-200">
        {instances.map(instance => (
          <div key={instance.id} className="px-6 py-4 hover:bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <h3 className="text-sm font-medium text-gray-900">{instance.name}</h3>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(instance.status)}`}>
                    {instance.status}
                  </span>
                </div>
                <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                  <span>{instance.vehicle_type} • {instance.model}</span>
                  <span className="flex items-center">
                    <Server className="w-3 h-3 mr-1" />
                    {getNodeName(instance.node_id)}
                  </span>
                  {instance.mav_udp && (
                    <span>Port: {instance.mav_udp}</span>
                  )}
                </div>
                <div className="mt-1 flex items-center space-x-4 text-xs text-gray-400">
                  <span className="flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    Started {formatDate(instance.created_at)}
                  </span>
                  {instance.updated_at !== instance.created_at && (
                    <span>Updated {formatDate(instance.updated_at)}</span>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {instance.mav_udp && (
                  <button
                    onClick={() => {
                      // Open QGroundControl connection
                      const qgcUrl = `qgroundcontrol://?connection=UDP&host=localhost&port=${instance.mav_udp}`;
                      window.open(qgcUrl, '_blank');
                    }}
                    className="p-2 text-gray-400 hover:text-primary-600"
                    title="Connect with QGroundControl"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </button>
                )}
                {instance.status === 'running' && (
                  <button
                    onClick={() => onStopInstance(instance.node_id, { instance_id: instance.id })}
                    className="p-2 text-red-600 hover:text-red-800"
                    title="Stop instance"
                  >
                    <Square className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default InstanceList;
