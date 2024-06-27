// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useState, useEffect } from 'react';
import { ROUTE_PREFIX } from '../APIConfig';
import { SquareMousePointer } from 'lucide-react';

export const AppInfo = () => {
  const [currentVersion, setcurrentVersion] = useState(null);

  useEffect(() => {
    fetch(`${ROUTE_PREFIX}/static/version.json`)
      .then((response) => response.json())
      .then((data) => setcurrentVersion(data.git))
      .catch((error) => {
        console.error(error);
        setcurrentVersion({ version: 'Fetch failed' });
      });
  }, []);

  return (
    <div className="text-gray-500 dark:text-gray-300 print:hidden">
      {currentVersion && <p>Version: {currentVersion.version}</p>}
      <a
        href="https://github.com/DSD-DBS/capella-model-explorer"
        target="_blank"
        className="text-custom-blue hover:text-custom-blue-hover">
        Contribute on GitHub
        <SquareMousePointer
          className="
          ml-1 inline-block h-4 w-4 text-custom-blue
          hover:text-custom-blue-hover"
        />
      </a>
    </div>
  );
};
