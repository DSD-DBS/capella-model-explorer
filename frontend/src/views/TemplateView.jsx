// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

/*

In this component we show list of template instances, and when we click on a template, we show the rendered instance next to the list. If no imnstance is selected we show a hint to select one.

*/

import React, { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { Header } from "../components/Header";
import { InstanceView } from "../components/InstanceView";
import { TemplateDetails } from "../components/TemplateDetails";

export const TemplateView = ({ endpoint }) => {
    let { templateName, objectID } = useParams();
    const [singleObjectID, setObjectID] = useState(null);
    const location = useLocation();

    useEffect(() => {}, [endpoint, templateName, objectID, location]);

    return (
        <div className="flex flex-col h-screen">
            {" "}
            {/* Use h-screen to ensure the container fits the viewport height */}
            {/* Header */}
            <Header />
            {/* Body: Sidebar + Main Content */}
            <div className="flex flex-1 overflow-hidden">
                {" "}
                {/* This ensures the remaining height is distributed here */}
                {/* Sidebar - Adjust visibility/responsiveness as needed */}
                <aside className="hidden lg:block lg:w-80 p-4 overflow-y-auto">
                    {" "}
                    {/* Use overflow-y-auto to enable vertical scrolling */}
                    <TemplateDetails
                        endpoint={endpoint}
                        onSingleInstance={setObjectID}
                    />
                </aside>
                {/* Main Content */}
                <main className="flex-1 overflow-hidden p-4">
                    <div className="w-full p-4 max-w-none lg:max-w-4xl min-w-0 lg:min-w-[850px] overflow-y-hidden h-full flex items-center justify-center">
                        {" "}
                        {/* Ensure main content is scrollable and fills the height */}
                        {!!!objectID && !!!singleObjectID && (
                            <p className="text-xl text-gray-700">
                                Select an Instance
                            </p>
                        )}
                        {(objectID || singleObjectID) && (
                            <InstanceView
                                endpoint={endpoint}
                                objectID={objectID || singleObjectID}
                                templateName={templateName}
                            />
                        )}
                    </div>
                </main>
            </div>
        </div>
    );
};
