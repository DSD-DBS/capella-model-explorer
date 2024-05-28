/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ObjectList } from '../components/ObjectList';

export default {
  title: 'Example/ObjectList',
  component: ObjectList,
  // This component will have an automatically generated Autodocs entry:
  //  https://storybook.js.org/docs/writing-docs/autodocs
  tags: ['autodocs'],
  parameters: {
    // More on how to position stories at:
    //  https://storybook.js.org/docs/configure/story-layout
    layout: 'fullscreen'
  }
};

export const Capabilities = {
  args: {
    objects: [
      { name: 'Brew Coffee', uuid: '9876' },
      { name: 'Steam Milk', uuid: '5432' },
      { name: 'Grind Beans', uuid: 'efgh' },
      { name: 'Clean Machine', uuid: 'mnop' },
      { name: 'Adjust Settings', uuid: 'qrst' }
    ]
  }
};
