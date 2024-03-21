import React, {useState, useEffect} from 'react';
import { useNavigate } from 'react-router-dom';
import { ViewsList } from './ViewsList';


export const WiredTemplatesList = ({endpoint}) => {
    const [templates, setTemplates] = useState([])
    const [error, setError] = useState(null);
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
            catch (error) {
                setError(error.message)
            }
            finally {}
        };
        fetchTemplates();
    }, [endpoint]);

    if (error) {
        return (
        <div className='bg-red-500 text-white p-4 rounded text-2xl'>
            {error === 'Failed to fetch' ? 
            "Can't connect to the server. Maybe your session was inactive for too long? if that's the case, request a new session / restart the app." 
            : 
            error
            }   
        </div>);
    }
    return <ViewsList templates={templates} cardClickCallback={(idx) => navigate(`/views/${idx}`, {state: {idx: idx}})} />;}