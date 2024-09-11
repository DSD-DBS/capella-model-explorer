// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0
import { useEffect, useState } from 'react';
import { SVGDisplay } from './SVGDisplay';
import { API_BASE_URL } from '../APIConfig';
import { Spinner } from './Spinner';

export const DiffView = ({ objectID, endpoint, diffData }) => {
  const [details, setDetails] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchTemplate = () => {
      setIsLoading(true);
      fetch(`${API_BASE_URL}/object-diff`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(diffData)
      })
        .then((response) => response.json())
        .then(() => {
          let url;
          if (diffData.change) {
            url = `${endpoint}object_comparison/${objectID}`;
          }
          fetch(url, {
            method: 'GET',
            headers: {
              'Content-Type': 'text/html'
            }
          })
            .then((response) => response.text())
            .then((data) => {
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
              setIsLoading(false);
            })
            .catch((error) => {
              setDetails([
                { type: 'Error', content: `Error fetching data: ${error}` }
              ]);
              setIsLoading(false);
            });
        })
        .catch((error) => {
          console.error('Error posting diff data:', error);
          setIsLoading(false);
        });
    };

    if (objectID) {
      fetchTemplate();
    }
  }, [objectID]);

  return (
    <div>
      <div
        className="html-content mb-4 rounded-lg border-4 border-transparent
          bg-gray-100 p-8 text-gray-700 shadow-lg scrollbar
          scrollbar-track-gray-200 scrollbar-thumb-gray-400
          hover:border-gray-300 hover:shadow-md dark:bg-custom-dark-2
          dark:text-gray-100  dark:shadow-dark
          dark:scrollbar-track-custom-dark-3 dark:scrollbar-thumb-slate-600
          md:w-[210mm] print:m-0 print:bg-transparent print:p-0 print:shadow-none">
        {isLoading ? (
          <Spinner />
        ) : (
          details.map((item, idx) => {
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
          })
        )}
      </div>
    </div>
  );
};
