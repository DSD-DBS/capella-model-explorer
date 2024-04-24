// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React from "react";

export const TemplateCard = ({ template, onClickCallback }) => (
  <div
    onClick={() => onClickCallback(template.idx)}
    className="m-2 mt-6 max-w-sm cursor-pointer rounded-lg bg-gray-200 shadow-md hover:bg-custom-light dark:bg-custom-dark-2 dark:shadow-dark dark:hover:bg-custom-dark-4"
  >
    <div className="p-5">
      <h5 className="mb-2 text-2xl font-bold text-gray-900 dark:text-gray-100">
        {template.name}
      </h5>
      <p className="mb-3 font-normal text-gray-700 dark:text-gray-300">
        {template.description}
      </p>
    </div>
  </div>
);
