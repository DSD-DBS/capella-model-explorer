// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React from 'react';

export const Button = ({ theme, children, ...props }) => {
  return (
    <a href="#" {...props} className="print:hidden rounded-md mx-1 bg-blue-800 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 hover:text-gray-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ">
        {children}
    </a>
  );
};