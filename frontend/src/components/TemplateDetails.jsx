import React, {useEffect, useState} from 'react';
import { useParams } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { Card } from './Card';

export const TemplateDetails = ({endpoint}) => {
    let { templateName, objectID } = useParams();
    const [error, setError] = useState(null);
    const [details, setDetails] = useState([]);
    const navigate = useNavigate();
    const [filterText, setFilterText] = useState('');

    useEffect(() => {
        const fetchDetails = async () => {
            try {
                const response = await fetch(endpoint + templateName, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                });
                const data = await response.json();
                setDetails(data);
            }
            catch (error) {
                setError(error.message);
            }
            finally {}
        };
        fetchDetails(); 
    }, [endpoint, templateName, objectID]);
    if (error) {
        return (
        <div className='bg-red-500 text-white p-4 rounded text-2xl'>
            {error}
        </div>
        )
    }
    return (
    <div className='flex flex-col h-full'>
        <h5 className='mb-2 text-2xl font-bold text-gray-900 dark:text-white'>
                {details.name}
        </h5>
        <p className='mb-3 font-normal text-gray-700 dark:text-white'>{details.description}</p>
    {details.error ? (
        <div>
            <p>We failed to find matching template instances due to the following error: </p>
        <div className='bg-red-500 py-2 px-2 text-white rounded'>
            {details.error}
        </div>
        </div>
    ) : (
        <>
            <input
                type="text"
                value={filterText}
                onChange={(e) => setFilterText(e.target.value)}
                placeholder="Filter objects"
                className="mb-3 p-2 border rounded"
            />
            <div className='flex flex-wrap justify-center items-center overflow-auto'>
    {details.objects && details.objects.length === 0 ? (
        <p>No objects found</p>
    ) : (
        details.objects && details.objects.filter(object => object.name.toLowerCase().includes(filterText.toLowerCase())).map(object => (
            <div key={object.idx}
                onClick={() => {navigate(`/${templateName}/${object.idx}`);}}
                className={(objectID && object.idx === objectID ? 'bg-blue-800 dark:bg-blue-800 text-white hover:dark:text-white hover:text-blue-800' : 'text-gray-900') + ' max-w-sm rounded-lg border border-gray-200 shadow-md m-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 dark:border-gray-700'}
            >
                <div className='p-2'>
                    <h5 className={'text-md font-bold dark:text-white ' + (objectID && object.idx === objectID ? '' : '')}>
                        {object.name}
                    </h5>
                </div>
            </div>
        ))
    )}
</div>
        </>
    )}
        
    </div>
    );}
