/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import {TemplateCard} from '../components/TemplateCard';

export default {
    title: 'Example/TemplateCard',
    component: TemplateCard,
    // This component will have an automatically generated Autodocs entry: https://storybook.js.org/docs/writing-docs/autodocs
    tags: ['autodocs'],
    parameters: {
        // More on how to position stories at: https://storybook.js.org/docs/configure/story-layout
        layout: 'fullscreen',
    },

};

export const Demo = {
    args: {
        template: {
            name: "System Capability",
            description: "Specifies what the system should be capable of and how it needs to interact with external actors.",
            idx: "THE IDENTIFIER"
        },
        onClickCallback: (idx) => alert(idx)
    },
};
