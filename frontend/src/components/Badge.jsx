// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

const color_classes = {
  default: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  danger: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
  success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  warning:
    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
};
/*
 * provides a badge that may have different colors
 */
export const Badge = ({ children, color = 'default' }) => (
  <div
    className={
      'me-2 inline-block rounded-full px-2.5 py-1 text-xs font-medium ' +
      color_classes[color]
    }>
    {children}
  </div>
);
