import React, {useEffect, useState} from 'react';
import { useParams } from 'react-router-dom';


export const InstanceView = ({endpoint}) => {
    let { templateName, objectID } = useParams();
    const [details, setDetails] = useState([]);

    useEffect(() => {
        const fetchDetails = async () => {
            try {
                const url = endpoint + `${templateName}/${objectID}`;
                console.log(url);
                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'text/html'
                    },
                });
                const data = await response.text();
                setDetails(data);
            }
            catch (error) {}
            finally {}
        };
        fetchDetails();
    }, [endpoint]);

    return (
    <div dangerouslySetInnerHTML={{__html: details}}>

    </div>
    );}