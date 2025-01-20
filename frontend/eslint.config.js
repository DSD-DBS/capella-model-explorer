/*
 * Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import globals from 'globals';
import pluginJs from '@eslint/js';
import pluginReact from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import eslintConfigPrettier from 'eslint-config-prettier';

/** @type {import('eslint').Linter.Config[]} */
export default [
  { files: ['**/*.{js,mjs,cjs,jsx}'] },
  { languageOptions: { globals: globals.browser } },
  pluginJs.configs.recommended,
  pluginReact.configs.flat.recommended,
  pluginReact.configs.flat['jsx-runtime'],
  {
    rules: {
      'react/jsx-no-target-blank': 'off',
      'react/prop-types': 'off',
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true }
      ],
      'max-len': [
        'error',
        { code: 100, ignoreUrls: true, ignoreStrings: true }
      ]
    }
  },
  reactRefresh.configs.recommended,
  // TODO: Simplify when https://github.com/facebook/react/issues/28313 is released
  {
    plugins: {
      'react-hooks': reactHooks
    },
    rules: { ...reactHooks.configs.recommended.rules }
  },
  eslintConfigPrettier
];
