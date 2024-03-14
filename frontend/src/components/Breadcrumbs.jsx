import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { API_BASE_URL } from '../APIConfig';

export const Breadcrumbs = () => {
  const location = useLocation();
  const [breadcrumbLabels, setBreadcrumbLabels] = useState({});
  const pathnames = location.pathname.split('/').filter(x => x);

  const fetchModelInfo = async () => {
    const response = await fetch(API_BASE_URL + `/model-info`);
    const modelInfo = await response.json();
    return modelInfo.title;
  };

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
    return object.name;
  };

  useEffect(() => {
    const updateLabels = async () => {
      const title = await fetchModelInfo();
      const labels = { '/': title };
  
      for (let i = 0; i < pathnames.length; i++) {
        const to = `/${pathnames.slice(0, i + 1).join('/')}`;
  
        if (pathnames[i] === 'views') {
          labels[to] = 'Views';
        } else if (i === 1 && pathnames[0] === 'views') {
          labels[to] = await fetchViewName(pathnames[i]);
        } else if (i === 2 && pathnames[0] === 'views') {
          labels[to] = await fetchObjectName(pathnames[i]);
        } else {
          labels[to] = pathnames[i];
        }
      }
      console.log(labels);
  
      setBreadcrumbLabels(labels);
    };
  
    updateLabels();
  }, [location]);

  const visible_pathnames = [breadcrumbLabels['/'], ...location.pathname.split('/').filter(x => x)];

  return (
    <nav aria-label="breadcrumb" className="flex items-center">
      <ol className="flex items-center">
        <li className="flex items-center">
          <span>{breadcrumbLabels['/']}</span>
          <span className="mx-2">/</span>
        </li>
        {visible_pathnames.slice(1).map((value, index) => {
          const last = index === visible_pathnames.length - 2;
          const to = `/${visible_pathnames.slice(1, index + 2).join('/')}`;
          const label = breadcrumbLabels[to] || value;
  
          return (
            <li className="flex items-center" key={to}>
              {!last && <Link to={to}>{label}</Link>}
              {last && <span>{label}</span>}
              {!last && <span className="mx-2">/</span>}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
