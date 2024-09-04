// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React, { useState } from 'react';

export const DiffExplorer = ({
  node,
  nodeId,
  setObjectID,
  setDiffData,
  searchTerm,
  filterStatus
}) => {
  const [expanded, setExpanded] = useState(false);
  const hasChildren = node.children && Object.keys(node.children).length > 0;

  const getNodeClass = (changed, attributes) => {
    const hasNonEmptyAttributes =
      attributes && Object.keys(attributes).length > 0;
    switch (changed) {
      case 'created':
        return 'text-green-500';
      case 'deleted':
        return 'text-red-500 line-through cursor-not-allowed';
      case 'modified':
        return hasNonEmptyAttributes ? 'text-orange-500' : 'text-gray-400';
      default:
        return 'text-gray-900';
    }
  };

  const handleToggle = () => {
    setExpanded(!expanded);
  };

  const handleLeafClick = () => {
    setObjectID(nodeId);
    setDiffData(node);
  };

  const filterNodes = (node) => {
    if (filterStatus !== 'all' && node.change !== filterStatus) {
      if (node.children) {
        return Object.values(node.children).some(filterNodes);
      }
      return false;
    }
    if (!searchTerm) return true;
    if (node.display_name.toLowerCase().includes(searchTerm.toLowerCase()))
      return true;
    if (node.children) {
      return Object.values(node.children).some(filterNodes);
    }
    return false;
  };

  if (!filterNodes(node)) return null;

  return (
    <div>
      <div
        key={nodeId}
        className={`ml-4 text-start ${getNodeClass(node.change, node.attributes)}`}>
        <div className="flex items-center">
          {hasChildren && (
            <span onClick={handleToggle} className="mr-2 cursor-pointer">
              {expanded ? '▼' : '▶'}
            </span>
          )}
          <span
            onClick={handleLeafClick}
            className={`max-w-xs cursor-pointer truncate ${node.change === 'deleted' ? 'pointer-events-none' : ''}`}
            title={node.display_name}>
            {node.display_name}
          </span>
        </div>
        {expanded && hasChildren && (
          <div className="ml-4">
            {Object.keys(node.children).map((childId) => (
              <DiffExplorer
                key={childId}
                node={node.children[childId]}
                nodeId={childId}
                setObjectID={setObjectID}
                setDiffData={setDiffData}
                searchTerm={searchTerm}
                filterStatus={filterStatus}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
