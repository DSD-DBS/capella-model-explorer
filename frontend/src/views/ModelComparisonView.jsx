// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { DiffExplorer } from '../components/DiffExplorer';
import { DiffView } from '../components/DiffView';
import { API_BASE_URL } from '../APIConfig';
import { useMediaQuery } from 'react-responsive';

export const ModelComparisonView = ({ endpoint }) => {
  const [modelDiff, setModelDiff] = useState(null);
  const [objectID, setObjectID] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const isSmallScreen = useMediaQuery({ query: '(max-width: 1080px)' });
  const [isSidebarVisible, setIsSidebarVisible] = useState(!isSmallScreen);

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };
  const handleStatusChange = (event) => {
    setFilterStatus(event.target.value);
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
  useEffect(() => {
    setIsSidebarVisible(!isSmallScreen);
  }, [isSmallScreen]);

  const toggleSidebar = () => {
    setIsSidebarVisible(!isSidebarVisible);
  };

  return (
    <div>
      <Header />
      {isSmallScreen && (
        <button
          onClick={toggleSidebar}
          className={`text-md fixed left-1/2 top-16 z-20 m-4 flex h-10 w-auto
          -translate-x-1/2 cursor-pointer items-center justify-center
          rounded-b-md border-2 border-gray-900 bg-custom-blue p-2 px-4
          text-white transition-transform duration-500 ease-in-out
          hover:bg-custom-blue-hover focus:outline-none dark:border-white
          print:hidden`}>
          {isSidebarVisible ? 'Collapse Sidebar' : 'Expand Sidebar'}
        </button>
      )}
      <div className="flex min-h-screen pt-28">
        <div
          className={`scrollbar scrollbar-track-gray-200
            scrollbar-thumb-gray-400 dark:scrollbar-track-custom-dark-3
            dark:scrollbar-thumb-slate-600 fixed left-0 h-[calc(100vh-8rem)]
            w-96 flex-none overflow-auto overflow-y-scroll rounded-md
            border-b-4 border-t-4 border-gray-300 bg-gray-100 p-4 shadow-lg
            dark:border-custom-dark-3 dark:bg-custom-dark-2 dark:shadow-dark ${
            isSidebarVisible ? 'translate-x-0' : '-translate-x-full' }`}
          style={{ minWidth: '25%' }}>
          <div className="mb-4">
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="mx-auto mb-2 w-full rounded border-2
                border-transparent bg-custom-light p-2 text-gray-700 shadow-sm
                focus:border-gray-400 focus:outline-none dark:border-gray-500
                dark:bg-custom-dark-3 dark:text-gray-100
                dark:focus:border-custom-dark-1"
            />
            <select
              value={filterStatus}
              onChange={handleStatusChange}
              className="custom-select mx-auto mb-2 w-full rounded border-2
                border-transparent bg-custom-light p-2 text-gray-700 shadow-sm
                focus:border-gray-400 focus:outline-none dark:border-gray-500
                dark:bg-custom-dark-3 dark:text-gray-100
                dark:focus:border-custom-dark-1">
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
                Object.keys(modelDiff.objects[layer]).length > 0 && (
                  <DiffExplorer
                    key={modelDiff.objects[layer]}
                    node={modelDiff.objects[layer]}
                    setObjectID={setObjectID}
                    searchTerm={searchTerm}
                    filterStatus={filterStatus}
                  />
                )
            )}
        </div>
        <div
          className={`flex-1 overflow-y-hidden
            ${isSmallScreen ? (isSidebarVisible ? 'pl-96' : '') : 'pl-96'}`}>
          <div className="relative flex flex-1">
            {objectID && <DiffView objectID={objectID} endpoint={endpoint} />}
          </div>
        </div>
      </div>
    </div>
  );
};
