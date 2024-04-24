// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

/*

In this component we show list of template instances, and when we click on a template, we show the rendered instance next to the list. If no imnstance is selected we show a hint to select one.

*/

import React, { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { useMediaQuery } from "react-responsive";
import { Header } from "../components/Header";
import { InstanceView } from "../components/InstanceView";
import { TemplateDetails } from "../components/TemplateDetails";
import { Button } from "../components/Button";

export const TemplateView = ({ endpoint }) => {
  let { templateName, objectID } = useParams();
  const [singleObjectID, setObjectID] = useState(null);
  const location = useLocation();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const isSmallScreen = useMediaQuery({ query: "(max-width: 1024px)" });

  useEffect(() => {
    if (isSmallScreen) {
      setIsSidebarCollapsed(true);
    }
  }, [isSmallScreen]);

  return (
    <div>
      <div className="fixed h-screen w-auto flex-col left-0 top-0">
      <Header />
      {isSmallScreen && (
        <div className="mt-8 flex justify-center">
          <Button
            className="px-4 py-2"
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          >
            {isSidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          </Button>
        </div>
      )}
      <div className="flex-32 flex">
        <aside
          className={`mb-8 mt-8 flex max-h-[75vh] flex-col overflow-y-auto rounded-lg shadow-lg dark:shadow-dark lg:block lg:w-96 print:hidden ${
            isSidebarCollapsed ? "hidden" : "h-screen w-64"
          }`}
        >
          <TemplateDetails endpoint={endpoint} onSingleInstance={setObjectID} />
        </aside>
        
      </div>
    </div>
      <main className="flex-1 ">
          <div className="html-wrapper ml-8 mt-8 flex h-[80vh] min-w-0 max-w-none items-start justify-center  lg:min-w-[650px] lg:max-w-4xl">
            {!!!objectID && !!!singleObjectID && (
              <p className="text-xl text-gray-700 dark:text-gray-300">
                Select an Instance
              </p>
            )}
            {(objectID || singleObjectID) && (
              <div className=" mx-auto box-border mb-4">
                <InstanceView
                  endpoint={endpoint}
                  objectID={objectID || singleObjectID}
                  templateName={templateName}
                />
              </div>
            )}
          </div>
        </main>
    </div>
  );
};
