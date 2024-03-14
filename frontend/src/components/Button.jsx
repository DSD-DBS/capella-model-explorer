import React from 'react';

export const Button = ({ theme, children, ...props }) => {
  const buttonClass = theme === 'dark' ? 'bg-black text-white' : 'bg-white text-black';

  return (
    <a href="#" {...props} class="rounded-md bg-blue-800 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ">
        {children}
    </a>
  );
};
