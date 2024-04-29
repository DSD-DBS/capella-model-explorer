// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React, { useEffect, useRef, useState } from "react";
import { SVGDisplay } from "./SVGDisplay";
import { Spinner } from "./Spinner";
import { Button } from "./Button";
import { Printer } from "lucide-react";

export const InstanceView = ({ templateName, objectID, endpoint }) => {
  const [details, setDetails] = useState([]);
  const [loading, setLoading] = useState(true);
  const contentRef = useRef(null);
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    setLoading(true);
    const url = endpoint + `${templateName}/${objectID}`;
    fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "text/html",
      },
    })
      .then((response) => response.text())
      .then((data) => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(data, "text/html");
        const contentItems = [];
        doc.body.childNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.tagName === "svg") {
              contentItems.push({
                type: "SVGDisplay",
                content: node.outerHTML,
              });
            } else {
              contentItems.push({
                type: "HTML",
                content: node.outerHTML,
              });
            }
          }
        });
        setDetails(contentItems);
        setLoading(false);
      })
      .catch((error) => {
        setLoading(false);
        setDetails("Error fetching data ", error);
      });
  }, [endpoint, objectID, templateName]);

  useEffect(() => {
    document.body.style.height = "auto";
    document.body.style.minHeight = "100vh";
    if (!contentRef.current) return;
    const currentHeight = contentRef.current.scrollHeight;
    document.body.style.height = `${currentHeight + 150}px`;
  }, [details]);

  return (
    <div
      ref={contentRef}
      className={`html-content rounded-lg border-4 border-transparent bg-gray-100 p-8 text-gray-700 shadow-lg  scrollbar scrollbar-track-gray-200 scrollbar-thumb-gray-400 hover:border-gray-300 dark:bg-custom-dark-2 dark:text-gray-100 dark:shadow-dark dark:scrollbar-track-custom-dark-3 dark:scrollbar-thumb-slate-600 md:w-[210mm] print:m-0 print:bg-transparent print:p-0 print:shadow-none ${
        isHovering ? " shadow-md" : ""
      }`}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {loading ? (
        <div className="flex h-screen -translate-y-48 transform items-center justify-center">
          <Spinner />
        </div>
      ) : (
        <>
          {isHovering && (
            <div className="fixed -ml-14 -mt-6">
              <div
                onClick={() => window.print()}
                className="flex cursor-pointer items-center justify-center rounded-full bg-custom-blue p-2 text-white transition-colors duration-700 ease-in-out hover:bg-custom-dark-4 dark:bg-custom-blue dark:text-gray-100 dark:hover:bg-custom-light"
              >
                <Printer></Printer>
              </div>
            </div>
          )}
          {details.map((item, idx) => {
            if (item.type === "SVGDisplay") {
              return <SVGDisplay key={idx} content={item.content} />;
            } else {
              return (
                <div
                  key={idx}
                  dangerouslySetInnerHTML={{
                    __html: item.content,
                  }}
                />
              );
            }
          })}
        </>
      )}
    </div>
  );
};
