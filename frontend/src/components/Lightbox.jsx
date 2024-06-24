// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useEffect, useState } from 'react';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import { Printer, XIcon } from 'lucide-react';
import { LightboxButton } from './LightboxButton';

export const Lightbox = ({ onClose, imageSource }) => {
  const [adjustedWidth, setAdjustedWidth] = useState('100%');
  const [adjustedHeight, setAdjustedHeight] = useState('100%');
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

  useEffect(() => {
    if (imageSource) {
      const controlBar = document.getElementById('control-bar');
      const heightMatch = imageSource.match(/height="(\d+)"/);
      const widthMatch = imageSource.match(/width="(\d+)"/);
      const imgHeight = heightMatch ? heightMatch[1] : 'defaultHeight';
      const imgWidth = widthMatch ? widthMatch[1] : 'defaultWidth';

      if (imgHeight + controlBar.clientHeight > window.innerHeight) {
        let widthScale = window.innerWidth / imgWidth;
        let heightScale =
          (window.innerHeight - controlBar.clientHeight - 40) / imgHeight;
        const scalingFactor = Math.min(heightScale, widthScale);

        let adjustedHeight = imgHeight * scalingFactor;
        let adjustedWidth = imgWidth * scalingFactor;
        setAdjustedHeight(adjustedHeight);
        setAdjustedWidth(adjustedWidth);
      }
    }
  }, [imageSource]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black bg-opacity-85"
        onClick={onClose}></div>
      <div className="z-50 flex flex-col items-center justify-center">
        <div
          id="control-bar"
          className={`
            fixed top-0 z-50 flex w-screen justify-center bg-black py-4
             print:hidden
          `}>
          <LightboxButton onClick={() => window.print()} className="mr-4">
            <Printer />
          </LightboxButton>
          <LightboxButton onClick={onClose}>
            <XIcon />
          </LightboxButton>
        </div>
        <div className="mt-2 flex h-full w-full overflow-visible pt-16">
          {imageSource && (
            <TransformWrapper
              options={{ limitToBounds: true, centerContent: true }}>
              <TransformComponent>
                <div
                  dangerouslySetInnerHTML={{ __html: imageSource }}
                  className={`
                    select-text overflow-visible
                    ${isClicked ? 'cursor-grabbing' : 'cursor-grab'}`}
                  onMouseDown={() => setIsClicked(true)}
                  style={{
                    width: adjustedWidth,
                    height: adjustedHeight
                  }}></div>
              </TransformComponent>
            </TransformWrapper>
          )}
        </div>
      </div>
    </div>
  );
};
