// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { API_BASE_URL } from '../APIConfig';
import { Recycle } from 'lucide-react';

export const TemplateDetails = ({ endpoint, onSingleInstance }) => {
  const [modelDiff, setModelDiff] = useState(null);
  let { templateName, objectID } = useParams();
  const [error, setError] = useState(null);
  const [details, setDetails] = useState([]);
  const navigate = useNavigate();
  const [filterText, setFilterText] = useState('');

  useEffect(() => {
    const fetchModelDiff = async () => {
      try {
        const response = await fetch(API_BASE_URL + '/model-diff');
        const data = await response.json();
        setModelDiff(data);
      } catch (err) {
        setError('Failed to fetch model info: ' + err.message);
      }
      document.body.style.height = 'auto';
    };

    fetchModelDiff();
  }, []);

  const modifiedItems = [
    ...Object.values(modelDiff?.Diagrams?.Modified || []).map(
      (item) => item.uuid
    ),
    ...Object.values(modelDiff?.Objects || {}).reduce((acc, object) => {
      const modifiedNames = object.modified || [];
      const uuid = modifiedNames.map((item) => item.uuid);
      return acc.concat(uuid);
    }, [])
  ];

  const createdItems = [
    ...Object.values(modelDiff?.Diagrams?.Created || []).map(
      (item) => item.uuid
    ),
    ...Object.values(modelDiff?.Objects || {}).reduce((acc, object) => {
      const createdNames = object.created || [];
      const uuid = createdNames.map((item) => item.uuid);
      return acc.concat(uuid);
    }, [])
  ];

  console.log(createdItems);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const response = await fetch(endpoint + templateName, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        const data = await response.json();
        setDetails(data);
        if (data.single) {
          onSingleInstance('render');
        }
      } catch (error) {
        setError(error.message);
      }
    };
    fetchDetails();
  }, [endpoint, templateName, objectID, onSingleInstance]);
  if (error) {
    return (
      <div
        className={
          'rounded bg-red-500 p-4 text-2xl text-white ' +
          'dark:bg-custom-dark-error'
        }>
        {error}
      </div>
    );
  }
  return (
    <div
      className={
        'flex h-full max-h-[calc(90vh-32px)] w-80 flex-col overflow-hidden ' +
        'rounded-lg bg-gray-100 p-4 shadow-lg dark:bg-custom-dark-2 ' +
        'dark:shadow-dark'
      }>
      <h5
        className={'mb-2 text-2xl font-bold text-gray-900 dark:text-gray-100'}>
        {details.name}
      </h5>
      <p className="mb-3 font-normal text-gray-700 dark:text-gray-300">
        {details.description}
      </p>
      {details.error ? (
        <div>
          <p className="mb-3 font-bold text-gray-700 dark:text-gray-300">
            We failed to find matching template instances due to the following
            error:{' '}
          </p>
          <div
            className={
              'rounded bg-red-500 px-2 py-2 font-bold text-gray-100 ' +
              'dark:bg-custom-dark-error'
            }>
            {details.error}
          </div>
        </div>
      ) : (
        <>
          {details && !details.single ? (
            <input
              type="text"
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
              placeholder="Filter objects"
              className={
                'mx-auto mb-3 mr-6 w-full rounded bg-custom-light p-2 ' +
                'text-gray-700 shadow-sm dark:border-gray-500 ' +
                'dark:bg-custom-dark-3 dark:text-gray-100'
              }
            />
          ) : (
            <></>
          )}
          <div
            className={
              'flex flex-wrap items-center justify-center overflow-auto ' +
              'border-2 border-transparent text-left scrollbar ' +
              'scrollbar-track-gray-200 scrollbar-thumb-gray-400 ' +
              'dark:scrollbar-track-custom-dark-3 ' +
              'dark:scrollbar-thumb-slate-600'
            }>
            {details.instanceList &&
            details.single === false &&
            details.instanceList.length === 0 ? (
              <p
                className={
                  'mb-3 font-normal text-gray-700 dark:text-gray-300'
                }>
                No objects found
              </p>
            ) : (
              details.instanceList &&
              details.instanceList
                .filter(
                  (object) =>
                    object.name &&
                    object.name
                      .toLowerCase()
                      .includes(filterText.toLowerCase())
                )
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((object) => (
                  <div
                    key={object.idx}
                    onClick={() => {
                      navigate(`/${templateName}/${object.idx}`);
                    }}
                    className={`${
                      objectID && object.idx === objectID
                        ? 'w-full bg-custom-blue text-white dark:bg-custom-blue dark:text-gray-100'
                        : 'w-full bg-gray-200 text-gray-900 dark:bg-custom-dark-4'
                    } ${
                      createdItems.includes(object.idx)
                        ? 'border-l-8 border-transparent border-l-green-500'
                        : modifiedItems.includes(object.idx)
                          ? 'border-l-8 border-transparent border-l-orange-500'
                          : 'border-transparent'
                    } dark:bg-dark-quaternary m-2 min-w-0 cursor-pointer rounded-lg
                    border-2 shadow-md hover:bg-custom-blue hover:text-white
                    dark:shadow-dark dark:hover:bg-blue-500`}>
                    <div className="flex items-center justify-between p-2">
                      <h5 className="text-md break-words font-bold dark:text-gray-100">
                        {object.name}
                      </h5>
                    </div>
                  </div>
                ))
            )}
          </div>
        </>
      )}
    </div>
  );
};
