// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import React, { useState, useEffect } from 'react';
import { Button } from './Button';

export const ThemeSwitcher = () => {
  const [theme, setTheme] = useState('light'); // default theme is light

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const switchTheme = (newTheme) => {
    setTheme(newTheme);
  };

  return (
    <div>
      {theme !== 'light' && <Button onClick={() => switchTheme('light')}>Light</Button>}
      {theme !== 'dark' && <Button onClick={() => switchTheme('dark')}>Dark</Button>}
      {theme !== 'auto' && <Button onClick={() => switchTheme('auto')}>Auto</Button>}
    </div>
  );
};
