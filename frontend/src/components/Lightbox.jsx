// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { Printer, XIcon } from 'lucide-react';
import { useEffect, useState } from 'react';
import { TransformComponent, TransformWrapper } from 'react-zoom-pan-pinch';
import { LightboxButton } from './LightboxButton';

export const Lightbox = ({ onClose, imageSource }) => {
  const [isClicked, setIsClicked] = useState(false);

  useEffect(() => {
    const revertCursor = () => {
      setIsClicked(false);
      window.removeEventListener('mouseup', revertCursor);
    };
    if (isClicked) {
      window.addEventListener('mouseup', revertCursor);
    }
    return () => {
      window.removeEventListener('mouseup', revertCursor);
    };
  }, [isClicked]);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    const handleClick = (event) => {
      if (event.target.tagName === 'text') {
        navigator.clipboard.writeText(event.target.textContent);
      }
    };
    document.addEventListener('keydown', handleEscape);
    document.addEventListener('click', handleClick);

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('click', handleClick);
    };
  }, [onClose]);

  function setHeightAndWeightOfSVG(imageSource) {
    const doc = new DOMParser().parseFromString(imageSource, 'image/svg+xml');
    const svg = doc.querySelector('svg');
    svg.setAttribute('height', 'calc(100vh - 72px)');
    svg.setAttribute('width', '100%');
    return new XMLSerializer().serializeToString(doc);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black bg-opacity-85"
        onClick={onClose}></div>
      <div className="z-50 flex flex-col items-center justify-center">
        <div
          id="control-bar"
          className="icon fixed top-0 z-50 flex w-screen justify-center
            bg-black py-4 print:hidden">
          <LightboxButton onClick={() => window.print()} className="mr-4">
            <Printer />
          </LightboxButton>
          <LightboxButton onClick={onClose}>
            <XIcon />
          </LightboxButton>
        </div>
        <div
          className="svg-display mt-2 flex h-full w-full overflow-visible pt-16">
          {imageSource && (
            <TransformWrapper wheel={{ smoothStep: 0.005 }}>
              <TransformComponent>
                <div
                  dangerouslySetInnerHTML={{
                    __html: setHeightAndWeightOfSVG(imageSource)
                  }}
                  className={`select-text overflow-visible
                  ${isClicked ? 'cursor-grabbing' : 'cursor-grab'}`}
                  onMouseDown={() => setIsClicked(true)}></div>
              </TransformComponent>
            </TransformWrapper>
          )}
        </div>
      </div>
    </div>
  );
};
