import React, {useState, useEffect} from 'react';
import { TemplatesList } from './TemplatesList';


export const WiredTemplatesList = ({templates_endpoint}) => {
    const [templates, setTemplates] = useState([])

    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                const response = await fetch(templates_endpoint, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        // set no-cors mode to avoid CORS issues
                        'mode': 'no-cors',
                    },
                });
                const data = await response.json();
                setTemplates(data);
                console.log(data);
            }
            catch (error) {}
            finally {}
        };
        fetchTemplates();
    }, [templates_endpoint]);

    return <TemplatesList templates={templates} />;}