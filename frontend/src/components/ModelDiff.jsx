// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { API_BASE_URL, ROUTE_PREFIX } from '../APIConfig';
import { useState } from 'react';
import { Spinner } from './Spinner';
import CommitInformation from './CommitInformation';

export const ModelDiff = ({ onRefetch, hasDiffed }) => {
  const [loadingState, setLoadingState] = useState('idle');
  const [commitDetails, setCommitDetails] = useState([]);
  const [selectionOptions, setSelectionOptions] = useState([]);
  const [isPopupVisible, setIsPopupVisible] = useState(false);
  const [selectedDetails, setSelectedDetails] = useState(null);
  const [error, setError] = useState('');
  const [selectedOption, setSelectedOption] = useState('');
  const [isExpanded, setIsExpanded] = useState({
    head: false,
    details: false
  });
  const [diffSuccess, setDiffSuccess] = useState(null);

  const handleSelectChange = (e) => {
    const option = JSON.parse(e.target.value);
    setSelectedOption(e.target.value);
    setSelectedDetails(option);
    setIsExpanded((prev) => ({ ...prev, details: false }));
  };

  const handleGenerateDiff = async () => {
    const headCommit = commitDetails[0]?.hash;
    const selectedCommit = selectedDetails?.hash;

    if (!headCommit || !selectedCommit) {
      alert('Please select a version.');
      return;
    }

    setLoadingState('loading');
    setError('');

    try {
      const response = await postData(`${API_BASE_URL}/compare`, {
        head: headCommit,
        prev: selectedCommit
      });
      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      setDiffSuccess(true);
      setLoadingState('complete');
    } catch (error) {
      setDiffSuccess(false);
      setError(error.message);
      setLoadingState('error');
    } finally {
      onRefetch();
    }
  };

  const postData = async (url, data) => {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (!response.ok) throw new Error('Network response was not ok');
      return response;
    } catch (error) {
      console.error('Error in postData:', error);
      throw error;
    }
  };

  const openModelCompareDialog = async () => {
    try {
      setError('');
      setSelectedOption('');
      setSelectedDetails(null);
      setDiffSuccess(null);
      setLoadingState('idle');

      const response = await fetch(`${API_BASE_URL}/commits`);

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Internal server error.');
      }

      const data = await response.json();
      if (data === null) {
        throw new Error('Not a git repo');
      } else if (data.length < 2) {
        throw new Error('Not enough commits to compare.');
      } else if (data.error) {
        throw new Error('Internal server error: ' + data.error);
      }

      setCommitDetails(data);

      const options = data.map((commit) => ({
        value: JSON.stringify(commit),
        label: `${commit.hash.substring(0, 7)} ${
          commit.tag ? `(${commit.tag})` : ''
        } - ${commit.subject} - Created on ${commit.date.substring(0, 10)}`
      }));

      setSelectionOptions(options);
      setIsPopupVisible(true);
    } catch (err) {
      alert(err.message || 'An error occurred while fetching commits.');
    }
  };

  const closeModelCompareDialog = () => {
    setIsPopupVisible(false);
    setLoadingState('idle');
    setSelectedOption('');
    setSelectedDetails(null);
  };

  const toggleExpand = (section) => {
    setIsExpanded((prev) => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  return (
    <div className="mb-2 mt-2 flex flex-col items-center">
      <button
        className="rounded border border-black bg-gray-200 px-4 py-2
          text-gray-700 hover:bg-custom-light dark:bg-custom-dark-2
          dark:text-gray-100 dark:hover:bg-custom-dark-4"
        onClick={openModelCompareDialog}>
        {hasDiffed
          ? 'Compare with another version'
          : 'Compare with previous version'}
      </button>
      {isPopupVisible && (
        <div>
          <div
            className="fixed inset-0 z-10 bg-black bg-opacity-50"
            onClick={
              loadingState !== 'loading' ? closeModelCompareDialog : null
            }></div>
          <div
            className="absolute left-1/2 top-1/2 z-20 w-1/2 min-w-0
              -translate-x-1/2 -translate-y-1/2 transform overflow-y-auto
              rounded bg-gray-100 p-4 shadow-lg dark:bg-custom-dark-2
              dark:text-gray-100"
            style={{ maxHeight: '75%' }}
            onClick={(e) => e.stopPropagation()}>
            <div className="flex flex-col space-y-8 break-words text-lg">
              <div>
                <select
                  className="mb-2 w-full cursor-not-allowed bg-gray-300
                    text-gray-500 dark:bg-custom-dark-3 dark:text-gray-100"
                  disabled>
                  <option>{selectionOptions[0]?.label}</option>
                </select>

                <CommitInformation
                  commitDetails={commitDetails[0]}
                  isExpanded={isExpanded.head}
                  toggleExpand={toggleExpand}
                  section="head"
                />

                <select
                  className="mb-2 mt-2 w-full bg-gray-200 dark:bg-custom-dark-3
                    dark:text-gray-100"
                  value={selectedOption}
                  onChange={handleSelectChange}
                  disabled={loadingState === 'loading'}>
                  <option disabled value="">
                    Select Commit:
                  </option>
                  {selectionOptions.slice(1).map((option) => (
                    <option
                      key={option.value}
                      value={option.value}
                      className="font-mono">
                      {option.label}
                    </option>
                  ))}
                </select>

                {selectedDetails && (
                  <CommitInformation
                    commitDetails={selectedDetails}
                    isExpanded={isExpanded.details}
                    toggleExpand={toggleExpand}
                    section="details"
                  />
                )}
                <div className="mb-4 mt-4 flex items-center justify-center">
                  {loadingState === 'loading' && <Spinner />}
                </div>
                <div className="flex flex-col">
                  {loadingState === 'loading' && (
                    <div
                      className="mt-4 rounded border border-blue-400
                        bg-blue-100 p-4 text-blue-700">
                      <strong>Comparing versions...</strong>
                    </div>
                  )}
                  {loadingState === 'complete' && diffSuccess && (
                    <>
                      <div
                        className="mt-4 rounded border border-green-400
                          bg-green-100 p-4 text-green-700">
                        Successfully compared versions ✓
                      </div>
                      <button
                        className="mt-4 rounded bg-green-500 px-4 py-2
                          text-white hover:bg-green-600"
                        onClick={() =>
                          window.open(
                            `${ROUTE_PREFIX}/model-comparison`,
                            '_blank'
                          )
                        }>
                        View model comparison
                      </button>
                      <button
                        className="mt-4 rounded bg-custom-blue px-4 py-2
                          text-white hover:bg-custom-blue-hover"
                        onClick={handleGenerateDiff}>
                        Compare to a different version
                      </button>
                    </>
                  )}
                  {loadingState === 'error' && (
                    <>
                      <div
                        className={`mt-4 rounded border p-4 ${
                        error === 'No model changes to show'
                            ? 'border-yellow-400 bg-yellow-100 text-yellow-700'
                            : 'border-red-400 bg-red-100 text-red-700'
                        }`}>
                        {error !== 'No model changes to show' && (
                          <strong>Error:</strong>
                        )}{' '}
                        {error}
                      </div>
                      <button
                        className="mt-4 rounded bg-custom-blue px-4 py-2
                          text-white hover:bg-custom-blue-hover"
                        onClick={() => {
                          setError('');
                          handleGenerateDiff();
                        }}>
                        Compare to a different version
                      </button>
                    </>
                  )}
                  {loadingState === 'idle' && (
                    <button
                      className="mt-4 rounded bg-custom-blue px-4 py-2
                        text-white hover:bg-custom-blue-hover"
                      onClick={handleGenerateDiff}
                      disabled={loadingState === 'loading'}>
                      Compare versions
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
