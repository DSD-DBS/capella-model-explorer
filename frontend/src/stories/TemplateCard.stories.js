/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TemplateCard } from '../components/TemplateCard';

export default {
  title: 'Example/TemplateCard',
  component: TemplateCard,
  tags: ['autodocs'],
  // This component will have an automatically generated Autodocs entry:
  //  https://storybook.js.org/docs/writing-docs/autodocs
  parameters: {
    // More on how to position stories at:
    //  https://storybook.js.org/docs/configure/story-layout
    layout: 'fullscreen'
  }
};

export const ExperimentalDocument = {
  args: {
    name: 'System Capability',
    description: `Specifies what the system should be capable of
      and how it needs to interact with external actors.`,
    idx: 'THE IDENTIFIER',
    isDocument: true,
    isExperimental: true,
    instances: 0,
    isBroken: false,
    onClickCallback: (idx) => alert(idx)
  }
};

export const Draft = {
  args: {
    name: 'System Capability',
    description: `Specifies what the system should be capable of
      and how it needs to interact with external actors.`,
    idx: 'THE IDENTIFIER',
    instances: 42,
    isExperimental: true,
    onClickCallback: (idx) => alert(idx)
  }
};

export const Broken = {
  args: {
    name: 'System Capability',
    description: `Specifies what the system should be capable of
      and how it needs to interact with external actors.`,
    idx: 'THE IDENTIFIER',
    isBroken: true,
    onClickCallback: (idx) => alert(idx)
  }
};
