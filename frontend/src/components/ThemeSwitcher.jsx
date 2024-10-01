// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0
import { useState, useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';

export const ThemeSwitcher = () => {
  const systemTheme =
    window.matchMedia &&
    window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';

  const savedTheme = localStorage.getItem('theme') || systemTheme;
  const [theme, setTheme] = useState(savedTheme);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
    } else {
      document.documentElement.classList.add('light');
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <div onClick={toggleTheme} className="header-button">
      {theme === 'dark' ? (
        <Sun
          className="transform text-white transition-transform duration-500
            ease-in-out"
        />
      ) : (
        <Moon
          className="transform text-white transition-transform duration-500
            ease-in-out"
        />
      )}
    </div>
  );
};
