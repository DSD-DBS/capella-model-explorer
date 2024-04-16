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
                if (contentRef.current)
                    contentRef.current.scrollIntoView();
            })
            .catch((error) => {
                setLoading(false);
                setDetails("Error fetching data ", error);
            });
    }, [endpoint, objectID, templateName]);
    if (loading)
        return (
            <div>
                <Spinner />
            </div>
        );
    return (
        <div
            ref={contentRef}
            className={`html-content bg-white shadow-lg dark:shadow-white text-gray-700 mx-auto md:my-8 p-8 md:w-[210mm] max-w-full max-h-full overflow-auto print:shadow-none print:m-0 print:p-0 print:bg-transparent relative box-border border-4 ${
                isHovering
                    ? "border-grey-700 shadow-md z-50"
                    : "border-transparent"
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
                    return (
                        <SVGDisplay key={idx} content={item.content} />
                    );
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
