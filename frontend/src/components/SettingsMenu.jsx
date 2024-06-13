// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useState, useEffect, useRef } from 'react';
import { Settings } from 'lucide-react';

export const SettingsMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const toggleMenu = () => setIsOpen(!isOpen);
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="relative" ref={menuRef}>
      <div onClick={toggleMenu} className="header-button">
        <Settings className="h-6 w-6 text-black dark:text-white" />
      </div>
      {isOpen && (
        <div
          className={
            'absolute right-0 mt-2 w-48 divide-y divide-gray-100 ' +
            'rounded-lg border border-gray-200 bg-white shadow-xl'
          }>
          <button
            onClick={handlePrint}
            className={
              'block w-full px-4 py-2 text-left text-sm ' +
              'text-gray-700 hover:bg-blue-100 hover:text-blue-700'
            }>
            Print page
          </button>
          {/* Add more options here as needed, following the same pattern */}
        </div>
      )}
    </div>
  );
};
