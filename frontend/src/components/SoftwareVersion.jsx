// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useState, useEffect } from 'react';
import { API_BASE_URL, ROUTE_PREFIX } from '../APIConfig';

export const SoftwareVersion = () => {
  const [frontendVersion, setFrontendVersion] = useState(null);
  const [backendVersion, setBackendVersion] = useState(null);

  useEffect(() => {
    fetch(`${ROUTE_PREFIX}/static/version.json`)
      .then((response) => response.json())
      .then((data) => setFrontendVersion(data.git))
      .catch((error) => {
        console.error(error);
        setFrontendVersion({ version: 'Fetch failed' });
      });
  }, []);

  useEffect(() => {
    fetch(`${API_BASE_URL}/metadata`)
      .then((response) => response.json())
      .then((data) => setBackendVersion(data.version))
      .catch((error) => {
        console.error(error);
        setBackendVersion('Fetch failed');
      });
  }, []);

  return (
    <div className="text-gray-500 dark:text-gray-300 print:hidden">
      {frontendVersion && (
        <p>Frontend Version: {frontendVersion.version}</p>
      )}
      {backendVersion && <p>Backend Version: {backendVersion}</p>}
    </div>
  );
};
