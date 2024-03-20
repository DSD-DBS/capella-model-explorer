import React from 'react';

export const TemplateCard = ({template, onClickCallback}) => (
    <div onClick={() => onClickCallback(template.idx)}
        className='max-w-sm bg-white rounded-lg border border-gray-200 shadow-md m-2 cursor-pointer hover:bg-gray-100'>
        <div className='p-5'>
            <h5 className='mb-2 text-2xl font-bold text-gray-900'>
                {template.name}
            </h5>
            <p className='mb-3 font-normal text-gray-700'>{template.description}</p>
        </div>
    </div>
    );
