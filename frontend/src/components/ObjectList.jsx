// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React from 'react';

export const ObjectList = ({objects}) => (
    <div>
        <h1>Object List</h1>
        {/* if objects is an empty list or undefined lets say that no objects found */}
        {objects.length === 0 && <p>No objects found</p>}
        {/* if objects is not an empty list or undefined lets display the list of objects */}
        {objects.length > 0 &&
            <ul>
                {objects.map((object) => (
                    <li key={object.uuid}>{object.name}</li>
                ))}
            </ul>
        }
    </div>
    );
