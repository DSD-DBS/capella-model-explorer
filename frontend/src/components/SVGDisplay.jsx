// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useState, useEffect } from 'react';
import { Lightbox } from './Lightbox';

export const SVGDisplay = ({ content }) => {
  const [showLightbox, setShowLightbox] = useState(false);

  useEffect(() => {
    if (showLightbox) {
      document.body.classList.add('svg-visible');
      document.body.classList.remove('svg-hidden');
    } else {
      document.body.classList.add('svg-hidden');
      document.body.classList.remove('svg-visible');
    }
  }, [showLightbox]);

  const handleSvgClick = () => {
    setShowLightbox(true);
  };

  return (
    <>
      <div
        className="svg-display group relative"
        style={{ maxWidth: '100%', height: 'auto' }}
        onClick={handleSvgClick}>
        <div
          className="absolute inset-0 flex cursor-pointer items-center
            justify-center rounded bg-black bg-opacity-0 duration-200
            group-hover:bg-opacity-50"
          style={{ pointerEvents: 'none' }}>
          <div
            className="text-2xl font-bold text-transparent
              group-hover:text-white">
            Click to enlarge
          </div>
        </div>
        {content && <div dangerouslySetInnerHTML={{ __html: content }}></div>}
      </div>
      {showLightbox && (
        <Lightbox
          onClose={() => setShowLightbox(false)}
          imageSource={content}
        />
      )}
    </>
  );
};
