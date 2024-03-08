import React from 'react';
import { WiredTemplatesList } from '../components/WiredTemplatesList';

export default {
    title: 'Example/WiredTemplatesList',
    component: WiredTemplatesList,
    // This component will have an automatically generated Autodocs entry: https://storybook.js.org/docs/writing-docs/autodocs
    tags: ['autodocs'],
    parameters: {
        // More on how to position stories at: https://storybook.js.org/docs/configure/story-layout
        layout: 'fullscreen',
    },

};

export const GoodEndpoint = {
    args: {
        templates_endpoint: "http://localhost:8000/api/templates"
    },
};

export const WrongEndpoint = {
    args: {
        templates_endpoint: "http://google.com"
    },
};

export const NoEndpoint = {
};
