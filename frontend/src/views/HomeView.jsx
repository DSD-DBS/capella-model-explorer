// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React, { useState, useEffect } from "react";
import { WiredTemplatesList } from "../components/WiredTemplatesList";
import { API_BASE_URL } from "../APIConfig";
import { ThemeSwitcher } from "../components/ThemeSwitcher";

export const HomeView = () => {
  const [modelInfo, setModelInfo] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        const response = await fetch(API_BASE_URL + "/model-info");
        const data = await response.json();
        setModelInfo(data);
      } catch (err) {
        setError("Failed to fetch model info: " + err.message);
      }
    };

    fetchModelInfo();
  }, []);

  if (error) {
    return (
      <div className="dark:bg-custom-dark-error rounded bg-red-500 p-2 text-xl text-white">
        {error}
      </div>
    );
  }

  return (
    <div className="mb-8 flex h-full flex-col justify-center">
      <div className="flex w-full items-start justify-between px-4 ">
        <div className="mx-auto mb-8 text-center ">
          {modelInfo && (
            <div className="rounded-b-lg bg-gray-100 p-4 text-gray-700 shadow-lg dark:bg-custom-dark-3 dark:text-gray-100 ">
              <h2 className="text-xl">{modelInfo.title}</h2>
              {modelInfo.capella_version && (
                <p>Capella Version: {modelInfo.capella_version}</p>
              )}
              {modelInfo.revision && <p>Revision: {modelInfo.revision}</p>}
              {modelInfo.branch && <p>Branch: {modelInfo.branch}</p>}
              {modelInfo.hash && <p>Commit Hash: {modelInfo.hash}</p>}
              <div dangerouslySetInnerHTML={{ __html: modelInfo.badge }}></div>
            </div>
          )}
        </div>
        <div className="flex items-start justify-end rounded-b-lg bg-gray-100 p-6 shadow-lg dark:bg-custom-dark-2">
          <ThemeSwitcher />
        </div>
      </div>
      <div className="mt-4">
        <WiredTemplatesList />
      </div>
    </div>
  );
};
