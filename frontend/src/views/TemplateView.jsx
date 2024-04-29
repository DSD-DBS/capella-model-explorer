// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

/*

In this component we show list of template instances, and when we click on a template, we show the rendered instance next to the list. If no imnstance is selected we show a hint to select one.

*/

import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useMediaQuery } from "react-responsive";
import { Header } from "../components/Header";
import { InstanceView } from "../components/InstanceView";
import { TemplateDetails } from "../components/TemplateDetails";

export const TemplateView = ({ endpoint }) => {
  let { templateName, objectID } = useParams();
  const [singleObjectID, setObjectID] = useState(null);
  const isSmallScreen = useMediaQuery({ query: "(max-width: 1080px)" });
  const [isSidebarVisible, setIsSidebarVisible] = useState(!isSmallScreen);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = "";
      document.documentElement.style.overflow = "";
    };
  }, []);
  useEffect(() => {
    setIsSidebarVisible(!isSmallScreen);
  }, [isSmallScreen]);

  const toggleSidebar = () => {
    setIsSidebarVisible(!isSidebarVisible);
    if (!isSidebarVisible) {
      setIsButtonClicked(true);
    }
  };
  return (
    <div>
      <Header />
      {isSmallScreen && (
        <button
          onClick={toggleSidebar}
          className={`fixed left-1/2 top-16 z-20 m-4 flex h-10 w-auto -translate-x-1/2 transform cursor-pointer items-center justify-center rounded-full bg-blue-500 p-2 px-4 text-sm text-white transition-transform duration-500 ease-in-out hover:bg-blue-700 focus:outline-none`}
        >
          {isSidebarVisible ? "Collapse Sidebar" : "Expand Sidebar"}
        </button>
      )}

      <div className="flex">
        <div
          className={`z-19 mt-20 flex w-96 transform flex-col items-center transition-all duration-700 ease-in-out ${
            isSidebarVisible ? "translate-y-0 " : "hidden"
          }`}
        >
          <aside className="h-auto min-w-80 flex-col overflow-y-auto rounded-lg shadow-lg dark:shadow-dark print:hidden">
            <TemplateDetails
              endpoint={endpoint}
              onSingleInstance={setObjectID}
            />
          </aside>
        </div>

        <main>
          <div className="w-[100vw] overflow-y-auto">
            <div className="relative ml-12 mr-12 flex flex-1 ">
              <div className="html-wrapper relative flex h-screen items-center justify-center pt-28">
                {!!!objectID && !!!singleObjectID && (
                  <p
                    className={`${isSmallScreen ? "ml-32" : "ml-80"} text-xl text-gray-700 dark:text-gray-300 `}
                  >
                    Select an Instance
                  </p>
                )}
                {(objectID || singleObjectID) && (
                  <div className="m-auto mx-auto box-border">
                    <InstanceView
                      endpoint={endpoint}
                      objectID={objectID || singleObjectID}
                      templateName={templateName}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};
