// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { API_BASE_URL } from '../APIConfig';

export const Breadcrumbs = () => {
  const location = useLocation();
  const [breadcrumbLabels, setBreadcrumbLabels] = useState({});
  const pathnames = location.pathname.split('/').filter((x) => x);

  const fetchModelInfo = async () => {
    const response = await fetch(API_BASE_URL + `/model-info`);
    const modelInfo = await response.json();
    return modelInfo.title;
  };

  // Function to fetch view names
  const fetchViewName = async (idx) => {
    const response = await fetch(API_BASE_URL + `/views`);

    const viewsDict = await response.json();
    const allViews = Object.values(viewsDict).flat();
    const view = allViews.find((v) => v.idx.toString() === idx);
    return view ? view.name : idx;
  };

  // Function to fetch object names
  const fetchObjectName = async (uuid) => {
    const response = await fetch(API_BASE_URL + `/objects/${uuid}`);
    const object = await response.json();
    return object.name;
  };

  useEffect(() => {
    const updateLabels = async () => {
      const title = await fetchModelInfo();
      const labels = { '/': title };

      for (let i = 0; i < pathnames.length; i++) {
        const to = `/${pathnames.slice(0, i + 1).join('/')}`;

        if (i === 0) {
          labels[to] = await fetchViewName(pathnames[i]);
        } else if (i === 1) {
          labels[to] = await fetchObjectName(pathnames[i]);
        } else {
          labels[to] = pathnames[i];
        }
      }

      setBreadcrumbLabels(labels);
      const modelName = Object.values(labels)[0];
      const instanceName = Object.values(labels).pop();
      document.title = `${instanceName} - ${modelName} - Model Explorer`;
    };
    updateLabels();
  }, [location, document.title]);

  const visible_pathnames = [
    breadcrumbLabels['/'],
    ...location.pathname.split('/').filter((x) => x)
  ];
  const slicedPathnames = visible_pathnames.slice(1);

  return (
    <nav
      aria-label="breadcrumb"
      className="flex items-center font-medium text-black dark:text-gray-200">
      <ol className="flex items-center">
        <li className="hidden items-center truncate lg:block">
          <Link to={'/'}>{breadcrumbLabels['/']}</Link>
          <span className="mx-0 md:mx-2">/</span>
        </li>

        {slicedPathnames.map((value, index) => {
          const last = index === slicedPathnames.length - 1;
          const to = `/${slicedPathnames.slice(0, index + 1).join('/')}`;
          const label = breadcrumbLabels[to] || value;

          return (
            <li className="flex items-center truncate md:items-start" key={to}>
              {!last && (
                <Link
                  to={to}
                  className="hidden max-w-64 truncate whitespace-nowrap
                    md:block">
                  {label}
                </Link>
              )}
              {last && (
                <span
                  className="hidden w-full truncate whitespace-nowrap
                    text-custom-blue custom-phone-width:block
                    custom-phone-width:max-w-60 md:max-w-full"
                  title={label}>
                  {label}
                </span>
              )}
              {!last && <span className="mx-2 hidden md:block">/</span>}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
