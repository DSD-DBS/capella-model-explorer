// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

const CommitInformation = ({
  commitDetails,
  isExpanded,
  toggleExpand,
  section
}) => {
  return (
    <div className="text-left">
      <p>
        <span className="font-semibold">Hash:</span> {commitDetails.hash}
      </p>
      {commitDetails.tag && (
        <p>
          <span className="font-semibold">Tag:</span> {commitDetails.tag}
        </p>
      )}
      <p>
        <span className="font-semibold">Author:</span> {commitDetails.author}
      </p>
      <p style={{ whiteSpace: 'pre-wrap' }}>
        <span className="font-semibold">Description:</span>{' '}
        {isExpanded
          ? commitDetails.description
          : `${commitDetails.description.split('\n')[0]}${
              commitDetails.description.includes('\n') ? '' : ''
            }`}
      </p>
      {commitDetails.description.includes('\n') && (
        <button
          className="mb-4 mt-2 font-normal text-custom-blue
            hover:text-custom-blue-hover"
          onClick={() => toggleExpand(section)}>
          {isExpanded ? 'Show Less' : 'Show Full Description'}
        </button>
      )}
      <p>
        <span className="font-semibold">Date:</span> {commitDetails.date}
      </p>
    </div>
  );
};

export default CommitInformation;
