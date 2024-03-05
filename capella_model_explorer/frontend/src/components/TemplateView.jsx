/*

In this component we show list of template instances, and when we click on a template, we show the rendered instance next to the list. If no imnstance is selected we show a hint to select one.

*/

import React, {useEffect, useState} from 'react';
import { TemplateDetails } from './TemplateDetails';
import { useLocation, useParams, Navigate } from 'react-router-dom';
import { InstanceView } from './InstanceView';

export const TemplateView = ({endpoint}) => {
    let { templateName, objectID } = useParams();
    const location = useLocation();

    useEffect(() => {
    }, [endpoint, templateName, objectID, location]);

    return (
        <div className='flex flex-row h-screen'>
            <div className='flex-initial p-4' style={{ flexBasis: '24%'}}>
                <TemplateDetails endpoint={endpoint} />
            </div>
            <div className='flex-auto p-4 overflow-auto h-full' style={{minWidth: 0}}>
                { !!!objectID && <p>Select an Instance</p>}
                { objectID && <InstanceView endpoint={endpoint} objectID={objectID} templateName={templateName} /> }
                
            </div>
        </div>
    )
}