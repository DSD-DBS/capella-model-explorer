// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0
import { useEffect, useState } from 'react';
import { SVGDisplay } from './SVGDisplay';
import { API_BASE_URL } from '../APIConfig';
import { Spinner } from './Spinner';

export const DiffView = ({ objectID, endpoint }) => {
  const [details, setDetails] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchTemplate = async () => {
      setIsLoading(true);

      try {
        const postResponse = await fetch(`${API_BASE_URL}/object-diff`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ uuid: objectID })
        });

        if (!postResponse.ok) {
          throw new Error(
            `Failed to post diff data: ${postResponse.statusText}`
          );
        }

        let url;
        if (objectID) {
          url = `${endpoint}object_comparison/${objectID}`;
        } else {
          throw new Error('Object ID is missing or invalid');
        }

        const getResponse = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'text/html'
          }
        });

        if (!getResponse.ok) {
          throw new Error(
            `Failed to fetch object comparison: ${getResponse.statusText}`
          );
        }

        const data = await getResponse.text();

        const parser = new DOMParser();
        const doc = parser.parseFromString(data, 'text/html');
        const contentItems = [];

        doc.body.childNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.tagName === 'svg') {
              contentItems.push({
                type: 'SVGDisplay',
                content: node.outerHTML
              });
            } else {
              contentItems.push({
                type: 'HTML',
                content: node.outerHTML
              });
            }
          }
        });

        setDetails(contentItems);
      } catch (error) {
        console.error('Error fetching template:', error);
        setDetails([
          { type: 'Error', content: `Error fetching data: ${error.message}` }
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    if (objectID) {
      fetchTemplate();
    }
  }, [objectID]);

  return (
    <div
      className="flex min-h-screen items-center justify-center
        overflow-x-hidden">
      {isLoading ? (
        <Spinner />
      ) : (
        <div
          className="html-content scrollbar scrollbar-track-gray-200
            scrollbar-thumb-gray-400 dark:scrollbar-track-custom-dark-3
            dark:scrollbar-thumb-slate-600 mb-4 rounded-lg border-4
            border-transparent bg-gray-100 p-8 text-gray-700 shadow-lg
            hover:border-gray-300 hover:shadow-md dark:bg-custom-dark-2
            dark:text-gray-100 dark:shadow-dark md:w-[210mm] print:m-0
            print:bg-transparent print:p-0 print:shadow-none">
          {details.map((item, idx) => {
            if (item.type === 'SVGDisplay') {
              return <SVGDisplay key={idx} content={item.content} />;
            } else {
              return (
                <div
                  key={idx}
                  dangerouslySetInnerHTML={{
                    __html: item.content
                  }}
                />
              );
            }
          })}
        </div>
      )}
    </div>
  );
};
