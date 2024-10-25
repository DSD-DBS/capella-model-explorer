// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import {
  FlaskConical,
  TriangleAlert,
  Book,
  FileStack,
  FileText,
  ShieldCheck
} from 'lucide-react';
import { Badge } from './Badge';

/**
 * TemplateCard shall introduce the template to the user and provide some basic insights:
 * - is this a template of a model element or a document
 * - is it a stable template or an experimental thing / not for production
 * - how many object / document instances this template applies to
 * - indicate if the template is broken / cant enumerate objects / other issues
 * - maybe indicate modeling rules compliance score
 */
export const TemplateCard = ({
  name,
  description,
  idx,
  onClickCallback,
  isDocument = false,
  isExperimental = false,
  isStable = true,
  instanceCount = 0,
  error = false
}) => {
  return (
    <div
      onClick={() => onClickCallback(idx)}
      className="m-2 mt-6 max-w-sm cursor-pointer rounded-lg bg-gray-200
        shadow-md hover:bg-custom-light dark:bg-custom-dark-2 dark:shadow-dark
        dark:hover:bg-custom-dark-4">
      <div className="p-5">
        <div className="flex flex-row justify-between">
          <h5
            className="mb-2 text-left text-2xl font-normal text-gray-900
              dark:text-gray-100"
            style={{ overflowWrap: 'break-word' }}>
            {name}
          </h5>
          {instanceCount === 1 && (
            <span className="ml-4 text-gray-900 dark:text-gray-100">
              <FileText size={16} style={{ display: 'inline-block' }} />
            </span>
          )}
          {instanceCount > 1 && (
            <span className="ml-4 text-gray-900 dark:text-gray-100">
              <FileStack size={16} style={{ display: 'inline-block' }} />{' '}
              {instanceCount}
            </span>
          )}
        </div>
        <p
          className="mb-3 text-left font-normal text-gray-700
            dark:text-gray-300">
          {description}
        </p>
        <div className={'text-left'}>
          {error && (
            <Badge color={'danger'}>
              <TriangleAlert size={16} style={{ display: 'inline-block' }} />{' '}
              {error}
            </Badge>
          )}
          {isStable && (
            <Badge color={'success'}>
              <ShieldCheck size={16} style={{ display: 'inline-block' }} />{' '}
              Stable
            </Badge>
          )}
          {isExperimental && (
            <Badge color={'warning'}>
              <FlaskConical size={16} style={{ display: 'inline-block' }} />{' '}
              Experimental
            </Badge>
          )}
          {isDocument && (
            <Badge>
              <Book size={16} style={{ display: 'inline-block' }} /> Document
            </Badge>
          )}
        </div>
      </div>
    </div>
  );
};
