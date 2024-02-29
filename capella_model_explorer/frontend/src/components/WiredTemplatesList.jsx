import React, {useState, useEffect} from 'react';
import { useNavigate } from 'react-router-dom';
import { TemplatesList } from './TemplatesList';


export const WiredTemplatesList = ({endpoint}) => {
    const [templates, setTemplates] = useState([])
    const navigate = useNavigate();

    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                const response = await fetch(endpoint, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                });
                const data = await response.json();
                setTemplates(data);
            }
            catch (error) {}
            finally {}
        };
        fetchTemplates();
    }, [endpoint]);

    return <TemplatesList templates={templates} cardClickCallback={(idx) => navigate(`/templates/${idx}`, {state: {idx: idx}})} />;}