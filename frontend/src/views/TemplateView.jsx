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
import { Printer } from "lucide-react";

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

  useEffect(() => {
    if (!objectID && !singleObjectID) {
      setIsSidebarVisible(true);
    }
  }, [objectID, singleObjectID]);
  return (
    <div>
      <Header
        isSmallScreen={isSmallScreen}
        toggleSidebar={toggleSidebar}
        isSidebarVisible={isSidebarVisible}
      />
      <div className="flex">
        <div
          className={`z-19 mr-8 mt-32 flex w-auto transform flex-col items-center transition-all duration-700 ease-in-out md:mt-20 ${
            isSidebarVisible ? "translate-y-0" : "hidden"
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
            <div className="relative flex flex-1 md:ml-12 md:mr-12 ">
              <div className="html-wrapper relative flex h-screen items-center justify-center pt-32">
                {!!!objectID && !!!singleObjectID && (
                  <p className="translate-x-full text-xl text-gray-700 dark:text-gray-300">
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
