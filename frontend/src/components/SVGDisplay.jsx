// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React, {useState} from "react";
import {Lightbox} from "./Lightbox";

export const SVGDisplay = ({content}) => {
    const [showLightbox, setShowLightbox] = useState(false);
    const [lightboxSrc, setLightboxSrc] = useState('');

    const handleSvgClick = () => {
        setShowLightbox(true);
        setLightboxSrc(content);
    }

    return (
        <>
        <div className="relative group" style={{ maxWidth: '100%', height: 'auto' }} onClick={handleSvgClick}>
            <div
                className="absolute rounded inset-0 flex justify-center items-center bg-black bg-opacity-0 group-hover:bg-opacity-50 duration-200 cursor-pointer"
                style={{ pointerEvents: 'none' }}
            >
                <div className="text-transparent group-hover:text-white text-2xl font-bold">Click to enlarge</div>
            </div>
            {content && <div dangerouslySetInnerHTML={{__html: content}}></div>}
        </div>
        {showLightbox && <Lightbox onClose={() => setShowLightbox(false)} imageSource={content} />}
        </>
    );
}
