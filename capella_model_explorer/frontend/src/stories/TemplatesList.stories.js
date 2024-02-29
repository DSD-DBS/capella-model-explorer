import React from 'react';
import { TemplatesList } from '../components/TemplatesList';


export default {
    title: 'Example/TemplatesList',
    component: TemplatesList,
    // This component will have an automatically generated Autodocs entry: https://storybook.js.org/docs/writing-docs/autodocs
    tags: ['autodocs'],
    parameters: {
        // More on how to position stories at: https://storybook.js.org/docs/configure/story-layout
        layout: 'fullscreen',
    },

};

export const Demo = {
    args: {
        templates: [
            {
                name: "System Capability",
                description: "Specifies what the system should be capable of and how it needs to interact with external actors."    
            },
            {
                name: "System Function",
                description: "Specifies how the system or actor shall behave."    
            }
        ]
    },
};

