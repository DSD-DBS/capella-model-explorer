// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React from 'react';
import { TemplateCard } from './TemplateCard';

export const ViewsList = ({templates, cardClickCallback}) => {
  let categories = {
    "oa": "Operational Analysis Reports",
    "sa": "System Analysis Reports",
    "la": "Logical Architecture Reports",
    "pa": "Physical Architecture Reports",
    "xc": "Cross-cutting Reports",
    "other": "Other reports"};
  return (
    <div>
      {Object.keys(categories).map(cat => (
        (cat in templates) && (templates[cat].length > 0) && (
        <div key={cat}>
        <h2 key={cat + "h2"} className='text-2xl p-2'>{categories[cat]}</h2>
        <div key={cat + "div"} className='flex flex-wrap justify-center gap-y-2'>
            {templates[cat].map(template => (
              <TemplateCard key={template.idx} template={template} onClickCallback={cardClickCallback} />
            ))}
        </div>
        </div>)
      ))}
    </div>
  );
};
