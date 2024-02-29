import React from 'react';

export const TemplateCard = ({name, description}) => (
    <div className='max-w-sm bg-white rounded-lg border border-gray-200 shadow-md m-4'>
        <div className='p-5'>
            <h5 className='mb-2 text-2xl font-bold text-gray-900'>
                {name}
            </h5>
            <p className='mb-3 font-normal text-gray-700'>{description}</p>
        </div>
    </div>
    );
