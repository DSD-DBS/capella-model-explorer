/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TemplatesList } from '../components/viewsList';

export default {
  title: 'Example/viewsList',
  component: TemplatesList,
  // This component will have an automatically generated Autodocs
  // entry: https://storybook.js.org/docs/writing-docs/autodocs
  tags: ['autodocs'],
  parameters: {
    // More on how to position stories at:
    //  https://storybook.js.org/docs/configure/story-layout
    layout: 'fullscreen'
  }
};

export const Demo = {
  args: {
    templates: [
      {
        name: 'System Capability',
        description: `Specifies what the system should be capable of
        and how it needs to interact with external actors.`,
        idx: 1
      },
      {
        name: 'System Function',
        description: 'Specifies how the system or actor shall behave.',
        idx: 2
      }
    ],
    cardClickCallback: (idx) => alert(idx)
  }
};
