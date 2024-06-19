// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useEffect } from 'react';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import { Printer, XIcon } from 'lucide-react';
import { LightboxButton } from './LightboxButton';

export const Lightbox = ({ onClose, imageSource }) => {
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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black bg-opacity-85"
        onClick={onClose}></div>
      <div
        className={`
          absolute left-0 right-0 top-0 z-50 bg-black py-4 print:hidden
        `}>
        <div className="flex justify-center">
          <LightboxButton onClick={() => window.print()} className="mr-4">
            <Printer />
          </LightboxButton>
          <LightboxButton onClick={onClose}>
            <XIcon />
          </LightboxButton>
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          maxWidth: '100%',
          height: 'auto',
          zIndex: 1
        }}>
        {imageSource && (
          <TransformWrapper>
            <TransformComponent>
              <div
                dangerouslySetInnerHTML={{ __html: imageSource }}
                style={{
                  width: '100%',
                  overflow: 'auto',
                  userSelect: 'text'
                }}></div>
            </TransformComponent>
          </TransformWrapper>
        )}
      </div>
    </div>
  );
};
