import React from 'react';
import { TemplateCard } from './TemplateCard';

export const ViewsList = ({templates, cardClickCallback}) => (
    <div className='flex flex-wrap justify-center items-center'>
        {templates.map(template => (
          <TemplateCard key={template.idx} template={template} onClickCallback={cardClickCallback} />  
        ))}
    </div>
    );
