// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React, { useState, useEffect } from 'react';
import { WiredTemplatesList } from '../components/WiredTemplatesList';
import { API_BASE_URL } from '../APIConfig';
import { SoftwareVersion } from '../components/SoftwareVersion';

export const HomeView = () => {
  const [modelInfo, setModelInfo] = useState(null);
  const [error, setError] = useState(null);
  const [modelDiff, setModelDiff] = useState(null);

  useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        const response = await fetch(API_BASE_URL + '/model-info');
        const data = await response.json();
        setModelInfo(data);
      } catch (err) {
        setError('Failed to fetch model info: ' + err.message);
      }
      document.body.style.height = 'auto';
    };

    fetchModelInfo();
  }, []);

  useEffect(() => {
    const fetchModelDiff = async () => {
      try {
        const response = await fetch(API_BASE_URL + '/data');
        const data = await response.json();
        setModelDiff(data);
      } catch (err) {
        setError('Failed to fetch model info: ' + err.message);
      }
      document.body.style.height = 'auto';
    };

    fetchModelDiff();
  }, []);

  if (error) {
    return (
      <div className="rounded bg-red-500 p-2 text-xl text-white dark:bg-custom-dark-error">
        {error}
      </div>
    );
  }

  return (
    <div className="mb-8 flex-col overflow-auto p-4">
      <div className="flex w-full items-center justify-center px-4">
        {modelInfo && (
          <div className="rounded-lg bg-gray-100 p-4 text-gray-700 shadow-lg dark:bg-custom-dark-3 dark:text-gray-100 md:mx-auto">
            <h2 className="text-xl">{modelInfo.title}</h2>
            {modelInfo.capella_version && (
              <p>Capella Version: {modelInfo.capella_version}</p>
            )}
            {modelInfo.revision && <p>Revision: {modelInfo.revision}</p>}
            {modelInfo.branch && <p>Branch: {modelInfo.branch}</p>}
            {modelInfo.hash && <p>Current Commit Hash: {modelInfo.hash}</p>}
            {modelDiff?.metadata?.new_revision && (
              <>
                <p className="pb-2">
                  Created on:{' '}
                  {new Date(
                    modelDiff.metadata.new_revision.date
                  ).toLocaleString()}
                </p>
              </>
            )}
            <div
              className="hidden md:block"
              dangerouslySetInnerHTML={{ __html: modelInfo.badge }}></div>
            {modelDiff?.metadata?.old_revision && (
              <>
                <p className="pt-2">
                  Comparing with commit hash:{' '}
                  {modelDiff.metadata.old_revision.hash}
                </p>
                <p>
                  Created on:{' '}
                  {new Date(
                    modelDiff.metadata.old_revision.date
                  ).toLocaleString()}
                </p>
              </>
            )}
          </div>
        )}
      </div>
      <div className="mt-4">
        <WiredTemplatesList />
      </div>
      <div className="mt-8 text-center 3xl:fixed 3xl:bottom-4 3xl:left-4 3xl:block 3xl:text-left">
        <SoftwareVersion />
      </div>
    </div>
  );
};
