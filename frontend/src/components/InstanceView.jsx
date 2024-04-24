// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React, { useEffect, useRef, useState } from "react";
import { SVGDisplay } from "./SVGDisplay";
import { Spinner } from "./Spinner";
import { Button } from "./Button";

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
    document.body.style.height = 'auto';
    document.body.style.minHeight = '100vh';
    if (!contentRef.current) return;
    const currentHeight = contentRef.current.scrollHeight;
    document.body.style.height = `${currentHeight + 100}px`;
  }, [details]);
  
  if (loading)
    return (
      <div className="mx-auto md:w-[210mm]">
        <Spinner />
      </div>
    );
  return (
    <div
      ref={contentRef}
      className={`html-content rounded-lg border-4 border-transparent bg-gray-100 p-8 text-gray-700 shadow-lg scrollbar scrollbar-track-gray-200 scrollbar-thumb-gray-400 hover:border-gray-300 dark:bg-custom-dark-2 dark:text-gray-100 dark:shadow-dark dark:scrollbar-track-custom-dark-3 dark:scrollbar-thumb-slate-600 md:w-[210mm] print:m-0 print:bg-transparent print:p-0 print:shadow-none ${
        isHovering ? "z-50 shadow-md" : ""
      }`}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {isHovering && (
        <Button
          style={{
            position: "absolute",
            top: 0,
            right: 0,
            margin: "1rem",
            padding: "0.5rem",
          }}
          onClick={() => window.print()}
        >
          Print Content
        </Button>
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
    </div>
  );
};
