import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { API_BASE_URL } from '../APIConfig';

export const Breadcrumbs = () => {
  const location = useLocation();
  const [breadcrumbLabels, setBreadcrumbLabels] = useState({});
  const pathnames = location.pathname.split('/').filter(x => x);

  // Function to fetch view names
  const fetchViewName = async (idx) => {
    const response = await fetch(API_BASE_URL + `/views`);
    
    const views = await response.json();
    const view = views.find(v => v.idx.toString() === idx);
    return view ? view.name : idx;
  };

  // Function to fetch object names
  const fetchObjectName = async (uuid) => {
    const response = await fetch(API_BASE_URL + `/objects/${uuid}`);
    const object = await response.json();
    console.log(object);
    return object.name;
  };

  useEffect(() => {
    const updateLabels = async () => {
      const labels = {};

      for (let i = 0; i < pathnames.length; i++) {
        const segment = pathnames[i];

        if (segment === 'views' && i + 1 < pathnames.length) {
          // Assuming the next segment is the view idx
          const viewName = await fetchViewName(pathnames[i + 1]);
          labels[`/${pathnames.slice(0, i + 2).join('/')}`] = viewName;
          i++; // Skip next since it's processed
        } else if (segment === 'objects' && i + 1 < pathnames.length) {
          // Assuming the next segment is the object ID
          const objectName = await fetchObjectName(pathnames[i + 1]);
          labels[`/${pathnames.slice(0, i + 2).join('/')}`] = objectName;
          i++; // Skip next since it's processed
        } else {
          labels[`/${pathnames.slice(0, i + 1).join('/')}`] = segment;
        }
      }

      setBreadcrumbLabels(labels);
    };

    updateLabels();
  }, [location]);

  return (
    <nav aria-label="breadcrumb">
      <ol>
        {pathnames.map((value, index) => {
          const last = index === pathnames.length - 1;
          const to = `/${pathnames.slice(0, index + 1).join('/')}`;
          const label = breadcrumbLabels[to] || value;

          return last ? (
            <li key={to}>{label}</li>
          ) : (
            <li key={to}>
              <Link to={to}>{label}</Link>
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
