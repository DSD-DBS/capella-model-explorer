// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

export const Card = ({ children, onClick }) => (
  <div
    onClick={onClick}
    className="m-2 max-w-sm cursor-pointer rounded-lg border border-gray-200
      bg-white shadow-md hover:bg-gray-100 dark:border-gray-700
      dark:bg-gray-800 dark:shadow-dark dark:hover:bg-gray-700">
    {children}
  </div>
);
