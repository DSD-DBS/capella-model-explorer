// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { API_BASE_URL } from '../APIConfig';
import React, { useState } from 'react';
import { Spinner } from './Spinner';

export const ModelDiff = ({ onRefetch, hasDiffed }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [completeLoading, setCompleteLoading] = useState(false);
  const [commitDetails, setCommitDetails] = useState({});
  const [selectionOptions, setSelectionOptions] = useState([]);
  const [isPopupVisible, setIsPopupVisible] = useState(false);
  const [selectedDetails, setSelectedDetails] = useState('');
  const [error, setError] = useState('');
  const [selectedOption, setSelectedOption] = useState('');

  const handleSelectChange = (e) => {
    const option = e.target.value;
    setSelectedOption(option);
    const selectedValue = JSON.parse(e.target.value);
    setSelectedDetails(selectedValue);
  };

  const handleGenerateDiff = async () => {
    if (!commitDetails[0].hash || !selectedDetails.hash) {
      alert('Please select a version.');
      return;
    }
    setCompleteLoading(false);
    setIsLoading(true);
    try {
      const url = new URL(API_BASE_URL + '/compare');
      const response = await postData(url, {
        head: commitDetails[0].hash,
        prev: selectedDetails.hash
      });
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
      setCompleteLoading(true);
      onRefetch();
    }
  };

  const postData = async (url = '', data = {}) => {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response;
    } catch (error) {
      console.error('Error in postData:', error);
      throw error;
    }
  };

  async function openModelCompareDialog() {
    try {
      const response = await fetch(API_BASE_URL + '/commits');
      if (!response.ok) {
        throw new Error(
          'Failed to fetch commits info: ' + response.statusText
        );
      }
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      setCommitDetails(data);
      const options = data.map((commit) => ({
        value: JSON.stringify(commit),
        label: `${commit.tag} - ${commit.hash.substring(0, 7)} - Created on ${commit.date.substring(0, 10)}`
      }));

      setSelectionOptions(options);
      setIsPopupVisible(true);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="mb-2 mt-2 flex flex-col items-center">
      <button
        className="rounded border border-black bg-gray-200 px-4 py-2
         text-gray-700 hover:bg-custom-light dark:bg-custom-dark-2 dark:text-gray-100 dark:hover:bg-custom-dark-4"
        onClick={openModelCompareDialog}>
        {hasDiffed
          ? 'Compare with another version'
          : 'Compare with previous version'}
      </button>
      {isPopupVisible && (
        <div>
          <div
            className="fixed inset-0 z-10 bg-black bg-opacity-50"
            onClick={() => {
              if (!isLoading) {
                setIsPopupVisible(false);
                setCompleteLoading(false);
              }
            }}></div>
          <div
            className="absolute left-1/2 top-1/2 z-20 w-1/2 min-w-0
            -translate-x-1/2 -translate-y-1/2 transform overflow-y-auto rounded bg-gray-100
            p-4 shadow-lg dark:bg-custom-dark-2 dark:text-gray-100"
            style={{ maxHeight: '66.6%' }}
            onClick={(e) => e.stopPropagation()}>
            <div className="flex flex-col space-y-8 break-words text-lg">
              <div>
                {error ? (
                  <div>
                    <p className="font-semibald text-red-500">
                      Cannot generate model diff: {error}
                    </p>
                    <p>
                      Select 'Deep clone' before running the session or run
                      model within git repo.
                    </p>
                  </div>
                ) : (
                  <>
                    <select
                      className="mb-2 w-full cursor-not-allowed bg-gray-300 text-gray-500
                      dark:bg-custom-dark-3 dark:text-gray-100"
                      disabled>
                      <option>{selectionOptions[0].label}</option>
                    </select>
                    <div className="text-left font-semibold">
                      <p>Hash: {commitDetails[0].hash}</p>
                      {commitDetails[0].tag && (
                        <p>Tag: {commitDetails[0].tag}</p>
                      )}
                      <p>Author: {commitDetails[0].author}</p>
                      <p>Description: {commitDetails[0].description}</p>
                      <p>Date: {commitDetails[0].date}</p>
                    </div>
                    <select
                      className="mb-2 mt-2 w-full bg-gray-200 dark:bg-custom-dark-3 dark:text-gray-100"
                      value={selectedOption}
                      onChange={handleSelectChange}
                      disabled={isLoading}>
                      <option disabled value="">
                        Select Commit:
                      </option>
                      {selectionOptions.slice(1).map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                    {selectedDetails && (
                      <div className="text-left">
                        <p>Hash: {selectedDetails.hash}</p>
                        {selectedDetails.tag && (
                          <p>Tag: {selectedDetails.tag}</p>
                        )}
                        <p>Author: {selectedDetails.author}</p>
                        <p>Description: {selectedDetails.description}</p>
                        <p>Date: {selectedDetails.date.substring(0, 10)}</p>
                      </div>
                    )}
                    {isLoading && (
                      <div className="mb-8 mt-8">
                        <Spinner />
                      </div>
                    )}
                    <div className="flex flex-col">
                      <button
                        className={`
                        mt-4 rounded px-4 py-2 text-white
                        ${
                          isLoading
                            ? 'bg-gray-500 '
                            : completeLoading
                              ? 'bg-green-500'
                              : 'bg-custom-blue hover:bg-custom-blue-hover'
                        }`}
                        onClick={handleGenerateDiff}
                        disabled={isLoading || completeLoading}>
                        {isLoading ? (
                          'Comparing versions...'
                        ) : completeLoading ? (
                          <span>Versions compared successfully &#10003;</span>
                        ) : (
                          'Compare versions'
                        )}
                      </button>
                      {completeLoading && (
                        <button
                          className="mt-4 rounded bg-custom-blue px-4 py-2 text-white hover:bg-custom-blue-hover"
                          onClick={() => {
                            window.open('/model-comparison', '_blank');
                          }}>
                          View model comparison
                        </button>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
