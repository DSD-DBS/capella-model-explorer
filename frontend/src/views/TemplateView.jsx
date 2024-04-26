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
import { ChevronUp } from "lucide-react";

export const TemplateView = ({ endpoint }) => {
  let { templateName, objectID } = useParams();
  const [singleObjectID, setObjectID] = useState(null);
  const isSmallScreen = useMediaQuery({ query: "(max-width: 1800px)" });
  const [isSidebarVisible, setIsSidebarVisible] = useState(!isSmallScreen);

  const [isButtonClicked, setIsButtonClicked] = useState(false);

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

      <div
        className={`fixed left-16 z-20 mt-20 flex w-96 transform flex-col items-center transition-all duration-700 ease-in-out ${
          isSidebarVisible ? "translate-y-0 " : "-translate-y-full"
        }`}
      >
        <aside className="m-h-50[vh] h-full w-full flex-col overflow-y-auto rounded-lg shadow-lg dark:shadow-dark print:hidden">
          <TemplateDetails endpoint={endpoint} onSingleInstance={setObjectID} />
        </aside>
        <button
          onClick={toggleSidebar}
          className={` flex h-8 w-16 cursor-pointer items-center justify-center rounded-full rounded-t-none bg-blue-500 p-2 transition-transform duration-500 ease-in-out hover:bg-blue-700 focus:outline-none ${
            isSidebarVisible ? "translate-y-0" : "translate-y-[2rem] "
          }`}
        >
          <ChevronUp
            className={`h-6 w-6 transform text-white  transition-all duration-700 ease-in-out ${
              isSidebarVisible ? "" : " rotate-180"
            }`}
          />
        </button>
      </div>

      <main>
        <div className="flex">
          {isSidebarVisible && isSmallScreen && (
            <div className="fixed left-0 top-0 z-10 h-screen w-screen bg-black opacity-50 dark:bg-gray-700"></div>
          )}
          <div
            className={`html-wrapper relative flex h-screen flex-1 items-center justify-center pb-12 pt-28`}
          >
            {!!!objectID && !!!singleObjectID && (
              <p className="text-xl text-gray-700 dark:text-gray-300">
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
      </main>
    </div>
  );
};
