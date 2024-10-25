// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useState, useEffect } from 'react';
import { WiredTemplatesList } from '../components/WiredTemplatesList';
import { API_BASE_URL } from '../APIConfig';
import { AppInfo } from '../components/AppInfo';
import { ModelDiff } from '../components/ModelDiff';

export const HomeView = () => {
  const [modelInfo, setModelInfo] = useState(null);
  const [error, setError] = useState(null);
  const [headDate, setHeadDate] = useState(null);
  const [headTag, setHeadTag] = useState(null);
  const [comparedVersionInfo, setComparedVersionInfo] = useState(null);
  const [hasDiffed, setHasDiffed] = useState(false);

  useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        const response = await fetch(API_BASE_URL + '/model-info');
        const data = await response.json();
        setModelInfo(data);
        document.title = `${data.title} - Model Explorer`;
      } catch (err) {
        setError('Failed to fetch model info: ' + err.message);
      }
      document.body.style.height = 'auto';
    };

    fetchModelInfo();
  }, []);

  const fetchDiffInfo = async () => {
    try {
      const response = await fetch(API_BASE_URL + '/diff');
      const data = await response.json();
      if (data.error) {
        console.log('Error fetching model diff:', data.error);
        setComparedVersionInfo(null);
      } else {
        setComparedVersionInfo(data);
        setHasDiffed(true);
      }
    } catch (err) {
      console.log('Failed to fetch model diff: ' + err.message);
      setComparedVersionInfo(null);
    }
  };

  useEffect(() => {
    fetchDiffInfo();
  }, []);

  useEffect(() => {
    const fetchHeadDate = async () => {
      try {
        const response = await fetch(API_BASE_URL + '/commits');
        const data = await response.json();
        if (data && data.length > 0) {
          setHeadDate(data[0].date.substring(0, 10));
          setHeadTag(data[0].tag);
        } else {
          console.log('No commits found');
          setHeadDate('');
          setHeadTag('');
        }
      } catch (err) {
        console.log('Failed to fetch head date: ' + err.message);
        setHeadDate('');
        setHeadTag('');
      }
    };
    fetchHeadDate();
  }, []);

  if (error) {
    return (
      <div
        className="rounded bg-red-500 p-2 text-xl text-white
          dark:bg-custom-dark-error">
        {error}
      </div>
    );
  }

  return (
    <div className="mb-8 flex-col overflow-auto p-4">
      <div className="flex w-full items-center justify-center px-4">
        {modelInfo && (
          <>
            <div
              className="rounded-lg bg-gray-100 p-4 text-gray-700 shadow-lg
                dark:bg-custom-dark-3 dark:text-gray-100 md:mx-auto">
              <h2 className="text-xl">{modelInfo.title}</h2>
              {modelInfo.capella_version && (
                <p>Capella Version: {modelInfo.capella_version}</p>
              )}
              {modelInfo.revision && <p>Revision: {modelInfo.revision}</p>}
              {modelInfo.branch && <p>Branch: {modelInfo.branch}</p>}
              {modelInfo.hash && <p>Current Commit Hash: {modelInfo.hash}</p>}
              {headDate && <p>Date Created: {headDate}</p>}
              {headTag && <p>Tag: {headTag}</p>}
              <ModelDiff onRefetch={fetchDiffInfo} hasDiffed={hasDiffed} />
              {comparedVersionInfo && (
                <div>
                  <p>Compared to Version:</p>
                  {comparedVersionInfo.metadata.old_revision.tag && (
                    <p>Tag: {comparedVersionInfo.metadata.old_revision.tag}</p>
                  )}
                  <p>
                    Commit Hash:{' '}
                    {comparedVersionInfo.metadata.old_revision.hash}
                  </p>
                  <p>
                    Date Created:{' '}
                    {comparedVersionInfo.metadata.old_revision.date.substring(
                      0,
                      10
                    )}
                  </p>
                </div>
              )}
              <div
                className="svg-display hidden md:block"
                dangerouslySetInnerHTML={{ __html: modelInfo.badge }}></div>
            </div>
          </>
        )}
      </div>
      <div className="mt-4">
        <WiredTemplatesList />
      </div>
      <div
        className="mt-10 text-center 3xl:fixed 3xl:bottom-4 3xl:left-4
          3xl:block 3xl:text-left">
        <AppInfo />
      </div>
    </div>
  );
};
