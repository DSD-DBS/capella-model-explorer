import React from 'react';
import { TemplateCard } from './TemplateCard';

export const TemplatesList = ({templates}) => (
    <div className='flex flex-wrap justify-center items-center'>
        {templates.map(template => (
          <TemplateCard name={template.name} description={template.description} />  
        ))}
    </div>
    );
