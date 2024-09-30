// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { TemplateCard } from './TemplateCard';

export const ViewsList = ({ templates, cardClickCallback }) => {
  let categories = {
    oa: 'Operational Analysis Reports',
    sa: 'System Analysis Reports',
    la: 'Logical Architecture Reports',
    pa: 'Physical Architecture Reports',
    xc: 'Cross-cutting Reports',
    other: 'Other reports'
  };

  return (
    <div
      className="rounded-lg bg-gray-100 pb-2 pl-4 pr-4 pt-8 shadow-lg
        dark:bg-custom-dark-3">
      {Object.keys(categories).map((cat) => {
        if (cat in templates && templates[cat].length > 0) {
          return (
            <div key={cat} className="mb-8 p-4">
              <h2
                className="border-b border-gray-900 pb-2 text-2xl font-bold
                  dark:border-gray-300">
                <span className="px-4 py-2 text-gray-900 dark:text-gray-100">
                  {categories[cat]}
                </span>
              </h2>
              <div
                className="mt-2 block gap-4 md:flex md:flex-wrap
                  md:justify-center">
                {templates[cat].map((template) => (
                  <TemplateCard
                    key={template.idx}
                    {...template}
                    onClickCallback={cardClickCallback}
                  />
                ))}
              </div>
            </div>
          );
        }
        return null;
      })}
    </div>
  );
};
