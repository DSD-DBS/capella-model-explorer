// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

export const ObjectList = ({ objects }) => (
  <div>
    <h1>Object List</h1>
    {objects.length === 0 && <p>No objects found</p>}
    {objects.length > 0 && (
      <ul>
        {objects.map((object) => (
          <li key={object.uuid}>{object.name}</li>
        ))}
      </ul>
    )}
  </div>
);
