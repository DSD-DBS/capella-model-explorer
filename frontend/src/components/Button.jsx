import React from 'react';

export const Button = ({ theme, children, ...props }) => {
  return (
    <a href="#" {...props} className="rounded-md mx-1 bg-blue-800 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ">
        {children}
    </a>
  );
};
