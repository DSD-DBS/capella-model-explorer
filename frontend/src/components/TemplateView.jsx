/*

In this component we show list of template instances, and when we click on a template, we show the rendered instance next to the list. If no imnstance is selected we show a hint to select one.

*/

import React, {useEffect, useState} from 'react';
import { TemplateDetails } from './TemplateDetails';
import { useLocation, useParams, Navigate } from 'react-router-dom';
import { InstanceView } from './InstanceView';
import { Breadcrumbs } from './Breadcrumbs';
import { ThemeSwitcher } from './ThemeSwitcher';

export const TemplateView = ({endpoint}) => {
    let { templateName, objectID } = useParams();
    const location = useLocation();

    useEffect(() => {
    }, [endpoint, templateName, objectID, location]);

    return (
        <div className="flex flex-col h-screen"> {/* Use h-screen to ensure the container fits the viewport height */}
            {/* Header */}
            <header className=" text-gray-700 p-4 flex justify-between items-center">
                <div><Breadcrumbs /></div>
                <div></div>
                <div><ThemeSwitcher /></div>
            </header>

            {/* Body: Sidebar + Main Content */}
            <div className="flex flex-1 overflow-hidden"> {/* This ensures the remaining height is distributed here */}
                {/* Sidebar - Adjust visibility/responsiveness as needed */}
                <aside className="hidden lg:block lg:w-80 p-4 overflow-y-auto"> {/* Use overflow-y-auto to enable vertical scrolling */}
                    <TemplateDetails endpoint={endpoint} />
                </aside>

                {/* Main Content */}
                <main className="flex-1 overflow-hidden p-4">
                    <div className="w-full p-4 max-w-none lg:max-w-4xl min-w-0 lg:min-w-[850px] overflow-y-auto h-full"> {/* Ensure main content is scrollable and fills the height */}
                        { !!!objectID && <p>Select an Instance</p>}
                        { objectID && <InstanceView endpoint={endpoint} objectID={objectID} templateName={templateName} /> }
                    </div>
                </main>
            </div>
        </div>
    );
}
