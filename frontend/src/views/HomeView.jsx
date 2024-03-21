import React, { useState, useEffect } from 'react';
import {WiredTemplatesList} from '../components/WiredTemplatesList';
import { API_BASE_URL } from '../APIConfig';

export const HomeView = () => {
    const [modelInfo, setModelInfo] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchModelInfo = async () => {
            try {
                const response = await fetch(API_BASE_URL + '/model-info');
                const data = await response.json();
                setModelInfo(data);
                console.log(data);
            } catch (err) {
                setError('Failed to fetch model info: ' + err.message);
            }
        };

        fetchModelInfo();
    }, []);

    if (error) {
        return (<div className='bg-red-500 text-white text-xl p-2 rounded'>{error}</div>);
    }

    return (
        <div className="flex flex-col justify-center h-full">
            <div className="mb-4  mx-auto text-center">
                {modelInfo && (
                    <div className='bg-white dark:bg-gray-900 text-gray-700 dark:text-white'>
                        <h2 className='text-xl'>{modelInfo.title}</h2>
                        {modelInfo.capella_version && <p>Capella Version: {modelInfo.capella_version}</p>}
                        {modelInfo.revision && <p>Revision: {modelInfo.revision}</p>}
                        {modelInfo.branch && <p>Branch: {modelInfo.branch}</p>}
                        {modelInfo.hash && <p>Commit Hash: {modelInfo.hash}</p>}
                        <div dangerouslySetInnerHTML={{ __html: modelInfo.badge }}></div>
                    </div>
                )}
            </div>
            <div>
                <WiredTemplatesList />
            </div>
        </div>
    );
};
