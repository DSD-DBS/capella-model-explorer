// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ViewsList } from './ViewsList';
import { API_BASE_URL } from '../APIConfig';

export const WiredTemplatesList = () => {
  const [templates, setTemplates] = useState([]);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const response = await fetch(API_BASE_URL + '/views', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        const data = await response.json();
        setTemplates(data);
      } catch (error) {
        setError(error.message);
      }
    };
    fetchTemplates();
  }, []);

  if (error) {
    return (
      <div
        className={
          'rounded bg-red-500 p-4 text-2xl text-white dark:bg-custom-dark-error'
        }>
        {error === 'Failed to fetch'
          ? `Can't connect to the server. Maybe your session was inactive for
          too long? If that's the case, request a new session / restart the app.`
          : error}
      </div>
    );
  }
  return (
    <ViewsList
      templates={templates}
      cardClickCallback={(idx) => navigate(`/${idx}`, { state: { idx: idx } })}
    />
  );
};
