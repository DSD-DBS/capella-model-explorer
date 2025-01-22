/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: CC0-1.0
 */

module.exports = {
  plugins: [
    require.resolve('prettier-plugin-tailwindcss'),
    require.resolve('prettier-plugin-classnames'),
    require.resolve('prettier-plugin-merge')
  ],
  semi: true,
  tabWidth: 2,
  printWidth: 79,
  singleQuote: true,
  trailingComma: 'none',
  bracketSameLine: true,
  endOfLine: 'lf',
  useTabs: false,
  endingPosition: 'absolute-with-indent'
};
