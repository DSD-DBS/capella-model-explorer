import React from 'react';

export const Card = ({children, onClick}) => (
    <div onClick={onClick}
    className='max-w-sm bg-white rounded-lg border border-gray-200 shadow-md m-4 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 dark:bg-gray-800 dark:border-gray-700'>
        {children}
    </div>
    );
