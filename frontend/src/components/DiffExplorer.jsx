// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useState } from 'react';
import {
  CirclePlus,
  CircleX,
  SquareAsterisk,
  FolderOpen,
  SquareChevronDown,
  SquareChevronRightIcon,
  FolderClosed,
  Dot,
  File
} from 'lucide-react';

export const DiffExplorer = ({
  node,
  setObjectID,
  searchTerm,
  filterStatus
}) => {
  const [expandedNodes, setExpandedNodes] = useState({});

  const getNodeClass = (changed, attributes) => {
    const hasNonEmptyAttributes =
      attributes && Object.keys(attributes).length > 0;
    switch (changed) {
      case 'created':
        return 'text-green-500';
      case 'deleted':
        return 'text-red-500 line-through cursor-not-allowed dark:text-custom-dark-error';
      case 'modified':
        return hasNonEmptyAttributes
          ? 'text-orange-600'
          : 'text-gray-500 dark:text-gray-200';
      default:
        return 'text-gray-900 dark:text-gray-100';
    }
  };

  const getIcon = (changed, attributes) => {
    const hasNonEmptyAttributes =
      attributes && Object.keys(attributes).length > 0;
    switch (changed) {
      case 'created':
        return <CirclePlus className="h-5 w-5 text-green-500" />;
      case 'deleted':
        return (
          <CircleX className="h-5 w-5 text-red-500 dark:text-custom-dark-error" />
        );
      case 'modified':
        return hasNonEmptyAttributes ? (
          <SquareAsterisk className="h-5 w-5 text-orange-600" />
        ) : (
          <Dot className="h-8 w-8 text-orange-600" />
        );
      default:
        return null;
    }
  };

  const handleToggle = (uuid) => {
    setExpandedNodes((prev) => ({
      ...prev,
      [uuid]: !prev[uuid]
    }));
  };

  const handleLeafClick = (node) => {
    setObjectID(node.uuid);
  };

  const flattenNodes = (node) => {
    let nodes = [];
    if (node.children) {
      Object.values(node.children).forEach((child) => {
        nodes = nodes.concat(flattenNodes(child));
      });
    }
    nodes.push(node);
    return nodes;
  };

  const filterNodes = (node) => {
    const allNodes = flattenNodes(node);
    return allNodes.filter((n) => {
      if (filterStatus !== 'all' && n.change !== filterStatus) {
        return false;
      }
      if (!searchTerm) return true;
      return n.display_name.toLowerCase().includes(searchTerm.toLowerCase());
    });
  };

  const renderNode = (node) => {
    const hasChildren = node.children && Object.keys(node.children).length > 0;
    const isExpanded = expandedNodes[node.uuid] || false;
    return (
      <div
        key={node.uuid}
        className={`text-start ${getNodeClass(node.change, node.attributes)}`}>
        <div className="flex items-center justify-between">
          <div className="flex min-w-0 flex-1 gap-2">
            {hasChildren ? (
              <button
                onClick={() => handleToggle(node.uuid)}
                className="flex items-center">
                {isExpanded ? (
                  <>
                    <SquareChevronDown className="mr-2 dark:text-gray-200" />
                    <FolderOpen className="dark:text-gray-200" />
                  </>
                ) : (
                  <>
                    <SquareChevronRightIcon className="mr-2 dark:text-gray-200" />
                    <FolderClosed className="dark:text-gray-200" />
                  </>
                )}
              </button>
            ) : (
              <File className="ml-5 dark:text-gray-200" />
            )}
            <span
              onClick={() => handleLeafClick(node)}
              className={`flex-1 cursor-pointer truncate
                ${node.change === 'deleted' ? 'pointer-events-none' : ''}`}
              title={node.display_name}>
              {node.display_name}
            </span>
          </div>
          <span
            className={`flex h-6 w-6 items-center justify-center rounded-full
              ${getNodeClass(node.change, node.attributes)}`}>
            {getIcon(node.change, node.attributes)}
          </span>
        </div>
        {isExpanded && hasChildren && (
          <div className="ml-3">
            {Object.keys(node.children).map((childId) => (
              <DiffExplorer
                key={childId}
                node={node.children[childId]}
                setObjectID={setObjectID}
                searchTerm={searchTerm}
                filterStatus={filterStatus}
              />
            ))}
          </div>
        )}
      </div>
    );
  };

  const filteredNodes = filterNodes(node);
  return (
    <div>
      {searchTerm || filterStatus !== 'all'
        ? filteredNodes.map((filteredNode) => renderNode(filteredNode))
        : renderNode(node)}
    </div>
  );
};
