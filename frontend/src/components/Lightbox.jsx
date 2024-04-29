// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React, { useEffect, useState } from 'react';
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";

export const Lightbox = ({ onClose, imageSource }) => {
    const [isSelecting, setIsSelecting] = useState(false);

    useEffect(() => {
        let isMouseDown = false;

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
        <div className='fixed inset-0 z-50 flex justify-center items-center'>
            <div className='fixed inset-0 bg-black bg-opacity-50' onClick={onClose}></div>
            <div style={{ position: 'absolute', maxWidth: '100%', height: 'auto', zIndex: 1 }}>
                {imageSource &&
                <TransformWrapper>
                    <TransformComponent>
                        <div dangerouslySetInnerHTML={{__html: imageSource}} style={{ width: '100%', overflow: 'auto', userSelect: 'text' }}></div>
                    </TransformComponent>
                </TransformWrapper>}
            </div>
        </div>
    );
}
