import React, {useEffect, useState} from 'react';
import { useLocation } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { Card } from './Card';

export const TemplateDetails = ({endpoint}) => {
    const location = useLocation();
    const template_id = location.state.idx;
    const [details, setDetails] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchDetails = async () => {
            try {
                const response = await fetch(endpoint + template_id, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                });
                const data = await response.json();
                setDetails(data);
            }
            catch (error) {}
            finally {}
        };
        fetchDetails();
    }, [endpoint]);
    
    return (
    <div>
        <div className='p-5'>
            <h5 className='mb-2 text-2xl font-bold text-gray-900 dark:text-white'>
                {details.name}
            </h5>
            <p className='mb-3 font-normal text-gray-700 dark:text-white'>{details.description}</p>
        </div>
        <div className='flex flex-wrap justify-center items-center'>
            {details.objects && details.objects.length === 0 && <p>No objects found</p>}
            {details.objects && details.objects.length > 0 && details.objects.map(object => (
                <Card key={object.idx}
                    onClick={() => navigate(`/templates/${template_id}/${object.idx}`)}
                >
                    <div className='p-4'>
                        <h5 className='text-lg font-bold text-gray-900 dark:text-white'>
                            {object.name}
                        </h5>
                    </div>
                </Card>
            ))}
        </div>
    </div>
    );}
