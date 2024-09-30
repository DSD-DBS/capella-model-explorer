// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

export const Button = ({ children, ...props }) => {
  return (
    <a
      href="#"
      {...props}
      className="mx-1 rounded-md bg-custom-blue px-2.5 py-1.5 text-sm
        font-semibold text-white shadow-sm hover:bg-custom-blue-hover
        hover:text-gray-50 focus-visible:outline focus-visible:outline-2
        focus-visible:outline-offset-2 dark:shadow-dark print:hidden">
      {children}
    </a>
  );
};
