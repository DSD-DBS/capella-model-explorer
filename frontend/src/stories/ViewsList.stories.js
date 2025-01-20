/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ViewsList } from '../components/ViewsList';

export default {
  title: 'Example/ViewsList',
  component: ViewsList,
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
    templates: {
      xc: [
        {
          idx: 'class',
          name: 'Data Class',
          template: 'cross-cutting/classes.html.j2',
          description:
            'Specifies structure of a data class. A class may be used to describe anything from a simple object relationship to a message on a bus.',
          scope: {
            type: 'Class',
            below: null,
            filters: {}
          },
          single: null,
          isStable: null,
          isDocument: null,
          isExperimental: null,
          error: null,
          traceback: null,
          instanceCount: 34,
          instanceList: null
        },
        {
          idx: 'diagram',
          name: 'Diagrams',
          template: 'cross-cutting/diagrams.html.j2',
          description:
            'Provides access to all human-made diagrams inside the model',
          scope: {
            type: 'DRepresentationDescriptor',
            below: null,
            filters: {}
          },
          single: null,
          isStable: null,
          isDocument: null,
          isExperimental: null,
          error: null,
          traceback: null,
          instanceCount: 112,
          instanceList: null
        }
      ],
      la: [
        {
          idx: 'logical-component',
          name: 'Logical Components',
          template: 'logical-architecture/logical-component.html.j2',
          description:
            'Specifies a logical component. This is a ported template from a prototype project.',
          scope: {
            type: 'LogicalComponent',
            below: 'la',
            filters: {}
          },
          single: null,
          isStable: null,
          isDocument: null,
          isExperimental: true,
          error: null,
          traceback: null,
          instanceCount: 23,
          instanceList: null
        }
      ]
    },
    cardClickCallback: (idx) => alert(idx)
  }
};
