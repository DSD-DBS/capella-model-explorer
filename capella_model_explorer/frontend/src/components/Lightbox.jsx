import React, {useEffect} from "react";

export const Lightbox = ({imageSource, onClose}) => {
    useEffect(() => {
        const handleEscape = (event) => {
            if (event.key === 'Escape') {
                onClose();
            }
        };
        document.addEventListener('keydown', handleEscape);
        return () => document.removeEventListener('keydown', handleEscape);
    }, [onClose]);

    return (
        <div onClick={onClose}
         className='fixed inset-0 z-50 flex justify-center items-center bg-black bg-opacity-50'>
            <div style={{ maxWidth: '100%'}}>
                {imageSource && <div dangerouslySetInnerHTML={{__html: imageSource}}></div>}
            </div>
        </div>
    );
}