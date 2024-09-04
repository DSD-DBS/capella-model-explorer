// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React from 'react';
import { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { DiffExplorer } from '../components/DiffExplorer';
import { DiffView } from '../components/DiffView';
import { API_BASE_URL } from '../APIConfig';

export const ModelComparisonView = () => {
  const [modelDiff, setModelDiff] = useState(null);
  const [objectID, setObjectID] = useState(null);
  const endpoint = `${API_BASE_URL}/views/`;
  const [diffData, setDiffData] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };
  const handleStatusChange = (event) => {
    setFilterStatus(event.target.value);
  };

  const filterNodes = (node) => {
    if (!searchTerm) return true;
    if (node.display_name.toLowerCase().includes(searchTerm.toLowerCase()))
      return true;
    if (node.children) {
      return Object.values(node.children).some(filterNodes);
    }
    return false;
  };

  useEffect(() => {
    const fetchModelDiff = async () => {
      try {
        const response = await fetch(API_BASE_URL + '/diff');
        const data = await response.json();
        setModelDiff(data);
      } catch (err) {
        setModelDiff({});
      }
      document.body.style.height = 'auto';
    };

    fetchModelDiff();
  }, []);

  useEffect(() => {}, [objectID]);
  useEffect(() => {}, [diffData]);

  return (
    <div>
      <Header />
      <div className="relative top-28 min-h-screen">
        <div className="fixed left-0 flex h-[calc(100vh-6rem)] w-1/4 flex-col overflow-auto rounded-lg bg-gray-100 p-4 shadow-lg dark:bg-custom-dark-2 dark:shadow-dark">
          <div className="mb-4">
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="w-full rounded border border-gray-300 p-2"
            />
            <select
              value={filterStatus}
              onChange={handleStatusChange}
              className="w-full rounded border border-gray-300 p-2">
              <option value="all">All</option>
              <option value="created">Created</option>
              <option value="deleted">Deleted</option>
              <option value="modified">Modified</option>
            </select>
          </div>
          {modelDiff &&
            modelDiff.objects &&
            Object.keys(modelDiff.objects).map(
              (layer) =>
                modelDiff.objects[layer] && (
                  <DiffExplorer
                    key={layer}
                    nodeId={layer}
                    node={modelDiff.objects[layer]}
                    setObjectID={setObjectID}
                    setDiffData={setDiffData}
                    searchTerm={searchTerm}
                    filterStatus={filterStatus}
                  />
                )
            )}
        </div>
        <div className="relative flex flex-1 md:ml-12 md:mr-12">
          <div className="relative mt-2 flex items-center justify-center  print:pt-0">
            {objectID && (
              <DiffView
                objectID={objectID}
                endpoint={endpoint}
                diffData={diffData}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
