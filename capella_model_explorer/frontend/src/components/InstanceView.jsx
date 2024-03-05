import React, {useEffect, useState} from 'react';
import { useParams } from 'react-router-dom';
import { Spinner } from './Spinner';
import { SVGDisplay } from './SVGDisplay';


export const InstanceView = ({endpoint}) => {
    let { templateName, objectID } = useParams();
    const [details, setDetails] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const url = endpoint + `${templateName}/${objectID}`;
        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'text/html'
            }
        })
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const contentItems = [];
            doc.body.childNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    if (node.tagName === 'svg') {
                        contentItems.push({type: "SVGDisplay", content: node.outerHTML});
                    } else {
                        contentItems.push({type: "HTML", content: node.outerHTML});
                    }
                }
            });
            setDetails(contentItems);
            setLoading(false);
        })
        .catch((error) => {
            setLoading(false);
            setDetails("Error fetching data ", error);
        });
    }, [endpoint]);
    if (loading) return (<div><Spinner />;</div>)
    return (
    <div className='html-content bg-white shadow-lg mx-auto my-8 p-8 w-[210mm] max-w-full overflow-auto print:shadow-none print:m-0 print:p-0 print:bg-transparent'>
        {details.map((item, idx) => {
            if (item.type === "SVGDisplay") {
                return (
                    <SVGDisplay key={idx} content={item.content} />
                );
            } else {
                return (
                    <div key={idx} dangerouslySetInnerHTML={{__html: item.content}} />
                );
            }
        })}
    </div>
    );}