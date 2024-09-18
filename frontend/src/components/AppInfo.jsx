// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useState, useEffect } from 'react';
import { ROUTE_PREFIX } from '../APIConfig';
import { SiGithub } from '@icons-pack/react-simple-icons';

export const AppInfo = () => {
  const [currentVersion, setCurrentVersion] = useState(null);

  useEffect(() => {
    fetch(`${ROUTE_PREFIX}/static/version.json`)
      .then((response) => response.json())
      .then((data) => setCurrentVersion(data.git))
      .catch((error) => {
        console.error(error);
        setCurrentVersion({ version: 'Fetch failed' });
      });
  }, []);

  return (
    <div className="text-black dark:text-gray-100 print:hidden">
      {currentVersion && <p>Version: {currentVersion.version}</p>}
      <a
        href="https://github.com/DSD-DBS/capella-model-explorer"
        className="flex items-center space-x-2 hover:underline"
        target="_blank">
        <span>Contribute on GitHub</span>
        <div
          className="flex h-6 w-6 items-center justify-center rounded-full
            bg-custom-light">
          <SiGithub className="h-5 w-5 text-black" />
        </div>
      </a>
    </div>
  );
};
