// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

/*

In this component we show list of template instances, and when we click on a template, we show the rendered instance next to the list. If no imnstance is selected we show a hint to select one.

*/

import React, { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { useMediaQuery } from 'react-responsive';
import { Header } from "../components/Header";
import { InstanceView } from "../components/InstanceView";
import { TemplateDetails } from "../components/TemplateDetails";
import { Button } from '../components/Button';

export const TemplateView = ({ endpoint }) => {
    let { templateName, objectID } = useParams();
    const [singleObjectID, setObjectID] = useState(null);
    const location = useLocation();
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
    const isSmallScreen = useMediaQuery({ query: '(max-width: 1024px)' });


    useEffect(() => {}, [endpoint, templateName, objectID, location]);

    return (
        <div className="flex flex-col h-screen">
            <Header />
            {isSmallScreen && (
                <div className="flex justify-center">
                    <Button 
                        className="px-4 py-2"
                        onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                    >
                        {isSidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
                    </Button>
                </div>
            )}
            <div className="flex flex-1 overflow-hidden">
                <aside className={`print:hidden lg:block lg:w-80 h-full p-4 overflow-y-auto ${isSidebarCollapsed ? 'hidden' : 'w-64 h-screen'}`}>
                    <TemplateDetails
                        endpoint={endpoint}
                        onSingleInstance={setObjectID}
                    />
                </aside>            
                <main className="flex-1 overflow-hidden p-4">
                    <div className="html-wrapper w-full p-4 max-w-none lg:max-w-4xl min-w-0 lg:min-w-[850px] overflow-y-hidden h-full flex items-center justify-center">
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
